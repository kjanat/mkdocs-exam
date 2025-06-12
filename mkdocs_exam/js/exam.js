document.querySelectorAll('.exam').forEach((exam) => {
  const form = exam.querySelector('form')
  const fieldset = form.querySelector('fieldset')
  const type = exam.dataset.type || 'choice'
  form.addEventListener('submit', (event) => {
    event.preventDefault()
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
    } else {
      const inputs = fieldset.querySelectorAll('input[type="text"][name="answer"], textarea[name="answer"]')
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

    const section = exam.querySelector('section')
    if (isCorrect) {
      section.classList.remove('hidden')
    } else {
      section.classList.add('hidden')
    }
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
