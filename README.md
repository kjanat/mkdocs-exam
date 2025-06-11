# MkDocs Exam Plugin

## Installation

This plugin hasn't landed on PyPI yet. Install it straight from GitHub:

```bash
uv pip install git+https://github.com/kjanat/mkdocs-exam.git
```
For local development, install the repository in editable mode:
```bash
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

```bash
<?exam?>
question: Are you ready?
answer-correct: Yes!
answer: No!
answer: Maybe!
content:
<h2>Provide some additional content</h2>
<?/exam?>
```

> **Info** The answers can get styled with HTML (like `<code>Yes!</code>`)

> **Warning** The exam content needs to be valid **_HTML_**

### Multiple choice

You can also create a multiple choice exam, by providing multiple answers as correct.

```bash
<?exam?>
question: Are you ready?
answer-correct: Yes!
answer: No!
answer-correct: Maybe!
content:
<h2>Provide some additional content</h2>
<?/exam?>
```

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
