# Phase 2 Advanced Features

This page showcases the advanced Phase 2 features: partial credit, categorization, hotspot/image maps, and plugin configuration.

## Multi-Select with Partial Credit

### Programming Languages Quiz

Award partial credit based on weighted answers:

```yaml
question: "Select all the programming languages (not markup languages):"
answer-correct:
  - value: "Python"
    weight: 0.33
    feedback: "Correct! Python is a general-purpose programming language."
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
  **How Partial Credit Works:**
  - Selecting all 3 correct answers = 100% (30 points)
  - Selecting 2 correct + 0 wrong = 66% (20 points)
  - Selecting 2 correct + 1 wrong = 33% (10 points)
  - Selecting 1 correct + 2 wrong = 0% (negative penalties applied)
```

### Fruit Selection Example

```yaml
question: "Select all fruits (each worth 50% of total points):"
answer-correct:
  - value: "Apple"
    weight: 0.5
    feedback: "Correct! Apples are fruits."
  - value: "Banana"
    weight: 0.5
    feedback: "Correct! Bananas are fruits."
answer:
  - value: "Carrot"
    weight: 0.5
    feedback: "Incorrect. Carrots are vegetables."
  - value: "Broccoli"
    weight: 0.5
    feedback: "Incorrect. Broccoli is a vegetable."
partial-credit: true
points: 10
content: |
  **Scoring breakdown:**
  - Both correct = 100% (10 points)
  - One correct = 50% (5 points)
  - One correct + one wrong = 0% (5 - 5 penalty)
  - Two wrong = negative score (clamped to 0)
```

### Science Concepts

```yaml
question: "Which of these are states of matter?"
answer-correct:
  - value: "Solid"
    weight: 0.25
  - value: "Liquid"
    weight: 0.25
  - value: "Gas"
    weight: 0.25
  - value: "Plasma"
    weight: 0.25
answer:
  - value: "Energy"
    weight: 0.25
  - value: "Heat"
    weight: 0.25
partial-credit: true
points: 20
content: |
  The four classical states of matter are solid, liquid, gas, and plasma.
```

## Categorization Exam Type

### Programming Concepts

Drag items into the correct categories:

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
  0: 0  # for loop -> Control Flow
  1: 0  # if statement -> Control Flow
  2: 1  # list -> Data Structures
  3: 1  # dictionary -> Data Structures
  4: 0  # while loop -> Control Flow
  5: 1  # tuple -> Data Structures
points: 20
content: |
  **Control Flow** structures control the execution order of code.
  **Data Structures** organize and store data efficiently.

  Drag each item to its appropriate category!
```

### Animal Classification

```yaml
type: categorization
question: "Sort these organisms by their taxonomic class:"
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
  0: 0  # Dog -> Mammals
  1: 0  # Cat -> Mammals
  2: 1  # Eagle -> Birds
  3: 1  # Sparrow -> Birds
  4: 2  # Salmon -> Fish
  5: 2  # Tuna -> Fish
points: 15
content: |
  Drag each organism into its correct taxonomic class.

  - **Mammals**: Warm-blooded vertebrates with hair
  - **Birds**: Warm-blooded vertebrates with feathers
  - **Fish**: Cold-blooded aquatic vertebrates
```

### Literary Genres

```yaml
type: categorization
question: "Categorize these books by genre:"
items:
  - "1984"
  - "The Hobbit"
  - "Pride and Prejudice"
  - "Dune"
  - "Romeo and Juliet"
  - "Harry Potter"
categories:
  - "Science Fiction"
  - "Fantasy"
  - "Classic Literature"
correct-mapping:
  0: 0  # 1984 -> Science Fiction
  1: 1  # The Hobbit -> Fantasy
  2: 2  # Pride and Prejudice -> Classic Literature
  3: 0  # Dune -> Science Fiction
  4: 2  # Romeo and Juliet -> Classic Literature
  5: 1  # Harry Potter -> Fantasy
points: 25
content: |
  Match each famous book to its literary genre.
```

### Data Structures Complexity

```yaml
type: categorization
question: "Categorize by average search time complexity:"
items:
  - "Array (unsorted)"
  - "Hash Table"
  - "Binary Search Tree"
  - "Linked List"
  - "Sorted Array (binary search)"
  - "Heap"
categories:
  - "O(1) - Constant"
  - "O(log n) - Logarithmic"
  - "O(n) - Linear"
correct-mapping:
  0: 2  # Array (unsorted) -> O(n)
  1: 0  # Hash Table -> O(1)
  2: 1  # Binary Search Tree -> O(log n)
  3: 2  # Linked List -> O(n)
  4: 1  # Sorted Array -> O(log n)
  5: 2  # Heap -> O(n) for search
points: 30
content: |
  **Time Complexity Categories:**
  - **O(1)**: Direct access, no iteration needed
  - **O(log n)**: Divide and conquer approach
  - **O(n)**: Must check each element
```

## Hotspot/Image Map Exam Type

### Color Theory

Click on correct regions of an image:

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
  - x: 15
    y: 60
    width: 15
    height: 15
    correct: false
    label: "Purple"
points: 15
content: |
  The three **primary colors** are Red, Blue, and Yellow.

  All other colors can be created by mixing these three primary colors.
  Green, orange, and purple are **secondary colors**.
```

### Human Anatomy

```yaml
type: hotspot
question: "Identify the organs in the digestive system:"
image: "https://example.com/human-anatomy.png"
regions:
  - x: 45
    y: 15
    width: 8
    height: 6
    correct: false
    label: "Esophagus (not digestive organ)"
  - x: 45
    y: 22
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
    y: 18
    width: 8
    height: 6
    correct: false
    label: "Heart"
  - x: 55
    y: 30
    width: 6
    height: 8
    correct: true
    label: "Liver"
points: 20
content: |
  Click on the regions that are major organs of the **digestive system**.

  The digestive system includes: stomach, small intestine, large intestine, and liver.
  All coordinates are percentages relative to the image dimensions.
```

### World Geography

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
  - x: 65
    y: 42
    width: 6
    height: 5
    correct: true
    label: "Czech Republic"
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
    label: "Poland (has Baltic Sea access)"
  - x: 48
    y: 30
    width: 7
    height: 6
    correct: false
    label: "Germany"
points: 25
content: |
  **Landlocked countries** have no direct access to the ocean or sea.

  In Europe, Switzerland, Austria, Hungary, and Czech Republic are landlocked.
  Poland and Germany have access to the Baltic Sea.
```

### Computer Parts

```yaml
type: hotspot
question: "Identify the CPU on this motherboard diagram:"
image: "https://example.com/motherboard.png"
regions:
  - x: 35
    y: 30
    width: 12
    height: 12
    correct: true
    label: "CPU Socket"
  - x: 60
    y: 25
    width: 18
    height: 8
    correct: false
    label: "RAM Slots"
  - x: 15
    y: 45
    width: 10
    height: 15
    correct: false
    label: "PCIe Slots"
  - x: 70
    y: 50
    width: 8
    height: 8
    correct: false
    label: "SATA Ports"
points: 10
content: |
  The **CPU (Central Processing Unit)** is typically located in the CPU socket,
  near the center-top of the motherboard.
```

## Combined Advanced Features

### Data Structures Deep Dive

Using categorization with hints, explanations, and time limits:

```yaml
type: categorization
question: "Categorize these data structures by their average time complexity for search operations:"
items:
  - "Array (unsorted)"
  - "Hash Table"
  - "Binary Search Tree"
  - "Linked List"
  - "Skip List"
categories:
  - "O(1) - Constant"
  - "O(log n) - Logarithmic"
  - "O(n) - Linear"
correct-mapping:
  0: 2  # Array (unsorted) -> O(n)
  1: 0  # Hash Table -> O(1)
  2: 1  # Binary Search Tree -> O(log n)
  3: 2  # Linked List -> O(n)
  4: 1  # Skip List -> O(log n)
hints:
  - text: "Hash tables use direct key-to-value mapping"
    penalty: 10
  - text: "Binary Search Trees and Skip Lists divide the search space"
    penalty: 15
  - text: "Unsorted arrays and linked lists must check every element"
    penalty: 20
explanation: |
  **Time Complexity Summary:**

  - **O(1)**: Hash tables provide constant-time average-case lookup through direct indexing
  - **O(log n)**: Binary Search Trees and Skip Lists divide the search space logarithmically
  - **O(n)**: Unsorted arrays and linked lists require linear search through all elements

  Understanding time complexity is crucial for choosing the right data structure!
show-explanation: "on-correct"
points: 30
time-limit: 180
content: |
  This question tests your understanding of algorithmic complexity.
  Consider the average case for each data structure.
```

### Weighted Science Quiz

Multi-select with partial credit and rich features:

```yaml
question: "Which of these are noble gases? (Each correct answer is worth 20%)"
answer-correct:
  - value: "Helium"
    weight: 0.2
    feedback: "Correct! Helium is a noble gas."
  - value: "Neon"
    weight: 0.2
    feedback: "Correct! Neon is a noble gas."
  - value: "Argon"
    weight: 0.2
    feedback: "Correct! Argon is a noble gas."
  - value: "Krypton"
    weight: 0.2
    feedback: "Correct! Krypton is a noble gas."
  - value: "Xenon"
    weight: 0.2
    feedback: "Correct! Xenon is a noble gas."
answer:
  - value: "Nitrogen"
    weight: 0.2
    feedback: "Nitrogen is not a noble gas, it's diatomic."
  - value: "Oxygen"
    weight: 0.2
    feedback: "Oxygen is not a noble gas."
partial-credit: true
hints:
  - text: "Noble gases are in Group 18 of the periodic table"
    penalty: 15
  - text: "They have full valence electron shells"
    penalty: 25
explanation: "Noble gases are: Helium, Neon, Argon, Krypton, Xenon, and Radon. They are chemically inert due to their full valence shells."
show-explanation: "always"
points: 50
time-limit: 120
media:
  type: image
  src: "https://example.com/periodic-table.png"
  alt: "Periodic Table"
  caption: "The Periodic Table of Elements"
content: |
  ## Noble Gases

  Noble gases are elements in **Group 18** of the periodic table.
  They are characterized by:
  - Full valence electron shells
  - Chemical inertness
  - Low reactivity
  - Gaseous state at room temperature
```

## Plugin Configuration

### Basic Configuration

Configure plugin defaults in your `mkdocs.yml`:

```yaml
# In mkdocs.yml
plugins:
  - mkdocs-exam:
      enabled: true
      default_type: choice
      default_points: 1
```

### Full Configuration Options

```yaml
# In mkdocs.yml
plugins:
  - mkdocs-exam:
      enabled: true           # Enable/disable plugin globally
      default_type: choice    # Default exam type if not specified
      default_points: 1       # Default points per question
      show_answers: false     # Show correct answers after submission
      randomize_answers: false # Shuffle answer order (not implemented yet)
      theme: default          # Theme name for custom styling
```

### Configuration Use Cases

**For Testing/Development:**
```yaml
plugins:
  - mkdocs-exam:
      enabled: true
      show_answers: true     # Show answers for quick testing
```

**For Production:**
```yaml
plugins:
  - mkdocs-exam:
      enabled: true
      show_answers: false    # Hide answers in production
      default_points: 5      # Higher point values
```

**Disable Plugin:**
```yaml
plugins:
  - mkdocs-exam:
      enabled: false         # Disable all exam processing
```

## Best Practices

### Partial Credit Tips

1. **Balance weights carefully**: Ensure weights add up to 1.0 for intuitive percentages
2. **Provide feedback**: Use the `feedback` field to explain why answers are right/wrong
3. **Set appropriate penalties**: Wrong selections deduct their weight from the score
4. **Test edge cases**: Consider what happens when all wrong answers are selected

### Categorization Tips

1. **Clear categories**: Use descriptive category names
2. **Logical groupings**: Ensure items clearly belong to one category
3. **Appropriate difficulty**: Start with 2-3 categories, increase complexity gradually
4. **Visual clarity**: Keep item names concise for better drag-and-drop UX

### Hotspot Tips

1. **Percentage positioning**: Use percentages (0-100) for x, y, width, height
2. **Responsive design**: Percentages ensure hotspots work on any screen size
3. **Clear regions**: Make clickable regions large enough to click easily
4. **Visual feedback**: Regions highlight on hover to show they're interactive
5. **Label wisely**: Use the `label` field for debugging (not shown to students)

### Plugin Configuration Tips

1. **Environment-specific**: Use different configs for dev vs production
2. **Documentation**: Document your config choices for team members
3. **Testing**: Test with `show_answers: true` during development
4. **Consistency**: Set sensible defaults to reduce repetition in exam definitions
