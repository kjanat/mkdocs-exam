"""MkDocs Exam Plugin - Create interactive training exams in markdown."""

import os
import re
from importlib import resources as impresources
from typing import Any

import yaml
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from . import css, js
from .exam_config import AnswerConfig, ExamMetadata
from .html_builders import (
    build_exam_wrapper,
    build_explanation_html,
    build_hints_html,
    build_media_html,
    escape_html,
)
from .processors import (
    process_categorization_answers,
    process_choice_truefalse_answers,
    process_code_completion_answers,
    process_hotspot_answers,
    process_matching_answers,
    process_numeric_answers,
    process_ordering_answers,
    process_short_answer_fill_essay_answers,
)

# Processor registry mapping exam types to their handlers
# Handlers return tuple of (answers_html, final_question)
PROCESSOR_REGISTRY: dict[str, Any] = {
    "choice": lambda config: (process_choice_truefalse_answers(config), config.question),
    "truefalse": lambda config: (process_choice_truefalse_answers(config), config.question),
    "short-answer": process_short_answer_fill_essay_answers,
    "fill": process_short_answer_fill_essay_answers,
    "essay": process_short_answer_fill_essay_answers,
    "matching": lambda config: (process_matching_answers(config), config.question),
    "numeric": lambda config: (process_numeric_answers(config), config.question),
    "code-completion": lambda config: (process_code_completion_answers(config), config.question),
    "ordering": lambda config: (process_ordering_answers(config), config.question),
    "categorization": lambda config: (process_categorization_answers(config), config.question),
    "hotspot": lambda config: (process_hotspot_answers(config), config.question),
}

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
    "choice",
    "truefalse",
    "short-answer",
    "fill",
    "essay",
    "matching",
    "numeric",
    "code-completion",
    "ordering",
    "categorization",  # Drag items into categories
    "hotspot",  # Click regions on images
}


def interpolate_env_vars(value: Any) -> Any:
    """Recursively interpolate environment variables in strings.

    Supports formats: ${VAR}, ${VAR:-default}.
    """
    if isinstance(value, str):
        # Match ${VAR} or ${VAR:-default}
        def replacer(match: re.Match) -> str:
            var_name = match.group(1)
            default_value = match.group(2) or ""
            return os.environ.get(var_name, default_value)

        return re.sub(r"\$\{([^:}]+)(?::[-]?([^}]*))?\}", replacer, value)
    elif isinstance(value, dict):
        return {k: interpolate_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [interpolate_env_vars(item) for item in value]
    return value


class MkDocsExamPlugin(BasePlugin):  # type: ignore[type-arg]
    """Convert custom ``<exam>`` blocks into interactive HTML quizzes with full YAML support."""

    config_scheme = (
        ("enabled", config_options.Type(bool, default=True)),
        ("default_type", config_options.Type(str, default="choice")),
        ("default_points", config_options.Type(int, default=1)),
        ("show_answers", config_options.Type(bool, default=False)),
        ("randomize_answers", config_options.Type(bool, default=False)),
        ("theme", config_options.Type(str, default="default")),
    )

    def __init__(self) -> None:
        """Initialize default state for the plugin."""
        self.enabled = True
        self.dirty = False

    def on_startup(self, *, command: str, dirty: bool) -> None:
        """Configure the plugin on startup."""
        self.dirty = dirty

    def _process_exam_data(self, exam_data: dict, exam_id: int, page_path: str) -> str:
        """Process a single exam data dictionary and return HTML.

        Supports environment variable interpolation and YAML anchors.
        """
        # Validate exam data
        if not isinstance(exam_data, dict):
            logger.warning(f"[{page_path}] Invalid exam data: expected dict, got {type(exam_data)}")
            return ""

        # Interpolate environment variables
        exam_data = interpolate_env_vars(exam_data)

        # Extract and validate exam properties
        q_type = exam_data.get("type", "choice").lower()
        question = exam_data.get("question", "")

        if q_type not in ALLOWED_EXAM_TYPES:
            logger.warning(f"[{page_path}] Exam #{exam_id}: Invalid type '{q_type}'. Using 'choice'.")
            q_type = "choice"

        if not question:
            logger.warning(f"[{page_path}] Exam #{exam_id}: Missing 'question' field")
            return ""

        # Extract optional fields
        hints = exam_data.get("hints", [])
        explanation = exam_data.get("explanation", "")
        show_explanation = exam_data.get("show-explanation", "on-correct")
        points = exam_data.get("points", 1)
        time_limit = exam_data.get("time-limit")
        partial_credit = exam_data.get("partial-credit", False)
        content_lines = exam_data.get("content", "").strip().splitlines()

        # Process answers and extract correct indices
        answers, correct_idx, answer_feedbacks, answer_weights = self._parse_answers(exam_data)

        # Generate answers HTML based on exam type
        html_question = escape_html(question)
        config = AnswerConfig(
            exam_type=q_type,
            answers=answers,
            correct_idx=correct_idx,
            answer_feedbacks=answer_feedbacks,
            answer_weights=answer_weights,
            exam_id=exam_id,
            partial_credit=partial_credit,
            exam_data=exam_data,
            question=html_question,
        )

        full_answers, final_question = self._generate_answers_html(config)

        # Build component HTML sections
        html_answers = "".join(full_answers)
        content_html = "\n".join(content_lines)
        hints_html = build_hints_html(hints)
        explanation_html = build_explanation_html(explanation, show_explanation)
        media_html = build_media_html(exam_data["media"]) if "media" in exam_data else ""

        # Build and return complete exam HTML
        metadata = ExamMetadata(
            question=final_question,
            exam_type=q_type,
            points=points,
            time_limit=time_limit,
            media_html=media_html,
            hints_html=hints_html,
            answers_html=html_answers,
            explanation_html=explanation_html,
            content_html=content_html,
        )

        return build_exam_wrapper(metadata)

    def _parse_answers(self, exam_data: dict) -> tuple[list[str], list[int], list[str], list[float]]:
        """Parse and extract answer data from exam configuration.

        Args:
            exam_data: Full exam data dictionary

        Returns:
            Tuple of (answers, correct_idx, answer_feedbacks, answer_weights)

        """
        answers: list[str] = []
        correct_idx: list[int] = []
        answer_feedbacks: list[str] = []
        answer_weights: list[float] = []

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

        answers.extend(str(ans) for ans in answer_list)

        # Process answers with feedback and weight support
        for ans in answer_correct + answer_list:
            if isinstance(ans, dict):
                answer_feedbacks.append(ans.get("feedback", ""))
                answer_weights.append(ans.get("weight", 1.0))
            else:
                answer_feedbacks.append("")
                answer_weights.append(1.0)

        return answers, correct_idx, answer_feedbacks, answer_weights

    def _generate_answers_html(self, config: AnswerConfig) -> tuple[list[str], str]:
        """Generate HTML for exam answers based on type.

        Args:
            config: Answer configuration

        Returns:
            Tuple of (list of HTML strings for answers, final question text)

        """
        processor = PROCESSOR_REGISTRY.get(config.exam_type)
        if processor:
            return processor(config)

        # Fallback for unknown exam types
        return [], config.question

    def on_page_markdown(
        self, markdown: str, page: Page, config: MkDocsConfig, files: Files | None = None, **kwargs: Any
    ) -> str:
        """Parse exam blocks in markdown and generate HTML quizzes.

        Supports:
        - Both ```exam and ```yaml codeblocks
        - Multi-document YAML (multiple exams separated by ---)
        - Environment variable interpolation (${VAR} or ${VAR:-default})
        - YAML anchors and aliases
        - Full markdown support in all string fields.
        """
        if "exam" in page.meta and page.meta["exam"] == "disable":
            return markdown

        page_path = page.file.src_path if hasattr(page, "file") and page.file else "unknown"

        # Look for ```exam or ```yaml codeblocks
        regex = r"```(?:exam|yaml)\s*\n(.*?)```"
        matches = re.findall(regex, markdown, re.DOTALL)
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
                error_msg = f"YAML parsing error in {page_path}: {e!s}"
                logger.exception(error_msg)
                raise PluginError(error_msg) from e
            except Exception as e:
                error_msg = f"Unexpected error processing exam in {page_path}: {e!s}"
                logger.exception(error_msg)
                raise PluginError(error_msg) from e

        return markdown

    def on_page_content(self, html: str, page: Page, config: MkDocsConfig, files: Files, **kwargs: Any) -> str:
        """Append inline resources to the rendered HTML page."""
        # Inject CSS and JavaScript so the quiz works without extra files
        html = html + style + script_tag
        return html

    def on_build_error(self, error: Exception, **kwargs: Any) -> None:
        """Handle build errors gracefully.

        This event is called when an error occurs during the build process.
        """
        # Log the error for debugging
        logger.debug(f"Build error encountered: {error}")
        # Allow error to propagate - we don't suppress it
