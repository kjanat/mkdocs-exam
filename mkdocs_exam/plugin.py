"""MkDocs Exam Plugin - Create interactive training exams in markdown."""

import os
import re
from importlib import resources as impresources
from typing import Any, TypeVar, overload

import yaml
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from . import css, js
from .exam_config import AnswerConfig, ExamMetadata, ExamPluginConfig
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

# Initialize logger early for error reporting
logger = get_plugin_logger(__name__)

# Processor registry mapping exam types to their handlers
# Handlers return tuple of (answers_html, final_question)
PROCESSOR_REGISTRY: dict[str, Any] = {
    "choice": lambda config: (
        process_choice_truefalse_answers(config),
        config.question,
    ),
    "truefalse": lambda config: (
        process_choice_truefalse_answers(config),
        config.question,
    ),
    "short-answer": process_short_answer_fill_essay_answers,
    "fill": process_short_answer_fill_essay_answers,
    "essay": process_short_answer_fill_essay_answers,
    "matching": lambda config: (process_matching_answers(config), config.question),
    "numeric": lambda config: (process_numeric_answers(config), config.question),
    "code-completion": lambda config: (
        process_code_completion_answers(config),
        config.question,
    ),
    "ordering": lambda config: (process_ordering_answers(config), config.question),
    "categorization": lambda config: (
        process_categorization_answers(config),
        config.question,
    ),
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
    # Critical error: plugin cannot function without resources
    logger.exception("Failed to load mkdocs-exam CSS/JS resources")
    raise PluginError(  # noqa: TRY003
        f"Failed to load required plugin resources. "
        f"This indicates an installation problem. Error: {e}"
    ) from e

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

T = TypeVar("T")


@overload
def interpolate_env_vars(value: str) -> str: ...


@overload
def interpolate_env_vars(value: dict[str, T]) -> dict[str, Any]: ...  # noqa: UP047


@overload
def interpolate_env_vars(value: list[T]) -> list[Any]: ...  # noqa: UP047


@overload
def interpolate_env_vars(value: T) -> T: ...  # noqa: UP047


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


class MkDocsExamPlugin(BasePlugin[ExamPluginConfig]):
    """Convert custom ``<exam>`` blocks into interactive HTML quizzes with full YAML support."""

    def __init__(self) -> None:
        """Initialize plugin state."""
        super().__init__()
        self.dirty = False
        self.total_exams_processed = 0

    def on_startup(self, *, command: str, dirty: bool) -> None:
        """Configure the plugin on startup."""
        self.dirty = dirty

    def _get_strict_validation(self) -> bool:
        """Get strict_validation config with fallback for backward compatibility.

        Returns:
            False by default (graceful fallback), True if strict_validation is enabled

        """
        return getattr(self.config, "strict_validation", False)

    def on_config(self, config: MkDocsConfig, **kwargs: Any) -> MkDocsConfig:
        """Validate plugin configuration and MkDocs config compatibility.

        This event is called once after config is loaded, before any build process.
        Perfect for validating configuration and failing fast.
        """
        # Check theme compatibility (warning only, not blocking)
        if config.theme.name not in {"material", "readthedocs", "mkdocs"}:
            logger.warning(
                f"mkdocs-exam is optimized for Material, ReadTheDocs, or MkDocs theme. "
                f"Current theme '{config.theme.name}' may have styling issues."
            )

        # Validate default_points is positive
        default_points = getattr(self.config, "default_points", 1)
        if default_points < 1:
            raise PluginError("default_points must be at least 1")  # noqa: TRY003

        # Validate default_type is in allowed list
        default_type = getattr(self.config, "default_type", "choice")
        if default_type not in ALLOWED_EXAM_TYPES:
            raise PluginError(  # noqa: TRY003
                f"Invalid default_type '{default_type}'. "
                f"Must be one of: {', '.join(sorted(ALLOWED_EXAM_TYPES))}"
            )

        return config

    def _process_exam_data(self, exam_data: dict, exam_id: int, page_path: str) -> str:
        """Process a single exam data dictionary and return HTML.

        Supports environment variable interpolation and YAML anchors.
        """
        # Validate exam data
        if not isinstance(exam_data, dict):
            error_msg = (
                f"[{page_path}] Invalid exam data: expected dict, got {type(exam_data)}"
            )

            if self._get_strict_validation():
                raise PluginError(error_msg)
            else:
                logger.warning(error_msg)
                return ""

        # Interpolate environment variables
        exam_data = interpolate_env_vars(exam_data)

        # Extract and validate exam properties
        q_type = exam_data.get("type", "choice").lower()
        question = exam_data.get("question", "")

        if q_type not in ALLOWED_EXAM_TYPES:
            error_msg = f"[{page_path}] Exam #{exam_id}: Invalid type '{q_type}'"

            if self._get_strict_validation():
                raise PluginError(  # noqa: TRY003
                    f"{error_msg}. Must be one of: {', '.join(sorted(ALLOWED_EXAM_TYPES))}"
                )
            else:
                logger.warning(f"{error_msg}. Using 'choice'.")
                q_type = "choice"

        if not question:
            error_msg = f"[{page_path}] Exam #{exam_id}: Missing 'question' field"

            if self._get_strict_validation():
                raise PluginError(error_msg)
            else:
                logger.warning(error_msg)
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
        answers, correct_idx, answer_feedbacks, answer_weights = self._parse_answers(
            exam_data
        )

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
        media_html = (
            build_media_html(exam_data["media"]) if "media" in exam_data else ""
        )

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

    def _parse_answers(
        self, exam_data: dict
    ) -> tuple[list[str], list[int], list[str], list[float]]:
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

    def _extract_exam_blocks(self, markdown: str) -> list[tuple[str, str, str]]:
        r"""Extract exam/yaml code blocks from markdown, handling nested blocks.

        Returns:
            List of tuples: (fence_type, content, full_block)
            - fence_type: "yaml" or "exam"
            - content: the YAML content inside the block
            - full_block: the complete ```yaml\n...\n``` block

        """
        blocks = []
        lines = markdown.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this line starts an exam or yaml block
            if line.startswith("```yaml") or line.startswith("```exam"):
                fence_type = "yaml" if line.startswith("```yaml") else "exam"
                start_index = i
                i += 1
                content_lines = []

                # Collect all lines until we find the closing fence
                # A closing fence is ``` at the start of a line
                while i < len(lines):
                    if lines[i].startswith("```") and lines[i].strip() == "```":
                        # Found the closing fence
                        content = "\n".join(content_lines)
                        full_block = "\n".join(lines[start_index : i + 1])
                        blocks.append((fence_type, content, full_block))
                        break
                    else:
                        content_lines.append(lines[i])
                    i += 1

            i += 1

        return blocks

    def on_page_markdown(
        self,
        markdown: str,
        page: Page,
        config: MkDocsConfig,
        files: Files | None = None,
        **kwargs: Any,
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

        page_path = (
            page.file.src_path if hasattr(page, "file") and page.file else "unknown"
        )

        # Extract exam/yaml blocks (handles nested code blocks properly)
        blocks = self._extract_exam_blocks(markdown)
        exam_id = 0

        for fence_type, content, full_block in blocks:
            # Try to parse YAML content (supports multi-document YAML)
            try:
                # yaml.safe_load_all returns a generator for multi-document YAML
                docs = list(yaml.safe_load_all(content))

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
                        self.total_exams_processed += 1

                # Join all exams with newlines
                combined_html = "\n".join(exam_htmls)

                # Replace the original block with the generated HTML
                # Use full_block which includes the complete fence markers
                markdown = markdown.replace(full_block, combined_html, 1)

            except yaml.YAMLError as e:
                error_msg = f"YAML parsing error in {page_path}: {e!s}"
                logger.exception(error_msg)
                raise PluginError(error_msg) from e
            except Exception as e:
                error_msg = f"Unexpected error processing exam in {page_path}: {e!s}"
                logger.exception(error_msg)
                raise PluginError(error_msg) from e

        return markdown

    def on_page_content(
        self, html: str, page: Page, config: MkDocsConfig, files: Files, **kwargs: Any
    ) -> str:
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

    def on_shutdown(self, **kwargs: Any) -> None:
        """Clean up resources and log build summary when MkDocs shuts down.

        Called once at the end of the build, useful for cleanup and statistics.
        """
        # Log summary statistics
        if self.total_exams_processed > 0:
            logger.info(f"Processed {self.total_exams_processed} exam(s) total")
