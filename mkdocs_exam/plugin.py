"""MkDocs plugin for creating interactive exam blocks."""

import logging
from importlib import resources as impresources
from typing import Any

from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from . import css, js
from .constants import CSSClasses, DefaultConfig, ExamTags
from .html_builder import build_exam_html
from .parser import ExamParseError, find_exam_blocks, parse_exam_block, replace_exam_blocks

logger = logging.getLogger("mkdocs.plugins.mkdocs-exam")

# Read bundled CSS and JS and wrap them for inline injection
inp_file = impresources.files(css) / "exam.css"
with inp_file.open("r", encoding="utf-8") as f:
    style_content = f.read()
style_tag = f'<style type="text/css">{style_content}</style>'

js_file = impresources.files(js) / "exam.js"
with js_file.open("r", encoding="utf-8") as f:
    script_content = f.read()
script_tag = f'<script type="text/javascript" defer>{script_content}</script>'


class MkDocsExamPlugin(BasePlugin):  # type: ignore[type-arg]
    """Convert custom ``<exam>`` blocks into interactive HTML quizzes."""

    config_scheme = (
        ("submit_text", config_options.Type(str, default=DefaultConfig.SUBMIT_TEXT)),
        ("reset_text", config_options.Type(str, default=DefaultConfig.RESET_TEXT)),
        ("show_score", config_options.Type(bool, default=DefaultConfig.SHOW_SCORE)),
        ("allow_retry", config_options.Type(bool, default=DefaultConfig.ALLOW_RETRY)),
        ("essay_rows", config_options.Type(int, default=DefaultConfig.ESSAY_ROWS)),
    )

    def __init__(self) -> None:
        """Initialize default state for the plugin."""
        super().__init__()
        self.enabled: bool = True
        self.dirty: bool = False

    def on_startup(self, *, command: str, dirty: bool) -> None:
        """Configure the plugin on startup."""
        self.dirty = dirty
        logger.info("MkDocs Exam Plugin initialized")

    def on_page_markdown(
        self,
        markdown: str,
        page: Page,
        config: MkDocsConfig,
        files: Files | None = None,
    ) -> str:
        """
        Parse exam blocks in markdown and generate the HTML quiz.

        Args:
            markdown: Page markdown content.
            page: Current page object.
            config: MkDocs configuration.
            files: All files in the site.

        Returns:
            Markdown with exam blocks replaced by HTML.
        """
        # Check if exams are disabled for this page
        if "exam" in page.meta and page.meta["exam"] == "disable":
            logger.debug(f"Exams disabled for page: {page.file.src_path}")
            return markdown

        # Find all exam blocks
        exam_blocks = find_exam_blocks(markdown)
        if not exam_blocks:
            return markdown

        logger.info(f"Found {len(exam_blocks)} exam block(s) in {page.file.src_path}")

        # Parse and convert each exam block
        replacements: dict[str, str] = {}
        exam_id = 0

        for block_content in exam_blocks:
            try:
                # Parse the exam block
                exam_data = parse_exam_block(block_content, exam_id)

                # Build HTML from parsed data
                exam_html = build_exam_html(exam_data, self.config)

                # Store replacement mapping
                original_block = ExamTags.START + block_content + ExamTags.END
                replacements[original_block] = exam_html

                exam_id += 1

            except ExamParseError as e:
                # Log error and leave block unchanged
                logger.error(f"Failed to parse exam block in {page.file.src_path}: {e}")
                # Optionally, insert error message in place of exam
                error_html = (
                    f'<div class="admonition error">'
                    f'<p class="admonition-title">Exam Parse Error</p>'
                    f'<p>{e}</p>'
                    f'</div>'
                )
                original_block = ExamTags.START + block_content + ExamTags.END
                replacements[original_block] = error_html

        # Replace all exam blocks with HTML
        markdown = replace_exam_blocks(markdown, replacements)
        return markdown

    def on_page_content(
        self,
        html: str,
        *,
        page: Page,
        config: MkDocsConfig,
        files: Files,
    ) -> str | None:
        """
        Append inline resources to the rendered HTML page.

        Only inject CSS and JavaScript if the page contains exams.

        Args:
            html: Rendered HTML content.
            page: Current page object.
            config: MkDocs configuration.
            files: All files in the site.

        Returns:
            HTML with CSS/JS injected if exams are present.
        """
        # Only inject if page has exams (performance optimization)
        if f'class="{CSSClasses.EXAM}"' not in html:
            return html

        # Inject CSS and JavaScript for quiz functionality
        html = html + style_tag + script_tag
        logger.debug(f"Injected exam resources into {page.file.src_path}")
        return html
