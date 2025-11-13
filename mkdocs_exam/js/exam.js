// Initialize all exams on the page
document.querySelectorAll('.exam').forEach((exam) => {
  const form = exam.querySelector('form')
  const fieldset = form.querySelector('fieldset')
  const type = exam.dataset.type || 'choice'
  const points = parseInt(exam.dataset.points) || 1
  const timeLimit = parseInt(exam.dataset.timeLimit)

  let currentScore = points
  let timerInterval = null
  let hintsUsed = 0

  // Initialize hints
  const hintsContainer = exam.querySelector('.exam-hints')
  if (hintsContainer) {
    hintsContainer.classList.remove('hidden')
    const hintButtons = hintsContainer.querySelectorAll('.hint-button')
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
        }
      })
    })
  }

  // Initialize time limit
  if (timeLimit) {
    let timeRemaining = timeLimit
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
    }, 1000)
  }

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

  container.querySelectorAll('.ordering-item').forEach((item) => {
    item.draggable = true

    item.addEventListener('dragstart', (e) => {
      draggedItem = item
      item.classList.add('dragging')
    })

    item.addEventListener('dragend', (e) => {
      item.classList.remove('dragging')
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

  container.querySelectorAll('.categorization-item').forEach((item) => {
    item.draggable = true

    item.addEventListener('dragstart', (e) => {
      draggedItem = item
      item.classList.add('dragging')
    })

    item.addEventListener('dragend', (e) => {
      item.classList.remove('dragging')
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
      }
    })
  })
})

// Add click handling for hotspot questions
document.querySelectorAll('.hotspot-container').forEach((container) => {
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
