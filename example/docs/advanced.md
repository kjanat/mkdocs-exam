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
