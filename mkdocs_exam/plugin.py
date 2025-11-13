from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from importlib import resources as impresources
from . import css, js
import re
import yaml

# Read bundled CSS and JS and wrap them for inline injection
inp_file = impresources.files(css) / "exam.css"
with inp_file.open("r", encoding="utf-8") as f:
    style = f.read()
style = f'<style type="text/css">{style}</style>'

js_file = impresources.files(js) / "exam.js"
with js_file.open("r", encoding="utf-8") as f:
    script_content = f.read()
script_tag = f'<script type="text/javascript" defer>{script_content}</script>'

# ```yaml
# question: "Are you ready?"
# answer-correct:
#   - "Yes!"
# answer:
#   - "No!"
#   - "Maybe!"
# content: |
#   ## Provide some additional content
# ```


class MkDocsExamPlugin(BasePlugin):  # type: ignore[type-arg]
    """Convert custom ``<exam>`` blocks into interactive HTML quizzes."""

    def __init__(self) -> None:
        """Initialize default state for the plugin."""
        self.enabled = True
        self.dirty = False

    def on_startup(self, *, command: str, dirty: bool) -> None:
        """Configure the plugin on startup."""
        self.dirty = dirty

    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files: Files | None = None) -> str:  # type: ignore[override]
        """Parse exam blocks in markdown and generate the HTML quiz."""

        if "exam" in page.meta and page.meta["exam"] == "disable":
            return markdown

        # Look for ```exam or ```yaml codeblocks
        REGEX = r"```(?:exam|yaml)\s*\n(.*?)```"
        matches = re.findall(REGEX, markdown, re.DOTALL)
        exam_id = 0
        for match in matches:
            # Parse YAML content
            try:
                exam_data = yaml.safe_load(match)
            except yaml.YAMLError as e:
                # Skip invalid YAML blocks
                continue

            # Extract exam properties from YAML
            q_type = exam_data.get("type", "choice").lower()
            question = exam_data.get("question", "")
            content_lines = exam_data.get("content", "").strip().splitlines()

            # Process answers
            answers: list[str] = []
            correct_idx: list[int] = []

            # Get answer-correct field
            answer_correct = exam_data.get("answer-correct", [])
            if isinstance(answer_correct, str):
                answer_correct = [answer_correct]
            elif answer_correct is None:
                answer_correct = []

            # Get answer field
            answer_list = exam_data.get("answer", [])
            if isinstance(answer_list, str):
                answer_list = [answer_list]
            elif answer_list is None:
                answer_list = []

            # Combine answers, tracking which are correct
            for ans in answer_correct:
                answers.append(str(ans))
                correct_idx.append(len(answers) - 1)

            for ans in answer_list:
                answers.append(str(ans))

            html_question = question
            full_answers: list[str] = []

            if q_type == "choice" or q_type == "truefalse":
                if q_type == "truefalse":
                    if not answers:
                        answers = ["True", "False"]
                        if not correct_idx:
                            correct_idx = [0]
                    elif len(answers) == 1:
                        if answers[0].strip().lower() in {"true", "yes"}:
                            answers.append("False")
                        else:
                            answers.append("True")
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
            elif q_type in {"short-answer", "fill", "essay"}:
                correct_vals = [answers[i] for i in correct_idx] or answers
                correct_attr = "|".join(correct_vals)
                if q_type == "essay":  # use textarea for long-form answers
                    full_answers.append(
                        f'<div><textarea name="answer" rows="4" correct="{correct_attr}"></textarea></div>'
                    )
                elif q_type == "fill":
                    html_question = question.replace(
                        "___", f'<input type="text" name="answer" correct="{correct_attr}">'
                    )
                else:
                    full_answers.append(f'<div><input type="text" name="answer" correct="{correct_attr}" ></div>')
            elif q_type == "matching":
                pairs = [ans.split("|") for ans in answers]
                left = [p[0].strip() for p in pairs]
                right = [p[1].strip() for p in pairs]
                options = "".join(f"<option>{r}</option>" for r in right)
                for i, left_item in enumerate(left):
                    full_answers.append(
                        f"<div><label>{left_item} "
                        f'<select name="answer" correct="{right[i]}">{options}</select>'
                        "</label></div>"
                    )

            html_answers = "".join(full_answers)
            content_html = "\n".join(content_lines)
            exam_html = (
                f'<div class="exam" data-type="{q_type}"><h3>{html_question}</h3><form><fieldset>'
                f"{html_answers}</fieldset>"
                '<button type="submit" class="exam-button">Submit</button>'
                f'</form><section class="content hidden">{content_html}</section></div>'
            )
            # Replace the original block with the generated HTML
            # Find the full codeblock (including delimiters) and replace it
            old_exam_pattern = re.escape(f"```yaml\n{match}```")
            if re.search(old_exam_pattern, markdown):
                markdown = re.sub(old_exam_pattern, exam_html, markdown, count=1)
            else:
                # Try with ```exam
                old_exam_pattern = re.escape(f"```exam\n{match}```")
                markdown = re.sub(old_exam_pattern, exam_html, markdown, count=1)
            exam_id += 1
        return markdown

    def on_page_content(self, html: str, *, page: Page, config: MkDocsConfig, files: Files) -> str | None:
        """Append inline resources to the rendered HTML page."""

        # Inject CSS and JavaScript so the quiz works without extra files
        html = html + style + script_tag
        return html
