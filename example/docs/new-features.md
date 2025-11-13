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

## Phase 2 Advanced Features

### Multi-Select with Partial Credit

Weighted scoring allows for partial credit based on which answers are selected:

```yaml
question: "Select all the programming languages (not markup languages):"
answer-correct:
  - value: "Python"
    weight: 0.33
    feedback: "Correct! Python is a programming language."
  - value: "JavaScript"
    weight: 0.33
    feedback: "Correct! JavaScript is a programming language."
  - value: "Java"
    weight: 0.34
    feedback: "Correct! Java is a programming language."
answer:
  - value: "HTML"
    weight: 0.33
    feedback: "HTML is a markup language, not a programming language."
  - value: "CSS"
    weight: 0.33
    feedback: "CSS is a stylesheet language, not a programming language."
partial-credit: true
points: 30
content: |
  With partial credit enabled, you receive points proportional to correct selections minus penalties for incorrect selections.
```

### Basic Partial Credit Example

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
  - value: "Broccoli"
    weight: 0.5
partial-credit: true
points: 10
content: |
  If you select both fruits, you get 100%. If you select one fruit and one vegetable, you get 0% (50% - 50% penalty).
```

### Categorization Exam Type

Drag and drop items into their correct categories:

```yaml
type: categorization
question: "Categorize these programming concepts:"
items:
  - "for loop"
  - "if statement"
  - "list"
  - "dictionary"
  - "while loop"
  - "tuple"
categories:
  - "Control Flow"
  - "Data Structures"
correct-mapping:
  0: 0 # for loop -> Control Flow
  1: 0 # if statement -> Control Flow
  2: 1 # list -> Data Structures
  3: 1 # dictionary -> Data Structures
  4: 0 # while loop -> Control Flow
  5: 1 # tuple -> Data Structures
points: 20
content: |
  **Control Flow** structures control the execution order of code.
  **Data Structures** organize and store data.
```

### Biology Categorization

```yaml
type: categorization
question: "Sort these organisms by their classification:"
items:
  - "Dog"
  - "Cat"
  - "Eagle"
  - "Sparrow"
  - "Salmon"
  - "Tuna"
categories:
  - "Mammals"
  - "Birds"
  - "Fish"
correct-mapping:
  0: 0 # Dog -> Mammals
  1: 0 # Cat -> Mammals
  2: 1 # Eagle -> Birds
  3: 1 # Sparrow -> Birds
  4: 2 # Salmon -> Fish
  5: 2 # Tuna -> Fish
points: 15
content: |
  Drag each organism into its correct taxonomic class.
```

### Hotspot/Image Map Exam Type

Click on specific regions of an image to answer:

```yaml
type: hotspot
question: "Click on all the primary colors in the color wheel:"
image: "https://example.com/color-wheel.png"
regions:
  - x: 25
    y: 10
    width: 15
    height: 15
    correct: true
    label: "Red"
  - x: 10
    y: 40
    width: 15
    height: 15
    correct: true
    label: "Blue"
  - x: 40
    y: 40
    width: 15
    height: 15
    correct: true
    label: "Yellow"
  - x: 30
    y: 25
    width: 15
    height: 15
    correct: false
    label: "Green"
  - x: 55
    y: 25
    width: 15
    height: 15
    correct: false
    label: "Orange"
points: 15
content: |
  The three primary colors are Red, Blue, and Yellow.
  All other colors can be created by mixing these three.
```

### Anatomy Hotspot

```yaml
type: hotspot
question: "Identify the major organs in the digestive system:"
image: "https://example.com/human-anatomy.png"
regions:
  - x: 45
    y: 20
    width: 10
    height: 8
    correct: true
    label: "Stomach"
  - x: 42
    y: 35
    width: 12
    height: 20
    correct: true
    label: "Small Intestine"
  - x: 40
    y: 58
    width: 14
    height: 15
    correct: true
    label: "Large Intestine"
  - x: 30
    y: 15
    width: 8
    height: 6
    correct: false
    label: "Heart"
points: 20
content: |
  Click on the regions that are part of the digestive system.
  Coordinates are in percentages relative to the image dimensions.
```

### Geography Hotspot

```yaml
type: hotspot
question: "Click on all landlocked countries in Europe:"
image: "https://example.com/europe-map.png"
regions:
  - x: 52
    y: 48
    width: 6
    height: 5
    correct: true
    label: "Switzerland"
  - x: 58
    y: 46
    width: 5
    height: 4
    correct: true
    label: "Austria"
  - x: 70
    y: 52
    width: 7
    height: 6
    correct: true
    label: "Hungary"
  - x: 40
    y: 35
    width: 8
    height: 9
    correct: false
    label: "France"
  - x: 75
    y: 40
    width: 9
    height: 7
    correct: false
    label: "Poland"
points: 25
content: |
  Landlocked countries have no direct access to the ocean or sea.
  Switzerland, Austria, and Hungary are landlocked European countries.
```

## Plugin Configuration Examples

Configure default behavior for all exams:

### Basic Configuration

```yaml
# In mkdocs.yml
plugins:
  - mkdocs-exam:
      enabled: true
      default_type: choice
      default_points: 1
```

### Full Configuration

```yaml
# In mkdocs.yml
plugins:
  - mkdocs-exam:
      enabled: true # Enable/disable plugin globally
      default_type: choice # Default exam type if not specified
      default_points: 1 # Default points per question
      show_answers: false # Show correct answers after submission
      randomize_answers: false # Shuffle answer order
      theme: default # Theme name for custom styling
```

### Advanced Multi-Feature Example

Combining Phase 1 and Phase 2 features:

```yaml
type: categorization
question: "Categorize these data structures by their average time complexity for search operations:"
items:
  - "Array (unsorted)"
  - "Hash Table"
  - "Binary Search Tree"
  - "Linked List"
categories:
  - "O(1) - Constant"
  - "O(log n) - Logarithmic"
  - "O(n) - Linear"
correct-mapping:
  0: 2 # Array (unsorted) -> O(n)
  1: 0 # Hash Table -> O(1)
  2: 1 # Binary Search Tree -> O(log n)
  3: 2 # Linked List -> O(n)
hints:
  - text: "Hash tables use direct key-to-value mapping"
    penalty: 10
  - text: "Binary Search Trees divide the search space in half each step"
    penalty: 15
  - text: "Unsorted arrays and linked lists require checking every element"
    penalty: 20
explanation: |
  **Time Complexity Summary:**
  - Hash tables provide O(1) average-case lookup
  - Binary Search Trees provide O(log n) search with balanced trees
  - Unsorted arrays and linked lists require O(n) linear search
show-explanation: "on-correct"
points: 30
time-limit: 180
content: |
  Understanding time complexity is crucial for choosing the right data structure.
```
