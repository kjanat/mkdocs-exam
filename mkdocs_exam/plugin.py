from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from importlib import resources as impresources
from . import css, js
import re

# Read bundled CSS and JS and wrap them for inline injection
inp_file = impresources.files(css) / "exam.css"
with inp_file.open("rt") as f:
    style = f.read()
style = f'<style type="text/css">{style}</style>'

js_file = impresources.files(js) / "exam.js"
with js_file.open("rt") as f:
    js = f.read()
js = f'<script type="text/javascript" defer>{js}</script>'

# <exam>
# question: Are you ready?
# answer-correct: Yes!
# answer: No!
# answer: Maybe!
# content:
# <h2>Provide some additional content</h2>
# </exam>


class MkDocsExamPlugin(BasePlugin):
    """Convert custom ``<exam>`` blocks into interactive HTML quizzes."""

    def __init__(self):
        """Initialize default state for the plugin."""
        self.enabled = True
        self.dirty = False

    def on_startup(self, *, command, dirty: bool) -> None:
        """Configure the plugin on startup."""
        self.dirty = dirty

    def on_page_markdown(self, markdown, page, config, **kwargs):
        """Parse exam blocks in markdown and generate the HTML quiz."""

        if "exam" in page.meta and page.meta["exam"] == "disable":
            return markdown

        # Look for ``<exam>`` ... ``</exam>`` blocks using a non-greedy regex
        EXAM_START_TAG = "<exam>"
        EXAM_END_TAG = "</exam>"
        REGEX = f"{re.escape(EXAM_START_TAG)}(.*?){re.escape(EXAM_END_TAG)}"
        matches = re.findall(REGEX, markdown, re.DOTALL)
        exam_id = 0
        for match in matches:
            exam_lines = [ln.strip() for ln in match.splitlines() if ln.strip()]
            content_idx = exam_lines.index("content:")
            header_lines = exam_lines[:content_idx]
            content = exam_lines[content_idx + 1 :]

            q_type = "choice"
            question = ""
            answers: list[str] = []
            correct_idx: list[int] = []
            for line in header_lines:
                if line.startswith("type:"):
                    q_type = line.split("type:", 1)[1].strip().lower()
                elif line.startswith("question:"):
                    question = line.split("question:", 1)[1].strip()
                elif line.startswith("answer-correct:"):
                    answers.append(line.split("answer-correct:", 1)[1].strip())
                    correct_idx.append(len(answers) - 1)
                elif line.startswith("answer:"):
                    answers.append(line.split("answer:", 1)[1].strip())

            html_question = question
            full_answers: list[str] = []

            if q_type == "choice" or q_type == "truefalse":
                as_checkboxes = len(correct_idx) > 1
                for i, ans in enumerate(answers):
                    is_correct = i in correct_idx
                    input_id = f"exam-{exam_id}-{i}"
                    input_type = "checkbox" if as_checkboxes else "radio"
                    correct = "correct" if is_correct else ""
                    full_answers.append(
                        f'<div><input type="{input_type}" name="answer" value="{i}" id="{input_id}" {correct}>'
                        f'<label for="{input_id}">{ans}</label></div>'
                    )
            elif q_type in {"short-answer", "essay"}:
                correct_vals = [answers[i] for i in correct_idx] or answers
                correct_attr = "|".join(correct_vals)
                full_answers.append(f'<div><input type="text" name="answer" correct="{correct_attr}" ></div>')
            elif q_type == "fill":
                correct_vals = [answers[i] for i in correct_idx] or answers
                correct_attr = "|".join(correct_vals)
                html_question = question.replace("___", f'<input type="text" name="answer" correct="{correct_attr}">')
            else:
                # fallback to choice rendering
                as_checkboxes = len(correct_idx) > 1
                for i, ans in enumerate(answers):
                    is_correct = i in correct_idx
                    input_id = f"exam-{exam_id}-{i}"
                    input_type = "checkbox" if as_checkboxes else "radio"
                    correct = "correct" if is_correct else ""
                    full_answers.append(
                        f'<div><input type="{input_type}" name="answer" value="{i}" id="{input_id}" {correct}>'
                        f'<label for="{input_id}">{ans}</label></div>'
                    )

            html_answers = "".join(full_answers)
            exam_html = (
                f'<div class="exam" data-type="{q_type}"><h3>{html_question}</h3><form><fieldset>'
                f"{html_answers}</fieldset>"
                '<button type="submit" class="exam-button">Submit</button>'
                f'</form><section class="content hidden">{"\n".join(content)}</section></div>'
            )
            # Replace the original block with the generated HTML
            old_exam = EXAM_START_TAG + match + EXAM_END_TAG
            markdown = markdown.replace(old_exam, exam_html)
            exam_id += 1
        return markdown

    def on_page_content(self, html: str, *, page: Page, config: MkDocsConfig, files: Files) -> str | None:
        """Append inline resources to the rendered HTML page."""

        # Inject CSS and JavaScript so the quiz works without extra files
        html = html + style + js
        return html
