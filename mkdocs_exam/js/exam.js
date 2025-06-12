document.querySelectorAll('.exam').forEach((exam) => {
  const form = exam.querySelector('form')
  const fieldset = form.querySelector('fieldset')
  form.addEventListener('submit', (event) => {
    event.preventDefault()
    const selectedAnswers = form.querySelectorAll(
      'input[name="answer"]:checked'
    )
    const correctAnswers = fieldset.querySelectorAll(
      'input[name="answer"][correct]'
    )
    // Check if all correct answers are selected
    let isCorrect = selectedAnswers.length === correctAnswers.length
    for (let i = 0; i < selectedAnswers.length; i++) {
      if (!selectedAnswers[i].hasAttribute('correct')) {
        isCorrect = false
        break
      }
    }
    const section = exam.querySelector('section')
    if (isCorrect) {
      section.classList.remove('hidden')
      resetFieldset(fieldset)
      // Mark all fields with colors
      const allAnswers = fieldset.querySelectorAll('input[name="answer"]')
      for (let i = 0; i < allAnswers.length; i++) {
        if (allAnswers[i].hasAttribute('correct')) {
          allAnswers[i].parentElement.classList.add('correct')
        } else {
          allAnswers[i].parentElement.classList.add('wrong')
        }
      }
    } else {
      section.classList.add('hidden')
      resetFieldset(fieldset)
      // Mark wrong fields with colors
      for (let i = 0; i < selectedAnswers.length; i++) {
        if (!selectedAnswers[i].hasAttribute('correct')) {
          selectedAnswers[i].parentElement.classList.add('wrong')
        } else {
          selectedAnswers[i].parentElement.classList.add('correct')
        }
      }
    }
  })
})

// Drag-and-drop exams
document.querySelectorAll('.drag-exam').forEach((exam) => {
  const form = exam.querySelector('form')
  let dragged = null
  exam.querySelectorAll('.drag-item').forEach((item) => {
    item.addEventListener('dragstart', () => {
      dragged = item
    })
  })
  exam.querySelectorAll('.drop-zone').forEach((zone) => {
    zone.addEventListener('dragover', (e) => {
      e.preventDefault()
    })
    zone.addEventListener('drop', (e) => {
      e.preventDefault()
      if (dragged) {
        zone.innerHTML = ''
        zone.appendChild(dragged)
        dragged = null
      }
    })
  })

  form.addEventListener('submit', (event) => {
    event.preventDefault()
    let isCorrect = true
    exam.querySelectorAll('.drop-zone').forEach((zone) => {
      zone.classList.remove('wrong')
      zone.classList.remove('correct')
      const item = zone.querySelector('.drag-item')
      if (!item || item.dataset.id !== zone.dataset.target) {
        isCorrect = false
        zone.classList.add('wrong')
      } else {
        zone.classList.add('correct')
      }
    })
    const section = exam.querySelector('section')
    if (isCorrect) {
      section.classList.remove('hidden')
    } else {
      section.classList.add('hidden')
    }
  })
})

function resetFieldset (fieldset) {
  const fieldsetChildren = fieldset.children
  for (let i = 0; i < fieldsetChildren.length; i++) {
    fieldsetChildren[i].classList.remove('wrong')
    fieldsetChildren[i].classList.remove('correct')
  }
}
