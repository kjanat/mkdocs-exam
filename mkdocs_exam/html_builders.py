"""HTML generation helpers for mkdocs-exam plugin."""

import html
from typing import Any


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


def build_explanation_html(explanation: str, show_explanation: str = "on-correct") -> str:
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


def build_exam_wrapper(  # noqa: PLR0913, PLR0917
    question: str,
    exam_type: str,
    points: int,
    time_limit: int | None,
    media_html: str,
    hints_html: str,
    answers_html: str,
    explanation_html: str,
    content_html: str,
) -> str:
    """Build complete exam HTML wrapper.

    Args:
        question: Exam question (already escaped)
        exam_type: Type of exam (choice, truefalse, etc.)
        points: Point value
        time_limit: Optional time limit in seconds
        media_html: Pre-built media HTML
        hints_html: Pre-built hints HTML
        answers_html: Pre-built answers HTML
        explanation_html: Pre-built explanation HTML
        content_html: Additional content HTML

    Returns:
        Complete exam HTML

    """
    data_attrs = f'data-type="{exam_type}" data-points="{points}"'
    if time_limit:
        data_attrs += f' data-time-limit="{time_limit}"'

    return (
        f'<div class="exam" {data_attrs}>'
        f"{media_html}"
        f"<h3>{question}</h3>"
        f"{hints_html}"
        f"<form><fieldset>"
        f"{answers_html}</fieldset>"
        '<button type="submit" class="exam-button">Submit</button>'
        f"</form>"
        f"{explanation_html}"
        f'<section class="content hidden">{content_html}</section>'
        f"</div>"
    )
