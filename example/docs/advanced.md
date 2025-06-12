# Advanced Exam Features

The following examples demonstrate advanced usage of the `mkdocs-exam` plugin.

## Multiple correct answers

<exam>
question: Select the <strong>prime</strong> numbers.
answer-correct: 2
answer-correct: 3
answer: 4
answer-correct: 5
content:

<p>Multiple answers may be correct in this question.</p>
</exam>

## HTML in questions and answers

<exam>
question: What does the <code>&lt;br&gt;</code> tag do?
answer-correct: Inserts a line break
answer: <em>Makes text bold</em>
answer: Creates a hyperlink
content:

<p>The <code>br</code> element simply causes a line break in the rendered page.</p>
</exam>

## Short answer

<exam>
type: short-answer
question: Who wrote "1984"?
answer-correct: George Orwell
content:

<p>The novel "1984" was written by George Orwell.</p>
</exam>

## Fill in the blank

<exam>
type: fill
question: The capital of France is ___
answer-correct: Paris
content:

<p>Paris is the capital city of France.</p>
</exam>

## True/false

<exam>
type: truefalse
question: The Earth orbits the Sun.
answer-correct: True
content:

<p>This is obviously true.</p>
</exam>

## Essay

<exam>
type: essay
question: Explain the theory of relativity in one paragraph.
answer-correct: It deals with space and time.
content:

<p>Provide an explanation.</p>
</exam>
