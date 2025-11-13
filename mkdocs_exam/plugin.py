from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from mkdocs.exceptions import PluginError
from importlib import resources as impresources
from typing import Any
from . import css, js
import re
import yaml
import os
import html

# Read bundled CSS and JS and wrap them for inline injection
try:
    inp_file = impresources.files(css) / "exam.css"
    with inp_file.open("r", encoding="utf-8") as f:
        style = f.read()
    style = f'<style type="text/css">{style}</style>'

    js_file = impresources.files(js) / "exam.js"
    with js_file.open("r", encoding="utf-8") as f:
        script_content = f.read()
    script_tag = f'<script type="text/javascript" defer>{script_content}</script>'
except Exception as e:
    # Use a fallback if resources can't be loaded
    style = ""
    script_tag = ""
    import warnings
    warnings.warn(f"Failed to load mkdocs-exam resources: {e}")

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

logger = get_plugin_logger(__name__)

# Allowed exam types (whitelist for validation)
ALLOWED_EXAM_TYPES = {
    'choice', 'truefalse', 'short-answer', 'fill', 'essay', 'matching',
    'numeric', 'code-completion', 'ordering'  # New types we'll implement
}


def escape_html(text: str) -> str:
    """Escape HTML to prevent XSS attacks."""
    return html.escape(str(text), quote=True)


def interpolate_env_vars(value: Any) -> Any:
    """
    Recursively interpolate environment variables in strings.
    Supports formats: ${VAR}, ${VAR:-default}
    """
    if isinstance(value, str):
        # Match ${VAR} or ${VAR:-default}
        def replacer(match: re.Match) -> str:
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) else ""
            return os.environ.get(var_name, default_value)

        return re.sub(r"\$\{([^:}]+)(?::[-]?([^}]*))?\}", replacer, value)
    elif isinstance(value, dict):
        return {k: interpolate_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [interpolate_env_vars(item) for item in value]
    return value


class MkDocsExamPlugin(BasePlugin):  # type: ignore[type-arg]
    """Convert custom ``<exam>`` blocks into interactive HTML quizzes with full YAML support."""

    def __init__(self) -> None:
        """Initialize default state for the plugin."""
        self.enabled = True
        self.dirty = False

    def on_startup(self, *, command: str, dirty: bool) -> None:
        """Configure the plugin on startup."""
        self.dirty = dirty

    def _process_exam_data(self, exam_data: dict, exam_id: int, page_path: str) -> str:
        """
        Process a single exam data dictionary and return HTML.
        Supports environment variable interpolation and YAML anchors.
        """
        # Validate exam data
        if not isinstance(exam_data, dict):
            logger.warning(f"[{page_path}] Invalid exam data: expected dict, got {type(exam_data)}")
            return ""

        # Interpolate environment variables
        exam_data = interpolate_env_vars(exam_data)

        # Extract exam properties from YAML
        q_type = exam_data.get("type", "choice").lower()
        question = exam_data.get("question", "")

        # Validate exam type
        if q_type not in ALLOWED_EXAM_TYPES:
            logger.warning(f"[{page_path}] Exam #{exam_id}: Invalid type '{q_type}'. Using 'choice'.")
            q_type = "choice"

        if not question:
            logger.warning(f"[{page_path}] Exam #{exam_id}: Missing 'question' field")
            return ""

        # Extract optional fields
        hints = exam_data.get("hints", [])
        explanation = exam_data.get("explanation", "")
        show_explanation = exam_data.get("show-explanation", "on-correct")  # always, on-correct, on-wrong, never
        points = exam_data.get("points", 1)
        time_limit = exam_data.get("time-limit")  # seconds

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

        # Escape HTML in question for security
        html_question = escape_html(question)
        full_answers: list[str] = []

        # Process answers with feedback support
        answer_feedbacks: list[str] = []
        for ans in answer_correct + answer_list:
            if isinstance(ans, dict):
                # Answer with feedback: {value: "...", feedback: "..."}
                answer_feedbacks.append(ans.get("feedback", ""))
            else:
                answer_feedbacks.append("")

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
                # Escape answer text for security
                ans_escaped = escape_html(ans)
                feedback = escape_html(answer_feedbacks[i]) if i < len(answer_feedbacks) else ""
                feedback_attr = f' data-feedback="{feedback}"' if feedback else ""
                full_answers.append(
                    f'<div><input type="{input_type}" name="answer" value="{i}" id="{input_id}" {correct}{feedback_attr}>'
                    f'<label for="{input_id}">{ans_escaped}</label></div>'
                )
        elif q_type in {"short-answer", "fill", "essay"}:
            correct_vals = [escape_html(answers[i]) for i in correct_idx] or [escape_html(a) for a in answers]
            correct_attr = "|".join(correct_vals)
            if q_type == "essay":  # use textarea for long-form answers
                full_answers.append(
                    f'<div><textarea name="answer" rows="4" correct="{correct_attr}"></textarea></div>'
                )
            elif q_type == "fill":
                # Keep original question but escape the correct answer in attribute
                html_question = escape_html(question).replace(
                    "___", f'<input type="text" name="answer" correct="{correct_attr}">'
                )
            else:
                full_answers.append(f'<div><input type="text" name="answer" correct="{correct_attr}" ></div>')
        elif q_type == "matching":
            pairs = [ans.split("|") for ans in answers]
            left = [escape_html(p[0].strip()) for p in pairs]
            right = [escape_html(p[1].strip()) for p in pairs]
            options = "".join(f"<option>{r}</option>" for r in right)
            for i, left_item in enumerate(left):
                full_answers.append(
                    f"<div><label>{left_item} "
                    f'<select name="answer" correct="{right[i]}">{options}</select>'
                    "</label></div>"
                )
        elif q_type == "numeric":
            # New numeric range type
            tolerance = exam_data.get("tolerance", 0.01)
            correct_val = exam_data.get("answer-correct", [0])[0] if exam_data.get("answer-correct") else 0
            unit = exam_data.get("unit", "")
            full_answers.append(
                f'<div><input type="number" step="any" name="answer" '
                f'data-correct="{correct_val}" data-tolerance="{tolerance}" data-unit="{escape_html(unit)}">'
                f' {escape_html(unit)}</div>'
            )
        elif q_type == "code-completion":
            # New code completion type
            template = exam_data.get("template", "")
            language = exam_data.get("language", "python")
            blanks = exam_data.get("blanks", [])
            # Split template by ___ and create inputs
            parts = escape_html(template).split("___")
            code_html = parts[0]
            for i, part in enumerate(parts[1:]):
                blank_correct = "|".join([escape_html(str(c)) for c in blanks[i].get("correct", [])]) if i < len(blanks) else ""
                code_html += f'<input type="text" name="answer" correct="{blank_correct}" class="code-blank">'
                code_html += part
            full_answers.append(f'<div><pre><code class="language-{language}">{code_html}</code></pre></div>')
        elif q_type == "ordering":
            # New ordering type
            items = exam_data.get("items", [])
            correct_order = exam_data.get("correct-order", list(range(len(items))))
            items_html = ""
            for i, item in enumerate(items):
                items_html += f'<div class="ordering-item" data-index="{i}">{escape_html(str(item))}</div>'
            full_answers.append(f'<div class="ordering-container" data-correct-order="{",".join(map(str, correct_order))}">{items_html}</div>')

        html_answers = "".join(full_answers)
        content_html = "\n".join(content_lines)

        # Build hints HTML
        hints_html = ""
        if hints:
            hints_html = '<div class="exam-hints hidden">'
            for i, hint in enumerate(hints):
                if isinstance(hint, dict):
                    hint_text = escape_html(hint.get("text", ""))
                    hint_penalty = hint.get("penalty", 0)
                    hints_html += f'<div class="hint" data-penalty="{hint_penalty}"><button class="hint-button">Hint {i+1} (-{hint_penalty}%)</button><div class="hint-text hidden">{hint_text}</div></div>'
                else:
                    hint_text = escape_html(str(hint))
                    hints_html += f'<div class="hint"><button class="hint-button">Hint {i+1}</button><div class="hint-text hidden">{hint_text}</div></div>'
            hints_html += '</div>'

        # Build explanation HTML
        explanation_html = ""
        if explanation:
            explanation_escaped = escape_html(explanation)
            explanation_html = f'<div class="exam-explanation hidden" data-show="{show_explanation}">{explanation_escaped}</div>'

        # Build rich media HTML
        media_html = ""
        if "media" in exam_data:
            media = exam_data["media"]
            media_type = media.get("type", "image")
            media_src = escape_html(media.get("src", ""))
            media_alt = escape_html(media.get("alt", ""))
            media_caption = escape_html(media.get("caption", ""))

            if media_type == "image":
                media_html = f'<figure class="exam-media"><img src="{media_src}" alt="{media_alt}"><figcaption>{media_caption}</figcaption></figure>'
            elif media_type == "video":
                media_html = f'<figure class="exam-media"><video controls src="{media_src}"></video><figcaption>{media_caption}</figcaption></figure>'
            elif media_type == "audio":
                media_html = f'<figure class="exam-media"><audio controls src="{media_src}"></audio><figcaption>{media_caption}</figcaption></figure>'

        # Build data attributes
        data_attrs = f'data-type="{q_type}" data-points="{points}"'
        if time_limit:
            data_attrs += f' data-time-limit="{time_limit}"'

        exam_html = (
            f'<div class="exam" {data_attrs}>'
            f'{media_html}'
            f'<h3>{html_question}</h3>'
            f'{hints_html}'
            f'<form><fieldset>'
            f"{html_answers}</fieldset>"
            '<button type="submit" class="exam-button">Submit</button>'
            f'</form>'
            f'{explanation_html}'
            f'<section class="content hidden">{content_html}</section>'
            f'</div>'
        )
        return exam_html

    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files: Files | None = None, **kwargs: Any) -> str:
        """
        Parse exam blocks in markdown and generate HTML quizzes.
        Supports:
        - Both ```exam and ```yaml codeblocks
        - Multi-document YAML (multiple exams separated by ---)
        - Environment variable interpolation (${VAR} or ${VAR:-default})
        - YAML anchors and aliases
        - Full markdown support in all string fields
        """
        if "exam" in page.meta and page.meta["exam"] == "disable":
            return markdown

        page_path = page.file.src_path if hasattr(page, "file") and page.file else "unknown"

        # Look for ```exam or ```yaml codeblocks
        REGEX = r"```(?:exam|yaml)\s*\n(.*?)```"
        matches = re.findall(REGEX, markdown, re.DOTALL)
        exam_id = 0

        for match in matches:
            # Try to parse YAML content (supports multi-document YAML)
            try:
                # yaml.safe_load_all returns a generator for multi-document YAML
                docs = list(yaml.safe_load_all(match))

                # Filter out None documents (empty sections)
                docs = [doc for doc in docs if doc is not None]

                if not docs:
                    logger.warning(f"[{page_path}] Empty YAML block detected, skipping")
                    continue

                # Process each document (exam)
                exam_htmls = []
                for doc in docs:
                    exam_html = self._process_exam_data(doc, exam_id, page_path)
                    if exam_html:
                        exam_htmls.append(exam_html)
                        exam_id += 1

                # Join all exams with newlines
                combined_html = "\n".join(exam_htmls)

                # Replace the original block with the generated HTML
                old_exam_pattern = re.escape(f"```yaml\n{match}```")
                if re.search(old_exam_pattern, markdown):
                    markdown = re.sub(old_exam_pattern, combined_html, markdown, count=1)
                else:
                    # Try with ```exam
                    old_exam_pattern = re.escape(f"```exam\n{match}```")
                    markdown = re.sub(old_exam_pattern, combined_html, markdown, count=1)

            except yaml.YAMLError as e:
                error_msg = f"YAML parsing error in {page_path}: {str(e)}"
                logger.error(error_msg)
                raise PluginError(error_msg) from e
            except Exception as e:
                error_msg = f"Unexpected error processing exam in {page_path}: {str(e)}"
                logger.error(error_msg)
                raise PluginError(error_msg) from e

        return markdown

    def on_page_content(self, html: str, page: Page, config: MkDocsConfig, files: Files, **kwargs: Any) -> str:
        """Append inline resources to the rendered HTML page."""
        # Inject CSS and JavaScript so the quiz works without extra files
        html = html + style + script_tag
        return html

    def on_build_error(self, error: Exception, **kwargs: Any) -> None:
        """
        Handle build errors gracefully.
        This event is called when an error occurs during the build process.
        """
        # Log the error for debugging
        logger.debug(f"Build error encountered: {error}")
        # Allow error to propagate - we don't suppress it
        return None
