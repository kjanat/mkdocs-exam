"""HTML generation helpers for mkdocs-exam plugin."""

import html
from typing import Any

from .exam_config import ExamMetadata


def escape_html(text: str) -> str:
    """Escape HTML to prevent XSS attacks."""
    return html.escape(str(text), quote=True)


def build_hints_html(hints: list[Any]) -> str:
    """Build HTML for exam hints section.

    Args:
        hints: List of hints (strings or dicts with text/penalty)

    Returns:
        HTML string for hints section

    """
    if not hints:
        return ""

    hints_html = '<div class="exam-hints hidden">'
    for i, hint in enumerate(hints):
        if isinstance(hint, dict):
            hint_text = escape_html(hint.get("text", ""))
            hint_penalty = hint.get("penalty", 0)
            hints_html += f'<div class="hint" data-penalty="{hint_penalty}"><button class="hint-button">Hint {i + 1} (-{hint_penalty}%)</button><div class="hint-text hidden">{hint_text}</div></div>'
        else:
            hint_text = escape_html(str(hint))
            hints_html += f'<div class="hint"><button class="hint-button">Hint {i + 1}</button><div class="hint-text hidden">{hint_text}</div></div>'
    hints_html += "</div>"
    return hints_html


def build_explanation_html(
    explanation: str, show_explanation: str = "on-correct"
) -> str:
    """Build HTML for exam explanation section.

    Args:
        explanation: Explanation text
        show_explanation: When to show (always, on-correct, on-wrong, never)

    Returns:
        HTML string for explanation section

    """
    if not explanation:
        return ""

    explanation_escaped = escape_html(explanation)
    return f'<div class="exam-explanation hidden" data-show="{show_explanation}">{explanation_escaped}</div>'


def build_media_html(media: dict[str, Any]) -> str:
    """Build HTML for rich media (image, video, audio).

    Args:
        media: Media configuration dict with type, src, alt, caption

    Returns:
        HTML string for media element

    """
    media_type = media.get("type", "image")
    media_src = escape_html(media.get("src", ""))
    media_alt = escape_html(media.get("alt", ""))
    media_caption = escape_html(media.get("caption", ""))

    if media_type == "image":
        return f'<figure class="exam-media"><img src="{media_src}" alt="{media_alt}"><figcaption>{media_caption}</figcaption></figure>'
    elif media_type == "video":
        return f'<figure class="exam-media"><video controls src="{media_src}"></video><figcaption>{media_caption}</figcaption></figure>'
    elif media_type == "audio":
        return f'<figure class="exam-media"><audio controls src="{media_src}"></audio><figcaption>{media_caption}</figcaption></figure>'
    return ""


def build_exam_wrapper(metadata: ExamMetadata) -> str:
    """Build complete exam HTML wrapper.

    Args:
        metadata: Exam metadata configuration

    Returns:
        Complete exam HTML

    """
    data_attrs = f'data-type="{metadata.exam_type}" data-points="{metadata.points}"'
    if metadata.time_limit:
        data_attrs += f' data-time-limit="{metadata.time_limit}"'

    return (
        f'<div class="exam" {data_attrs}>'
        f"{metadata.media_html}"
        f"<h3>{metadata.question}</h3>"
        f"{metadata.hints_html}"
        f"<form><fieldset>"
        f"{metadata.answers_html}</fieldset>"
        '<button type="submit" class="exam-button">Submit</button>'
        f"</form>"
        f"{metadata.explanation_html}"
        f'<section class="content hidden">{metadata.content_html}</section>'
        f"</div>"
    )
