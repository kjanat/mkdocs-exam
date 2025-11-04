'use strict'

/**
 * MkDocs Exam Plugin - Client-side exam validation and feedback
 * @module mkdocs-exam
 */

/**
 * Initialize all exam blocks on the page
 */
document.querySelectorAll('.exam').forEach((exam) => {
  const form = exam.querySelector('form')
  const fieldset = form.querySelector('fieldset')
  const type = exam.dataset.type || 'choice'
  const scoreDisplay = exam.querySelector('.exam-score')
  const resetButton = exam.querySelector('.reset-button')

  /**
   * Handle form submission
   * @param {Event} event - Form submit event
   */
  form.addEventListener('submit', (event) => {
    event.preventDefault()

    const result = validateExam(exam, form, fieldset, type)

    // Update score display if present
    if (scoreDisplay) {
      if (result.isCorrect) {
        scoreDisplay.textContent = '✓ Correct!'
        scoreDisplay.className = 'exam-score correct'
        scoreDisplay.setAttribute('aria-label', 'Answer is correct')
      } else {
        const score = `${result.correctCount} / ${result.totalCount}`
        scoreDisplay.textContent = `✗ Score: ${score}`
        scoreDisplay.className = 'exam-score wrong'
        scoreDisplay.setAttribute('aria-label', `Score: ${score} out of ${result.totalCount}`)
      }
      scoreDisplay.classList.remove('hidden')
    }

    // Show/hide content section based on correctness
    const section = exam.querySelector('section')
    if (result.isCorrect) {
      section.classList.remove('hidden')
      section.setAttribute('aria-label', 'Additional content revealed')
    } else {
      section.classList.add('hidden')
    }

    // Announce result to screen readers
    announceResult(result.isCorrect)
  })

  /**
   * Handle reset button click
   */
  if (resetButton) {
    resetButton.addEventListener('click', () => {
      resetExam(exam, form, fieldset, type, scoreDisplay)
    })
  }
})

/**
 * Validate exam answers based on question type
 * @param {HTMLElement} exam - The exam container
 * @param {HTMLFormElement} form - The form element
 * @param {HTMLFieldSetElement} fieldset - The fieldset element
 * @param {string} type - Question type (choice, matching, etc.)
 * @returns {{isCorrect: boolean, correctCount: number, totalCount: number}} Validation result
 */
function validateExam (exam, form, fieldset, type) {
  let isCorrect = false
  let correctCount = 0
  let totalCount = 0

  if (type === 'choice' || type === 'truefalse') {
    const selected = form.querySelectorAll('input[name="answer"]:checked')
    const correct = fieldset.querySelectorAll('input[name="answer"][correct]')

    totalCount = correct.length
    isCorrect = selected.length === correct.length

    for (let i = 0; i < selected.length; i++) {
      if (!selected[i].hasAttribute('correct')) {
        isCorrect = false
        break
      }
    }

    if (isCorrect) {
      correctCount = totalCount
    }

    markFields(selected, isCorrect)
  } else if (type === 'matching') {
    const selects = fieldset.querySelectorAll('select[name="answer"]')
    isCorrect = true
    totalCount = selects.length

    selects.forEach((sel) => {
      const expected = sel.getAttribute('correct')
      const ok = sel.value === expected

      if (ok) {
        correctCount++
      } else {
        isCorrect = false
      }

      sel.classList.add(ok ? 'correct' : 'wrong')
      sel.setAttribute('aria-invalid', ok ? 'false' : 'true')
    })
  } else {
    // Text inputs (short-answer, fill, essay)
    const inputs = fieldset.querySelectorAll(
      'input[type="text"][name="answer"], textarea[name="answer"]'
    )
    resetFieldset(fieldset)
    isCorrect = true
    totalCount = inputs.length

    for (let i = 0; i < inputs.length; i++) {
      const expected = (inputs[i].getAttribute('correct') || '').split('|')
      const val = inputs[i].value.trim().toLowerCase()
      const ok = expected.map((e) => e.trim().toLowerCase()).includes(val)

      if (ok) {
        correctCount++
      } else {
        isCorrect = false
      }

      inputs[i].classList.add(ok ? 'correct' : 'wrong')
      inputs[i].setAttribute('aria-invalid', ok ? 'false' : 'true')
    }
  }

  return { isCorrect, correctCount, totalCount }
}

/**
 * Mark selected fields as correct or wrong
 * @param {NodeList} selected - Selected input elements
 * @param {boolean} correct - Whether answers are correct
 */
function markFields (selected, correct) {
  resetFieldset(selected[0].closest('fieldset'))

  for (let i = 0; i < selected.length; i++) {
    const cssClass = selected[i].hasAttribute('correct') ? 'correct' : 'wrong'
    selected[i].parentElement.classList.add(cssClass)
    selected[i].setAttribute('aria-invalid', cssClass === 'wrong' ? 'true' : 'false')
  }
}

/**
 * Reset fieldset by removing validation classes
 * @param {HTMLFieldSetElement} fieldset - The fieldset to reset
 */
function resetFieldset (fieldset) {
  const fieldsetChildren = fieldset.children

  for (let i = 0; i < fieldsetChildren.length; i++) {
    fieldsetChildren[i].classList.remove('wrong', 'correct')

    const input = fieldsetChildren[i].querySelector('input, textarea, select')
    if (input) {
      input.classList.remove('wrong', 'correct')
      input.removeAttribute('aria-invalid')
    }
  }
}

/**
 * Reset exam to initial state
 * @param {HTMLElement} exam - The exam container
 * @param {HTMLFormElement} form - The form element
 * @param {HTMLFieldSetElement} fieldset - The fieldset element
 * @param {string} type - Question type
 * @param {HTMLElement|null} scoreDisplay - Score display element
 */
function resetExam (exam, form, fieldset, type, scoreDisplay) {
  // Reset form
  form.reset()

  // Clear validation classes
  resetFieldset(fieldset)

  // Hide score
  if (scoreDisplay) {
    scoreDisplay.classList.add('hidden')
  }

  // Hide content section
  const section = exam.querySelector('section')
  if (section) {
    section.classList.add('hidden')
  }

  // Focus first input for accessibility
  const firstInput = fieldset.querySelector('input, textarea, select')
  if (firstInput) {
    firstInput.focus()
  }

  // Announce reset to screen readers
  announceMessage('Exam reset. Please try again.')
}

/**
 * Announce result to screen readers
 * @param {boolean} isCorrect - Whether the answer is correct
 */
function announceResult (isCorrect) {
  const message = isCorrect ? 'Your answer is correct!' : 'Your answer is incorrect. Please try again.'
  announceMessage(message)
}

/**
 * Announce message to screen readers via ARIA live region
 * @param {string} message - Message to announce
 */
function announceMessage (message) {
  // Create temporary live region if it doesn't exist
  let liveRegion = document.getElementById('exam-announcements')
  if (!liveRegion) {
    liveRegion = document.createElement('div')
    liveRegion.id = 'exam-announcements'
    liveRegion.className = 'sr-only'
    liveRegion.setAttribute('role', 'status')
    liveRegion.setAttribute('aria-live', 'polite')
    liveRegion.setAttribute('aria-atomic', 'true')
    document.body.appendChild(liveRegion)
  }

  // Update message
  liveRegion.textContent = message

  // Clear after a delay
  setTimeout(() => {
    liveRegion.textContent = ''
  }, 1000)
}
