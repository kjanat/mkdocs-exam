// ==================== LocalStorage Persistence ====================

const STORAGE_PREFIX = 'mkdocs-exam-state:'
const EXPIRY_HOURS = 24

/**
 * Generate unique storage key for an exam
 */
function getStorageKey(examIndex) {
  const path = window.location.pathname
  return `${STORAGE_PREFIX}${path}:exam-${examIndex}`
}

/**
 * Save exam state to localStorage
 */
function saveExamState(examIndex, state) {
  try {
    const data = {
      timestamp: Date.now(),
      state: state
    }
    localStorage.setItem(getStorageKey(examIndex), JSON.stringify(data))
  } catch (e) {
    console.warn('Failed to save exam state:', e)
  }
}

/**
 * Load exam state from localStorage
 * Returns null if expired or not found
 */
function loadExamState(examIndex) {
  try {
    const key = getStorageKey(examIndex)
    const json = localStorage.getItem(key)
    if (!json) return null

    const data = JSON.parse(json)
    const age = Date.now() - data.timestamp
    const maxAge = EXPIRY_HOURS * 60 * 60 * 1000

    if (age > maxAge) {
      localStorage.removeItem(key)
      return null
    }

    return data.state
  } catch (e) {
    console.warn('Failed to load exam state:', e)
    return null
  }
}

/**
 * Clear exam state from localStorage
 */
function clearExamState(examIndex) {
  try {
    localStorage.removeItem(getStorageKey(examIndex))
  } catch (e) {
    console.warn('Failed to clear exam state:', e)
  }
}

// ==================== Initialize Exams ====================

// Initialize all exams on the page
document.querySelectorAll('.exam').forEach((exam, examIndex) => {
  const form = exam.querySelector('form')
  const fieldset = form.querySelector('fieldset')
  const type = exam.dataset.type || 'choice'
  const points = parseInt(exam.dataset.points) || 1
  const timeLimit = parseInt(exam.dataset.timeLimit)

  let currentScore = points
  let timerInterval = null
  let hintsUsed = 0

  // Load saved state
  const savedState = loadExamState(examIndex)

  // Initialize hints
  const hintsContainer = exam.querySelector('.exam-hints')
  if (hintsContainer) {
    hintsContainer.classList.remove('hidden')
    const hintButtons = hintsContainer.querySelectorAll('.hint-button')

    // Restore hint state
    if (savedState && savedState.hintsUsed) {
      savedState.hintsUsed.forEach((hintIndex) => {
        const btn = hintButtons[hintIndex]
        if (btn) {
          const hint = btn.parentElement
          const hintText = hint.querySelector('.hint-text')
          const penalty = parseInt(hint.dataset.penalty) || 0

          hintText.classList.remove('hidden')
          currentScore = Math.max(0, currentScore - (points * penalty / 100))
          hintsUsed++
          btn.disabled = true
          btn.textContent = `Hint ${hintIndex + 1} (used)`
        }
      })
    }

    hintButtons.forEach((btn, index) => {
      btn.addEventListener('click', () => {
        const hint = btn.parentElement
        const hintText = hint.querySelector('.hint-text')
        const penalty = parseInt(hint.dataset.penalty) || 0

        if (hintText.classList.contains('hidden')) {
          hintText.classList.remove('hidden')
          currentScore = Math.max(0, currentScore - (points * penalty / 100))
          hintsUsed++
          btn.disabled = true
          btn.textContent = `Hint ${index + 1} (used)`

          // Save hint usage
          saveExamState(examIndex, getCurrentState())
        }
      })
    })
  }

  // Initialize time limit
  if (timeLimit) {
    // Restore time remaining or use full time limit
    let timeRemaining = (savedState && savedState.timeRemaining) ? savedState.timeRemaining : timeLimit
    const timerDiv = document.createElement('div')
    timerDiv.className = 'exam-timer'
    timerDiv.textContent = `Time: ${timeRemaining}s`
    exam.insertBefore(timerDiv, form)

    timerInterval = setInterval(() => {
      timeRemaining--
      timerDiv.textContent = `Time: ${timeRemaining}s`
      if (timeRemaining <= 10) {
        timerDiv.classList.add('warning')
      }
      if (timeRemaining <= 0) {
        clearInterval(timerInterval)
        form.querySelector('button[type="submit"]').click()
        form.querySelector('button[type="submit"]').disabled = true
      }

      // Save time remaining every second
      saveExamState(examIndex, getCurrentState())
    }, 1000)
  }

  // Function to capture current exam state
  function getCurrentState() {
    const state = {
      type: type,
      hintsUsed: [],
      timeRemaining: null
    }

    // Capture hint state
    const hintContainer = exam.querySelector('.exam-hints')
    if (hintContainer) {
      const hintButtons = hintContainer.querySelectorAll('.hint-button')
      hintButtons.forEach((btn, index) => {
        if (btn.disabled) {
          state.hintsUsed.push(index)
        }
      })
    }

    // Capture time remaining (from closure)
    if (timerInterval) {
      const timerDiv = exam.querySelector('.exam-timer')
      if (timerDiv) {
        const match = timerDiv.textContent.match(/(\d+)s/)
        if (match) {
          state.timeRemaining = parseInt(match[1])
        }
      }
    }

    // Capture type-specific state
    if (type === 'choice' || type === 'truefalse') {
      const selected = form.querySelectorAll('input[name="answer"]:checked')
      state.selectedAnswers = Array.from(selected).map(input => input.value)
    } else if (type === 'categorization') {
      state.categorizationState = {}
      const container = fieldset.querySelector('.categorization-container')
      if (container) {
        const items = container.querySelectorAll('.categorization-item')
        items.forEach((item) => {
          const itemIndex = item.dataset.itemIndex
          const currentParent = item.closest('.categorization-category')
          const categoryIndex = currentParent ? currentParent.dataset.categoryIndex : null
          state.categorizationState[itemIndex] = categoryIndex
        })
      }
    } else if (type === 'hotspot') {
      const clickedRegions = fieldset.querySelectorAll('.hotspot-region.clicked')
      state.hotspotClicked = Array.from(clickedRegions).map(r => r.dataset.regionIndex)
    } else if (type === 'ordering') {
      const container = fieldset.querySelector('.ordering-container')
      if (container) {
        const items = Array.from(container.querySelectorAll('.ordering-item'))
        state.orderingOrder = items.map(item => item.dataset.index)
      }
    } else if (type === 'numeric') {
      const input = fieldset.querySelector('input[type="number"]')
      if (input) {
        state.numericValue = input.value
      }
    } else if (type === 'code-completion') {
      const inputs = fieldset.querySelectorAll('input.code-blank')
      state.codeBlankValues = Array.from(inputs).map(input => input.value)
    } else if (type === 'matching') {
      const selects = fieldset.querySelectorAll('select[name="answer"]')
      state.matchingSelections = Array.from(selects).map(select => select.value)
    } else {
      // short-answer, fill, essay
      const inputs = fieldset.querySelectorAll('input[type="text"][name="answer"], textarea[name="answer"]')
      state.textInputValues = Array.from(inputs).map(input => input.value)
    }

    return state
  }

  // Restore saved state for all exam types
  if (savedState) {
    // Restore choice/truefalse answers
    if (type === 'choice' || type === 'truefalse') {
      if (savedState.selectedAnswers) {
        savedState.selectedAnswers.forEach((value) => {
          const input = form.querySelector(`input[name="answer"][value="${value}"]`)
          if (input) {
            input.checked = true
          }
        })
      }
    }
    // Restore categorization
    else if (type === 'categorization' && savedState.categorizationState) {
      const container = fieldset.querySelector('.categorization-container')
      if (container) {
        Object.keys(savedState.categorizationState).forEach((itemIndex) => {
          const categoryIndex = savedState.categorizationState[itemIndex]
          const item = container.querySelector(`.categorization-item[data-item-index="${itemIndex}"]`)
          const category = container.querySelector(`.categorization-category[data-category-index="${categoryIndex}"]`)
          if (item && category) {
            const dropZone = category.querySelector('.category-drop-zone')
            if (dropZone) {
              dropZone.appendChild(item)
            }
          }
        })
      }
    }
    // Restore hotspot
    else if (type === 'hotspot' && savedState.hotspotClicked) {
      savedState.hotspotClicked.forEach((regionIndex) => {
        const region = fieldset.querySelector(`.hotspot-region[data-region-index="${regionIndex}"]`)
        if (region) {
          region.classList.add('clicked')
          if (region.hasAttribute('correct')) {
            region.classList.add('correct')
          } else {
            region.classList.add('wrong')
          }
        }
      })
    }
    // Restore ordering
    else if (type === 'ordering' && savedState.orderingOrder) {
      const container = fieldset.querySelector('.ordering-container')
      if (container) {
        const itemsMap = {}
        container.querySelectorAll('.ordering-item').forEach((item) => {
          itemsMap[item.dataset.index] = item
        })
        container.innerHTML = ''
        savedState.orderingOrder.forEach((index) => {
          if (itemsMap[index]) {
            container.appendChild(itemsMap[index])
          }
        })
      }
    }
    // Restore numeric
    else if (type === 'numeric' && savedState.numericValue !== undefined) {
      const input = fieldset.querySelector('input[type="number"]')
      if (input) {
        input.value = savedState.numericValue
      }
    }
    // Restore code-completion
    else if (type === 'code-completion' && savedState.codeBlankValues) {
      const inputs = fieldset.querySelectorAll('input.code-blank')
      savedState.codeBlankValues.forEach((value, index) => {
        if (inputs[index]) {
          inputs[index].value = value
        }
      })
    }
    // Restore matching
    else if (type === 'matching' && savedState.matchingSelections) {
      const selects = fieldset.querySelectorAll('select[name="answer"]')
      savedState.matchingSelections.forEach((value, index) => {
        if (selects[index]) {
          selects[index].value = value
        }
      })
    }
    // Restore text inputs
    else if (savedState.textInputValues) {
      const inputs = fieldset.querySelectorAll('input[type="text"][name="answer"], textarea[name="answer"]')
      savedState.textInputValues.forEach((value, index) => {
        if (inputs[index]) {
          inputs[index].value = value
        }
      })
    }
  }

  // Store save function on exam element for use in drag handlers
  exam._saveState = () => saveExamState(examIndex, getCurrentState())

  // Add event listeners to save state on input changes
  form.querySelectorAll('input, textarea, select').forEach((input) => {
    input.addEventListener('change', () => {
      exam._saveState()
    })
    input.addEventListener('input', () => {
      exam._saveState()
    })
  })

  // Handle form submission
  form.addEventListener('submit', (event) => {
    event.preventDefault()

    if (timerInterval) {
      clearInterval(timerInterval)
    }

    let isCorrect = false

    if (type === 'choice' || type === 'truefalse') {
      const selected = form.querySelectorAll('input[name="answer"]:checked')
      const correct = fieldset.querySelectorAll('input[name="answer"][correct]')
      isCorrect = selected.length === correct.length
      for (let i = 0; i < selected.length; i++) {
        if (!selected[i].hasAttribute('correct')) {
          isCorrect = false
          break
        }
      }
      markFields(selected, isCorrect)
      // Show answer feedback
      showAnswerFeedback(selected)
    } else if (type === 'matching') {
      const selects = fieldset.querySelectorAll('select[name="answer"]')
      isCorrect = true
      selects.forEach((sel) => {
        const expected = sel.getAttribute('correct')
        const ok = sel.value === expected
        if (!ok) {
          isCorrect = false
        }
        sel.classList.add(ok ? 'correct' : 'wrong')
      })
    } else if (type === 'numeric') {
      const input = fieldset.querySelector('input[type="number"]')
      const userValue = parseFloat(input.value)
      const correctValue = parseFloat(input.dataset.correct)
      const tolerance = parseFloat(input.dataset.tolerance) || 0.01
      isCorrect = Math.abs(userValue - correctValue) <= tolerance
      input.classList.add(isCorrect ? 'correct' : 'wrong')
    } else if (type === 'code-completion') {
      const inputs = fieldset.querySelectorAll('input.code-blank')
      isCorrect = true
      inputs.forEach((input) => {
        const expected = (input.getAttribute('correct') || '').split('|')
        const val = input.value.trim()
        const ok = expected.map(e => e.trim()).includes(val)
        if (!ok) {
          isCorrect = false
        }
        input.classList.add(ok ? 'correct' : 'wrong')
      })
    } else if (type === 'ordering') {
      const container = fieldset.querySelector('.ordering-container')
      const items = Array.from(container.querySelectorAll('.ordering-item'))
      const userOrder = items.map(item => parseInt(item.dataset.index))
      const correctOrder = container.dataset.correctOrder.split(',').map(x => parseInt(x))
      isCorrect = JSON.stringify(userOrder) === JSON.stringify(correctOrder)
      container.classList.add(isCorrect ? 'correct' : 'wrong')
    } else if (type === 'categorization') {
      const container = fieldset.querySelector('.categorization-container')
      const items = container.querySelectorAll('.categorization-item')
      isCorrect = true
      items.forEach((item) => {
        const correctCat = item.dataset.correctCategory
        const currentParent = item.closest('.categorization-category')
        const currentCat = currentParent ? currentParent.dataset.categoryIndex : null
        if (correctCat !== currentCat) {
          isCorrect = false
        }
      })
      container.classList.add(isCorrect ? 'correct' : 'wrong')
    } else if (type === 'hotspot') {
      const clickedRegions = fieldset.querySelectorAll('.hotspot-region.clicked')
      const correctRegions = fieldset.querySelectorAll('.hotspot-region[correct]')
      isCorrect = clickedRegions.length === correctRegions.length
      correctRegions.forEach((region) => {
        if (!region.classList.contains('clicked')) {
          isCorrect = false
        }
      })
      clickedRegions.forEach((region) => {
        if (!region.hasAttribute('correct')) {
          isCorrect = false
        }
      })
    } else {
      // short-answer, fill, essay
      const inputs = fieldset.querySelectorAll('input[type="text"][name="answer"], textarea[name="answer"]')
      resetFieldset(fieldset)
      isCorrect = true
      for (let i = 0; i < inputs.length; i++) {
        const expected = (inputs[i].getAttribute('correct') || '').split('|')
        const val = inputs[i].value.trim().toLowerCase()
        const ok = expected.map((e) => e.trim().toLowerCase()).includes(val)
        if (!ok) {
          isCorrect = false
        }
        inputs[i].classList.add(ok ? 'correct' : 'wrong')
      }
    }

    // Show/hide content based on correctness
    const section = exam.querySelector('section.content')
    if (isCorrect) {
      section.classList.remove('hidden')
    } else {
      section.classList.add('hidden')
    }

    // Show explanation based on setting
    const explanation = exam.querySelector('.exam-explanation')
    if (explanation) {
      const showWhen = explanation.dataset.show || 'on-correct'
      if (showWhen === 'always' ||
          (showWhen === 'on-correct' && isCorrect) ||
          (showWhen === 'on-wrong' && !isCorrect)) {
        explanation.classList.remove('hidden')
      }
    }

    // Show score
    const scoreDiv = document.createElement('div')
    scoreDiv.className = 'exam-score'
    scoreDiv.textContent = isCorrect
      ? `✓ Correct! Score: ${currentScore}/${points} points`
      : '✗ Incorrect. Try again!'

    const existingScore = exam.querySelector('.exam-score')
    if (existingScore) {
      existingScore.replaceWith(scoreDiv)
    } else {
      form.appendChild(scoreDiv)
    }

    // Disable submit button
    form.querySelector('button[type="submit"]').disabled = true

    // Clear saved state on successful submit
    clearExamState(examIndex)
  })
})

function markFields (selected, correct) {
  resetFieldset(selected[0].closest('fieldset'))
  for (let i = 0; i < selected.length; i++) {
    if (!selected[i].hasAttribute('correct')) {
      selected[i].parentElement.classList.add('wrong')
    } else {
      selected[i].parentElement.classList.add('correct')
    }
  }
}

function resetFieldset (fieldset) {
  const fieldsetChildren = fieldset.children
  for (let i = 0; i < fieldsetChildren.length; i++) {
    fieldsetChildren[i].classList.remove('wrong')
    fieldsetChildren[i].classList.remove('correct')
    const input = fieldsetChildren[i].querySelector('input, textarea, select')
    if (input) {
      input.classList.remove('wrong')
      input.classList.remove('correct')
    }
  }
}

function showAnswerFeedback (selectedInputs) {
  selectedInputs.forEach((input) => {
    const feedback = input.dataset.feedback
    if (feedback) {
      const feedbackDiv = document.createElement('div')
      feedbackDiv.className = 'answer-feedback'
      feedbackDiv.textContent = feedback
      input.parentElement.appendChild(feedbackDiv)
    }
  })
}

// Add drag-and-drop support for ordering questions
document.querySelectorAll('.ordering-container').forEach((container) => {
  let draggedItem = null

  // Find exam index for state persistence
  const examElement = container.closest('.exam')
  const allExams = Array.from(document.querySelectorAll('.exam'))
  const examIndex = allExams.indexOf(examElement)

  container.querySelectorAll('.ordering-item').forEach((item) => {
    item.draggable = true

    item.addEventListener('dragstart', (e) => {
      draggedItem = item
      item.classList.add('dragging')
    })

    item.addEventListener('dragend', (e) => {
      item.classList.remove('dragging')
      // Save state after drag ends
      if (examElement && examElement._saveState) {
        examElement._saveState()
      }
    })

    item.addEventListener('dragover', (e) => {
      e.preventDefault()
    })

    item.addEventListener('drop', (e) => {
      e.preventDefault()
      if (draggedItem !== item) {
        const allItems = Array.from(container.children)
        const draggedIndex = allItems.indexOf(draggedItem)
        const targetIndex = allItems.indexOf(item)

        if (draggedIndex < targetIndex) {
          item.parentNode.insertBefore(draggedItem, item.nextSibling)
        } else {
          item.parentNode.insertBefore(draggedItem, item)
        }
      }
    })
  })
})

// Add drag-and-drop support for categorization questions
document.querySelectorAll('.categorization-container').forEach((container) => {
  let draggedItem = null

  // Find exam element for state persistence
  const examElement = container.closest('.exam')

  container.querySelectorAll('.categorization-item').forEach((item) => {
    item.draggable = true

    item.addEventListener('dragstart', (e) => {
      draggedItem = item
      item.classList.add('dragging')
    })

    item.addEventListener('dragend', (e) => {
      item.classList.remove('dragging')
      // Save state after drag ends
      if (examElement && examElement._saveState) {
        examElement._saveState()
      }
    })
  })

  container.querySelectorAll('.category-drop-zone').forEach((dropZone) => {
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault()
      dropZone.classList.add('drag-over')
    })

    dropZone.addEventListener('dragleave', (e) => {
      dropZone.classList.remove('drag-over')
    })

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault()
      dropZone.classList.remove('drag-over')
      if (draggedItem) {
        dropZone.appendChild(draggedItem)
        // Save state after drop
        if (examElement && examElement._saveState) {
          examElement._saveState()
        }
      }
    })
  })
})

// Add click handling for hotspot questions
document.querySelectorAll('.hotspot-container').forEach((container) => {
  // Find exam element for state persistence
  const examElement = container.closest('.exam')

  container.querySelectorAll('.hotspot-region').forEach((region) => {
    region.addEventListener('click', (e) => {
      region.classList.toggle('clicked')
      if (region.classList.contains('clicked')) {
        if (region.hasAttribute('correct')) {
          region.classList.add('correct')
        } else {
          region.classList.add('wrong')
        }
      } else {
        region.classList.remove('correct', 'wrong')
      }

      // Save state after click
      if (examElement && examElement._saveState) {
        examElement._saveState()
      }
    })
  })
})

// Add partial credit calculation for choice questions
document.querySelectorAll('.exam[data-type="choice"]').forEach((exam) => {
  const partialCredit = exam.dataset.partialCredit === 'true'
  if (!partialCredit) return

  const form = exam.querySelector('form')
  if (!form) return

  const originalSubmitHandler = form.onsubmit
  form.addEventListener('submit', (event) => {
    const selected = form.querySelectorAll('input[name="answer"]:checked')
    const correct = form.querySelectorAll('input[name="answer"][correct]')

    let earnedPoints = 0
    let totalPoints = 0

    // Calculate points based on weights
    correct.forEach((input) => {
      const weight = parseFloat(input.dataset.weight) || 1.0
      totalPoints += weight
    })

    selected.forEach((input) => {
      const weight = parseFloat(input.dataset.weight) || 1.0
      if (input.hasAttribute('correct')) {
        earnedPoints += weight
      } else {
        earnedPoints -= weight // Penalty for incorrect selections
      }
    })

    // Normalize to 0-100%
    const percentage = Math.max(0, Math.min(100, (earnedPoints / totalPoints) * 100))

    // Show partial credit score
    const scoreDiv = document.createElement('div')
    scoreDiv.className = 'partial-credit-score'
    if (percentage === 100) {
      scoreDiv.className += ' full'
    } else if (percentage >= 50) {
      scoreDiv.className += ' partial'
    } else {
      scoreDiv.className += ' zero'
    }
    scoreDiv.textContent = `Score: ${percentage.toFixed(0)}%`
    form.appendChild(scoreDiv)
  }, { once: true })
})
