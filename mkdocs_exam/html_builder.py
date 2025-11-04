"""HTML generation for exam blocks."""

import html
from typing import Any

from .constants import CSSClasses, DefaultConfig, QuestionTypes
from .parser import ExamData


def escape(text: str) -> str:
    """
    Escape HTML to prevent XSS attacks.

    Args:
        text: Text to escape.

    Returns:
        HTML-escaped text.
    """
    return html.escape(text, quote=True)


def build_choice_inputs(
    exam_data: ExamData, config: dict[str, Any] | None = None
) -> tuple[str, list[str]]:
    """
    Build HTML for choice/true-false questions.

    Args:
        exam_data: Parsed exam data.
        config: Plugin configuration.

    Returns:
        Tuple of (question_html, list of answer HTML strings).
    """
    question_html = escape(exam_data.question)
    answer_htmls: list[str] = []

    # Determine if we need checkboxes (multiple correct) or radio buttons
    as_checkboxes = len(exam_data.correct_indices) > 1
    input_type = "checkbox" if as_checkboxes else "radio"

    for i, answer in enumerate(exam_data.answers):
        is_correct = i in exam_data.correct_indices
        input_id = f"exam-{exam_data.exam_id}-{i}"
        correct_attr = CSSClasses.CORRECT if is_correct else ""
        escaped_answer = escape(answer)

        answer_html = (
            f'<div>'
            f'<input type="{input_type}" name="answer" value="{i}" '
            f'id="{input_id}" {correct_attr} aria-describedby="{input_id}-label">'
            f'<label for="{input_id}" id="{input_id}-label">{escaped_answer}</label>'
            f'</div>'
        )
        answer_htmls.append(answer_html)

    return question_html, answer_htmls


def build_text_input(exam_data: ExamData, config: dict[str, Any] | None = None) -> tuple[str, list[str]]:
    """
    Build HTML for short-answer questions.

    Args:
        exam_data: Parsed exam data.
        config: Plugin configuration.

    Returns:
        Tuple of (question_html, list of answer HTML strings).
    """
    question_html = escape(exam_data.question)
    correct_vals = [exam_data.answers[i] for i in exam_data.correct_indices] or exam_data.answers
    # Escape each correct value individually
    correct_attr = "|".join(escape(val) for val in correct_vals)

    answer_html = (
        f'<div>'
        f'<input type="text" name="answer" correct="{correct_attr}" '
        f'aria-label="{escape(exam_data.question)}">'
        f'</div>'
    )

    return question_html, [answer_html]


def build_fill_input(exam_data: ExamData, config: dict[str, Any] | None = None) -> tuple[str, list[str]]:
    """
    Build HTML for fill-in-the-blank questions.

    Args:
        exam_data: Parsed exam data.
        config: Plugin configuration.

    Returns:
        Tuple of (question_html, list of answer HTML strings).
    """
    correct_vals = [exam_data.answers[i] for i in exam_data.correct_indices] or exam_data.answers
    # Escape each correct value individually
    correct_attr = "|".join(escape(val) for val in correct_vals)

    fill_placeholder = DefaultConfig.FILL_PLACEHOLDER
    input_html = f'<input type="text" name="answer" correct="{correct_attr}" aria-label="Fill in the blank">'

    # Replace placeholder with input, but escape the rest of the question
    # Split by placeholder, escape each part, then rejoin with input
    parts = exam_data.question.split(fill_placeholder)
    escaped_parts = [escape(part) for part in parts]
    question_html = input_html.join(escaped_parts)

    return question_html, []


def build_essay_input(exam_data: ExamData, config: dict[str, Any] | None = None) -> tuple[str, list[str]]:
    """
    Build HTML for essay questions.

    Args:
        exam_data: Parsed exam data.
        config: Plugin configuration.

    Returns:
        Tuple of (question_html, list of answer HTML strings).
    """
    question_html = escape(exam_data.question)
    correct_vals = [exam_data.answers[i] for i in exam_data.correct_indices] or exam_data.answers
    # Escape each correct value individually
    correct_attr = "|".join(escape(val) for val in correct_vals)

    rows = DefaultConfig.ESSAY_ROWS
    if config:
        rows = config.get("essay_rows", rows)

    answer_html = (
        f'<div>'
        f'<textarea name="answer" rows="{rows}" correct="{correct_attr}" '
        f'aria-label="{escape(exam_data.question)}"></textarea>'
        f'</div>'
    )

    return question_html, [answer_html]


def build_matching_inputs(
    exam_data: ExamData, config: dict[str, Any] | None = None
) -> tuple[str, list[str]]:
    """
    Build HTML for matching questions.

    Args:
        exam_data: Parsed exam data.
        config: Plugin configuration.

    Returns:
        Tuple of (question_html, list of answer HTML strings).
    """
    question_html = escape(exam_data.question)
    answer_htmls: list[str] = []

    # Parse pairs
    pairs = [ans.split("|") for ans in exam_data.answers]
    left = [escape(p[0].strip()) for p in pairs]
    right = [escape(p[1].strip()) for p in pairs]

    # Build option list (already escaped)
    options = "".join(f"<option>{r}</option>" for r in right)

    for i, left_item in enumerate(left):
        select_id = f"exam-{exam_data.exam_id}-match-{i}"
        # right[i] is already escaped from above
        answer_html = (
            f"<div>"
            f'<label for="{select_id}">{left_item} '
            f'<select name="answer" id="{select_id}" correct="{right[i]}" '
            f'aria-label="Match {left_item}">'
            f"{options}"
            f"</select>"
            f"</label>"
            f"</div>"
        )
        answer_htmls.append(answer_html)

    return question_html, answer_htmls


def build_exam_html(exam_data: ExamData, config: dict[str, Any] | None = None) -> str:
    """
    Build complete HTML for an exam block.

    Args:
        exam_data: Parsed exam data.
        config: Plugin configuration.

    Returns:
        Complete HTML for the exam.
    """
    # Get configuration values
    submit_text = DefaultConfig.SUBMIT_TEXT
    reset_text = DefaultConfig.RESET_TEXT
    show_score = DefaultConfig.SHOW_SCORE
    allow_retry = DefaultConfig.ALLOW_RETRY

    if config:
        submit_text = config.get("submit_text", submit_text)
        reset_text = config.get("reset_text", reset_text)
        show_score = config.get("show_score", show_score)
        allow_retry = config.get("allow_retry", allow_retry)

    # Build question and answers based on type
    if exam_data.question_type in {QuestionTypes.CHOICE, QuestionTypes.TRUEFALSE}:
        question_html, answer_htmls = build_choice_inputs(exam_data, config)
    elif exam_data.question_type == QuestionTypes.SHORT_ANSWER:
        question_html, answer_htmls = build_text_input(exam_data, config)
    elif exam_data.question_type == QuestionTypes.FILL:
        question_html, answer_htmls = build_fill_input(exam_data, config)
    elif exam_data.question_type == QuestionTypes.ESSAY:
        question_html, answer_htmls = build_essay_input(exam_data, config)
    elif exam_data.question_type == QuestionTypes.MATCHING:
        question_html, answer_htmls = build_matching_inputs(exam_data, config)
    else:
        # Fallback to text input
        question_html, answer_htmls = build_text_input(exam_data, config)

    # Build the complete HTML structure
    answers_html = "".join(answer_htmls)

    # Escape button text
    submit_text_escaped = escape(submit_text)
    reset_text_escaped = escape(reset_text)

    # Build buttons
    buttons_html = f'<button type="submit" class="{CSSClasses.EXAM_BUTTON}">{submit_text_escaped}</button>'
    if allow_retry:
        buttons_html += f' <button type="button" class="{CSSClasses.RESET_BUTTON}">{reset_text_escaped}</button>'

    # Build score display
    score_html = ""
    if show_score:
        score_html = f'<div class="{CSSClasses.SCORE} {CSSClasses.HIDDEN}" role="status" aria-live="polite"></div>'

    # Content is raw HTML from the markdown (user controls this)
    # We trust content_lines as it's part of the documentation content
    content_html = "\n".join(exam_data.content_lines)

    exam_html = (
        f'<div class="{CSSClasses.EXAM}" data-type="{escape(exam_data.question_type)}" '
        f'data-exam-id="{exam_data.exam_id}">'
        f"<h3>{question_html}</h3>"
        f"<form>"
        f"<fieldset>{answers_html}</fieldset>"
        f"{buttons_html}"
        f"</form>"
        f"{score_html}"
        f'<section class="{CSSClasses.CONTENT} {CSSClasses.HIDDEN}" aria-live="polite">{content_html}</section>'
        f"</div>"
    )

    return exam_html
