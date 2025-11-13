# New Features Examples

This page demonstrates all the newly implemented features in mkdocs-exam.

## Hints System

Hints can be revealed by students with optional score penalties:

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
  Paris is the capital and largest city of France.
```

## Explanations with Conditional Display

Show explanations always, only when correct, or only when wrong:

### Show on Correct

```yaml
question: "What is 2 + 2?"
answer-correct:
  - "4"
answer:
  - "3"
  - "5"
explanation: "Addition is combining two numbers to get a sum. 2 + 2 = 4."
show-explanation: "on-correct"
content: |
  Great job! You got it right.
```

### Show on Wrong

```yaml
question: "What is 3 × 3?"
answer-correct:
  - "9"
answer:
  - "6"
  - "12"
explanation: "Multiplication means repeated addition. 3 × 3 = 3 + 3 + 3 = 9."
show-explanation: "on-wrong"
content: |
  Try again!
```

### Always Show

```yaml
question: "What is the speed of light?"
answer-correct:
  - "299792458"
answer:
  - "300000000"
  - "186000"
explanation: "The speed of light in vacuum is exactly 299,792,458 meters per second."
show-explanation: "always"
content: |
  Speed of light is a fundamental constant.
```

## Answer Feedback

Provide specific feedback for each answer choice:

```yaml
question: "Which planet is closest to the Sun?"
answer-correct:
  - value: "Mercury"
    feedback: "Correct! Mercury orbits closest to the Sun."
answer:
  - value: "Venus"
    feedback: "Venus is actually the second planet from the Sun."
  - value: "Mars"
    feedback: "Mars is the fourth planet from the Sun."
content: |
  Mercury is the smallest planet and closest to the Sun.
```

## Numeric Exam Type

Accept numeric answers within a tolerance range:

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

### Numeric with Units

```yaml
type: numeric
question: "How many meters are in a kilometer?"
answer-correct:
  - 1000
tolerance: 0
unit: "m"
points: 5
content: |
  There are exactly 1000 meters in 1 kilometer.
```

## Code Completion Exam Type

Fill-in-the-blank for code:

```yaml
type: code-completion
question: "Complete the Python function to add two numbers:"
template: |
  def add(a, b):
      return a ___ b
language: python
blanks:
  - correct: ["+", "plus"]
points: 10
content: |
  The addition operator in Python is +
```

### Multiple Blanks

```yaml
type: code-completion
question: "Complete the JavaScript function:"
template: |
  function greet(___) {
      ___ "Hello, " + name;
  }
language: javascript
blanks:
  - correct: ["name"]
  - correct: ["return"]
points: 15
content: |
  Functions can accept parameters and return values.
```

## Ordering Exam Type

Drag-and-drop items into the correct order:

```yaml
type: ordering
question: "Arrange these steps of the scientific method in order:"
items:
  - "Ask a question"
  - "Form a hypothesis"
  - "Conduct experiment"
  - "Analyze results"
  - "Draw conclusions"
correct-order: [0, 1, 2, 3, 4]
points: 10
content: |
  The scientific method is a systematic approach to research.
```

### Custom Order

```yaml
type: ordering
question: "Sort these numbers from smallest to largest:"
items:
  - "42"
  - "7"
  - "105"
  - "23"
correct-order: [1, 3, 0, 2]
points: 5
content: |
  The correct order is: 7, 23, 42, 105
```

## Rich Media Support

### Image Questions

```yaml
question: "What shape is shown in the image?"
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

### Video Questions

```yaml
question: "What concept is demonstrated in the video?"
media:
  type: video
  src: "https://example.com/gravity.mp4"
  caption: "Physics demonstration"
answer-correct:
  - "Gravity"
answer:
  - "Magnetism"
  - "Friction"
content: |
  The video demonstrates gravitational force.
```

### Audio Questions

```yaml
question: "What instrument is playing in this audio clip?"
media:
  type: audio
  src: "https://example.com/piano.mp3"
  caption: "Musical instrument"
answer-correct:
  - "Piano"
answer:
  - "Guitar"
  - "Violin"
content: |
  The audio features a piano.
```

## Time Limits

Add a countdown timer that auto-submits when time expires:

```yaml
question: "Quick! What is 7 × 8?"
answer-correct:
  - "56"
answer:
  - "54"
  - "63"
time-limit: 30
points: 10
content: |
  Speed matters in mental math!
```

## Points and Scoring

Assign custom point values to questions:

```yaml
question: "What is the capital of Australia?"
answer-correct:
  - "Canberra"
answer:
  - "Sydney"
  - "Melbourne"
points: 20
content: |
  Many people think it's Sydney, but Canberra is the capital.
```

## Combined Features Example

A comprehensive example using multiple new features:

```yaml
type: choice
question: "Which programming language was created by Guido van Rossum?"
answer-correct:
  - value: "Python"
    feedback: "Correct! Guido van Rossum created Python in 1991."
answer:
  - value: "Java"
    feedback: "Java was created by James Gosling at Sun Microsystems."
  - value: "JavaScript"
    feedback: "JavaScript was created by Brendan Eich at Netscape."
  - value: "Ruby"
    feedback: "Ruby was created by Yukihiro Matsumoto."
hints:
  - text: "It's named after a British comedy group"
    penalty: 15
  - text: "The language is known for its use of indentation"
    penalty: 25
explanation: "Python was created by Guido van Rossum and first released in 1991. It emphasizes code readability and uses significant indentation."
show-explanation: "on-correct"
points: 25
time-limit: 60
media:
  type: image
  src: "https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg"
  alt: "Python logo"
  caption: "The Python programming language logo"
content: |
  ## Learn More

  Python is a high-level, interpreted programming language known for its:
  - Clear, readable syntax
  - Extensive standard library
  - Large ecosystem of third-party packages
  - Strong community support
```

## Advanced Numeric with Hints

```yaml
type: numeric
question: "Calculate the area of a circle with radius 5 (use π ≈ 3.14)"
answer-correct:
  - 78.5
tolerance: 0.5
unit: "square units"
hints:
  - text: "The formula is A = πr²"
    penalty: 20
  - text: "Substitute r = 5 into the formula"
    penalty: 30
explanation: "Area = π × 5² = 3.14 × 25 = 78.5 square units"
show-explanation: "always"
points: 30
time-limit: 120
content: |
  The area of a circle is calculated using the formula A = πr².
```
