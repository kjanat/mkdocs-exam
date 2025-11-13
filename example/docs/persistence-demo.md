# LocalStorage Persistence Demo

This page demonstrates the new localStorage persistence feature. All your answers are automatically saved as you type or interact with the exams!

**Try this:**
1. Answer some questions below
2. Refresh the page (F5)
3. Your answers will be restored automatically!

Saved state expires after 24 hours.

---

## Choice Question with Persistence

```yaml
question: "Select all programming languages (try selecting some, then refresh the page):"
answer-correct:
  - "Python"
  - "JavaScript"
  - "Java"
answer:
  - "HTML"
  - "CSS"
points: 10
content: |
  Your selections are automatically saved to localStorage!
```

## Categorization with Persistence

```yaml
type: categorization
question: "Drag items into categories, then refresh the page to see them restored:"
items:
  - "Dog"
  - "Cat"
  - "Apple"
  - "Banana"
  - "Oak"
  - "Pine"
categories:
  - "Animals"
  - "Fruits"
  - "Trees"
correct-mapping:
  0: 0  # Dog -> Animals
  1: 0  # Cat -> Animals
  2: 1  # Apple -> Fruits
  3: 1  # Banana -> Fruits
  4: 2  # Oak -> Trees
  5: 2  # Pine -> Trees
points: 15
content: |
  Drag positions are saved! Try moving items around, then refresh.
```

## Hotspot with Persistence

```yaml
type: hotspot
question: "Click on regions (your clicks are saved across page reloads):"
image: "https://via.placeholder.com/400x300/4CAF50/FFFFFF?text=Click+the+Green+Regions"
regions:
  - x: 10
    y: 10
    width: 25
    height: 25
    correct: true
    label: "Top Left"
  - x: 65
    y: 10
    width: 25
    height: 25
    correct: true
    label: "Top Right"
  - x: 10
    y: 65
    width: 25
    height: 25
    correct: false
    label: "Bottom Left"
  - x: 65
    y: 65
    width: 25
    height: 25
    correct: false
    label: "Bottom Right"
  - x: 37.5
    y: 37.5
    width: 25
    height: 25
    correct: true
    label: "Center"
points: 20
content: |
  Your clicked regions persist across page reloads!
```

## Ordering with Persistence

```yaml
type: ordering
question: "Arrange these in order (your arrangement is saved):"
items:
  - "First"
  - "Second"
  - "Third"
  - "Fourth"
  - "Fifth"
correct-order: [0, 1, 2, 3, 4]
points: 10
content: |
  Drag to reorder, then refresh the page!
```

## Numeric Input with Persistence

```yaml
type: numeric
question: "Enter a number (saved as you type):"
answer-correct:
  - 42
tolerance: 0
unit: ""
points: 5
content: |
  Type a number and refresh - it will still be there!
```

## Code Completion with Persistence

```yaml
type: code-completion
question: "Fill in the blanks (your answers are saved):"
template: |
  def greet(___):
      return "Hello, " ___ name
language: python
blanks:
  - correct: ["name"]
  - correct: ["+"]
points: 10
content: |
  Fill in the blanks, then try refreshing the page!
```

## Text Input with Persistence

```yaml
question: "What is the capital of France?"
answer-correct:
  - "Paris"
content: |
  Type your answer and refresh - it persists!
```

## Essay Question with Persistence

```yaml
type: essay
question: "Write a short essay (saved automatically as you type):"
content: |
  Start typing your essay, refresh the page, and continue where you left off!
```

## With Hints and Time Limit

```yaml
question: "Question with hints and timer (all state is saved):"
answer-correct:
  - "42"
hints:
  - text: "It's the answer to life, the universe, and everything"
    penalty: 20
  - text: "It's between 40 and 45"
    penalty: 30
time-limit: 300
points: 100
content: |
  **Persistence includes:**
  - Your answer
  - Which hints you've revealed
  - Time remaining on the clock

  Try revealing a hint, waiting a bit, then refreshing!
```

## Partial Credit with Persistence

```yaml
question: "Select all correct options (partial credit is calculated):"
answer-correct:
  - value: "Correct 1"
    weight: 0.33
  - value: "Correct 2"
    weight: 0.33
  - value: "Correct 3"
    weight: 0.34
answer:
  - value: "Wrong 1"
    weight: 0.33
  - value: "Wrong 2"
    weight: 0.33
partial-credit: true
points: 30
content: |
  Your selections are saved, including for partial credit questions!
```

---

## How It Works

The localStorage persistence feature:

1. **Auto-saves** your answers as you interact with any exam
2. **Expires** after 24 hours to prevent stale data
3. **Clears** automatically when you submit an exam successfully
4. **Unique per page** - different pages have separate saved states
5. **Privacy-friendly** - all data stays in your browser, nothing sent to servers

### What's Saved?

- ✅ Selected answers (radio/checkbox)
- ✅ Text inputs and textareas
- ✅ Drag-and-drop positions (categorization, ordering)
- ✅ Clicked regions (hotspot)
- ✅ Numeric values
- ✅ Code completion blanks
- ✅ Revealed hints
- ✅ Remaining time on timed questions

### Storage Keys

Data is stored with keys like:
```
mkdocs-exam-state:/docs/persistence-demo/:exam-0
mkdocs-exam-state:/docs/persistence-demo/:exam-1
```

### Clear Saved Data

To manually clear saved data:
1. Open browser DevTools (F12)
2. Go to Application > Local Storage
3. Find keys starting with `mkdocs-exam-state:`
4. Delete them

Or just submit the exam - it clears automatically!
