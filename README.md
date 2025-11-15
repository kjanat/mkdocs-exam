# MkDocs Exam Plugin

## Installation

This plugin hasn't landed on PyPI yet. Clone the repository and install it in editable mode with **uv**:

```bash
git clone https://github.com/kjanat/mkdocs-exam.git
cd mkdocs-exam
uv pip install -e .
```

## Create your first exam

Add the following to your `mkdocs.yml`:

```yaml
plugins:
  - mkdocs-exam
```

### Single choice

Now you can create your first exam directly in markdown:

````markdown
```yaml
question: "Are you ready?"
answer-correct:
  - "Yes!"
answer:
  - "No!"
  - "Maybe!"
content: |
  ## Provide some additional content
```
````

> [!NOTE]
> The questions, answers, and content support full **Markdown** syntax

> [!TIP]
> You can use either `` ```yaml `` or `` ```exam `` as the codeblock language

### Multiple choice

You can also create a multiple choice exam, by providing multiple answers as correct.

````markdown
```yaml
question: "Are you ready?"
answer-correct:
  - "Yes!"
  - "Maybe!"
answer:
  - "No!"
content: |
  ## Provide some additional content
```
````

### Short answer

Provide the expected answer as `answer-correct` and set the type to `short-answer`:

````markdown
```yaml
type: short-answer
question: "What color is the sky?"
answer-correct:
  - "blue"
content: |
  The sky often appears blue due to Rayleigh scattering.
```
````

### Fill in the blank

Use three underscores (`___`) as placeholder in your question and provide the correct answer.

````markdown
```yaml
type: fill
question: "2 + 2 = ___"
answer-correct:
  - "4"
content: |
  A simple addition problem.
```
````

### True/false

This type can be used for simple statements that are either true or false. If no
answers are provided, the plugin will automatically use _True_ and _False_.

````markdown
```yaml
type: truefalse
question: "The Earth orbits the Sun."
answer-correct:
  - "True"
content: |
  This is obviously true.
```
````

### Essay

For longer open questions the `essay` type renders a multiline textarea.

````markdown
```yaml
type: essay
question: "Explain the theory of relativity in one paragraph."
answer-correct:
  - "It deals with space and time."
content: |
  Provide an explanation.
```
````

### Matching

Provide pairs separated by a pipe (`|`). Each left item will be shown with a
drop-down to select the corresponding right item.

````markdown
```yaml
type: matching
question: "Match the capitals to countries"
answer:
  - "Paris | France"
  - "Rome | Italy"
  - "Madrid | Spain"
content: |
  Capitals and their countries.
```
````

## New Exam Types

### Numeric

Accept numeric answers within a tolerance range:

````markdown
```yaml
type: numeric
question: "What is the value of π (pi) to 2 decimal places?"
answer-correct:
  - 3.14
tolerance: 0.01
unit: ""
points: 5
content: |
  π (pi) is approximately 3.14159...
```
````

### Code Completion

Fill-in-the-blank for code with syntax highlighting:

````markdown
```yaml
type: code-completion
question: "Complete the Python function:"
template: |
  def add(a, b):
      return a ___ b
language: python
blanks:
  - correct: ["+"]
points: 10
content: |
  The addition operator in Python is +
```
````

### Ordering

Drag-and-drop items into the correct order:

````markdown
```yaml
type: ordering
question: "Arrange these steps in order:"
items:
  - "Step 1"
  - "Step 2"
  - "Step 3"
correct-order: [0, 1, 2]
points: 10
content: |
  Order matters!
```
````

## Core Features

### LocalStorage Persistence

**Never lose your answers again!** All exam answers are automatically saved to your browser's localStorage as you type or interact.

**Features:**

- ✅ Auto-saves on every interaction (typing, clicking, dragging)
- ✅ Restores state on page reload
- ✅ Expires after 24 hours to prevent stale data
- ✅ Clears automatically on successful submission
- ✅ Works with all exam types (choice, categorization, hotspot, ordering, etc.)
- ✅ Saves hints revealed and time remaining
- ✅ Privacy-friendly - all data stays in your browser

**What's Saved:**

- Selected answers (checkboxes, radio buttons)
- Text inputs and essay responses
- Drag-and-drop positions (categorization, ordering)
- Clicked regions (hotspot/image map)
- Numeric values and code completion
- Revealed hints
- Remaining time on timed questions

**Try it yourself:** See the [Persistence Demo](https://kjanat.github.io/mkdocs-exam/persistence-demo/) page to test this feature live!

## Pedagogical Features

### Hints with Score Penalties

Provide progressive hints that reduce the score when revealed:

````markdown
```yaml
question: "What is the capital of France?"
answer-correct:
  - "Paris"
hints:
  - text: "It's known as the City of Light"
    penalty: 10
  - text: "The Eiffel Tower is located here"
    penalty: 20
points: 10
content: |
  Paris is the capital of France.
```
````

### Explanations

Show explanations conditionally (always, on-correct, on-wrong, never):

````markdown
```yaml
question: "What is 2 + 2?"
answer-correct:
  - "4"
answer:
  - "3"
  - "5"
explanation: "Addition is combining two numbers. 2 + 2 = 4."
show-explanation: "on-correct"
content: |
  Great job!
```
````

### Answer Feedback

Provide specific feedback for each answer choice:

````markdown
```yaml
question: "Which planet is closest to the Sun?"
answer-correct:
  - value: "Mercury"
    feedback: "Correct! Mercury orbits closest to the Sun."
answer:
  - value: "Venus"
    feedback: "Venus is the second planet."
content: |
  Mercury is closest to the Sun.
```
````

### Rich Media Support

Add images, videos, or audio to questions:

````markdown
```yaml
question: "What shape is shown?"
media:
  type: image
  src: "https://example.com/triangle.png"
  alt: "A geometric shape"
  caption: "Geometric shape"
answer-correct:
  - "Triangle"
answer:
  - "Square"
  - "Circle"
content: |
  The image shows a triangle.
```
````

### Time Limits

Add countdown timers that auto-submit when time expires:

````markdown
```yaml
question: "Quick! What is 7 × 8?"
answer-correct:
  - "56"
time-limit: 30
points: 10
content: |
  Speed matters!
```
````

### Points and Scoring

Assign custom point values to questions:

````markdown
```yaml
question: "What is the capital of Australia?"
answer-correct:
  - "Canberra"
points: 20
content: |
  Canberra is the capital.
```
````

## Advanced Exam Types (Phase 2)

### Multi-Select with Partial Credit

Award partial credit for partially correct answers with weighted scoring:

````markdown
```yaml
question: "Select all fruits (each worth 50% of total points):"
answer-correct:
  - value: "Apple"
    weight: 0.5
  - value: "Banana"
    weight: 0.5
answer:
  - value: "Carrot"
    weight: 0.5
partial-credit: true
points: 10
content: |
  Partial credit is awarded based on the weights of correctly selected answers.
```
````

### Categorization (Drag and Drop)

Drag items into the correct categories:

````markdown
```yaml
type: categorization
question: "Categorize these items into Animals and Fruits:"
items:
  - "Dog"
  - "Cat"
  - "Apple"
  - "Banana"
categories:
  - "Animals"
  - "Fruits"
correct-mapping:
  0: 0 # Dog -> Animals
  1: 0 # Cat -> Animals
  2: 1 # Apple -> Fruits
  3: 1 # Banana -> Fruits
points: 10
content: |
  Drag each item to its correct category.
```
````

### Hotspot/Image Map

Click on correct regions of an image:

````markdown
```yaml
type: hotspot
question: "Click on all the European countries on this map:"
image: "https://example.com/world-map.png"
regions:
  - x: 20
    y: 15
    width: 10
    height: 8
    correct: true
    label: "France"
  - x: 25
    y: 18
    width: 8
    height: 6
    correct: true
    label: "Spain"
  - x: 50
    y: 40
    width: 12
    height: 10
    correct: false
    label: "Australia"
points: 15
content: |
  Regions are positioned using percentages (x, y, width, height).
```
````

### Plugin Configuration

Configure global settings in `mkdocs.yml`:

```yaml
plugins:
  - mkdocs-exam:
      enabled: true
      default_type: choice
      default_points: 1
      show_answers: false
      randomize_answers: false
      theme: default
```

## Advanced Features

### Multi-Document YAML

You can define multiple exams in a single codeblock using YAML's `---` document separator:

````markdown
```yaml
question: "First question?"
answer-correct:
  - "Answer 1"
content: |
  First exam content
---
question: "Second question?"
answer-correct:
  - "Answer 2"
content: |
  Second exam content
```
````

### Environment Variable Interpolation

Support for environment variables in YAML using `${VAR}` or `${VAR:-default}` syntax:

````markdown
```yaml
question: "What is the API endpoint?"
answer-correct:
  - "${API_URL}"
answer:
  - "${FALLBACK_URL:-https://example.com}"
content: |
  The correct endpoint is ${API_URL:-https://api.example.com}
```
````

### YAML Anchors and Aliases

Full support for YAML anchors (`&`) and aliases (`*`) to reuse configuration:

````markdown
```yaml
question: "Select all correct options"
answer-correct: &correct
  - "Option A"
  - "Option B"
answer:
  - "Option C"
content: |
  Reference answers with anchors
```
````

### Markdown Support

All string fields (question, answers, content) support **full Markdown syntax**:

`````markdown
````yaml
question: "What does `git commit` do?"
answer-correct:
  - "Creates a **new commit** with staged changes"
answer:
  - "*Pushes* changes to remote"
  - "Merges branches"
content: |
  ## Git Basics

  The `git commit` command:
  - Records changes
  - Creates a snapshot
  - Requires a message

  ```bash
  git commit -m "Your message"
````
`````

```
```

````
## [Demo](https://kjanat.github.io/mkdocs-exam/)

## Screenshots

The single choice exam will get generated as a radio button group, while the multiple choice exam will get generated as a checkbox group.

### Single choice

<img src="assets/images/exam.png" width="400rem">

### Multiple choice

<img src="assets/images/exam-multi.png" width="400rem">

## Disable for a page

You can disable the exam for a page by adding the following to the top (meta) of the page:

```markdown
---
exam: disable
---
```

## License

This project is licensed under the [MIT License](LICENSE).
````
