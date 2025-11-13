# Advanced Exam Features

The following examples demonstrate advanced usage of the `mkdocs-exam` plugin.

## Multiple correct answers

```yaml
question: "Select the **prime** numbers."
answer-correct:
  - "2"
  - "3"
  - "5"
answer:
  - "4"
content: |
  Multiple answers may be correct in this question.
```

## HTML in questions and answers

```yaml
question: "What does the `<br>` tag do?"
answer-correct:
  - "Inserts a line break"
answer:
  - "*Makes text bold*"
  - "Creates a hyperlink"
content: |
  The `br` element simply causes a line break in the rendered page.
```

## Short answer

```yaml
type: short-answer
question: "Who wrote \"1984\"?"
answer-correct:
  - "George Orwell"
content: |
  The novel "1984" was written by George Orwell.
```

## Fill in the blank

```yaml
type: fill
question: "The capital of France is ___"
answer-correct:
  - "Paris"
content: |
  Paris is the capital city of France.
```

## True/false

```yaml
type: truefalse
question: "The Earth orbits the Sun."
answer-correct:
  - "True"
content: |
  This is obviously true.
```

## Essay

```yaml
type: essay
question: "Explain the theory of relativity in one paragraph."
answer-correct:
  - "It deals with space and time."
content: |
  Provide an explanation.
```

## Matching

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

## Multi-Document YAML

Multiple exams in a single codeblock:

```yaml
question: "What is 2 + 2?"
answer-correct:
  - "4"
answer:
  - "3"
  - "5"
content: |
  Basic arithmetic
---
question: "What is 5 * 5?"
answer-correct:
  - "25"
answer:
  - "20"
  - "30"
content: |
  More arithmetic
```

## Environment Variables

```yaml
question: "What is the environment?"
answer-correct:
  - "${NODE_ENV:-development}"
content: |
  Testing in ${NODE_ENV:-development} mode
```

## YAML Anchors

```yaml
question: "Select programming languages"
answer-correct: &languages
  - "Python"
  - "JavaScript"
answer:
  - "HTML"
content: |
  Programming languages are listed above
```
