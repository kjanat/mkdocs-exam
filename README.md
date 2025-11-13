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
