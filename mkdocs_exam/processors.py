"""Exam type processors for mkdocs-exam plugin."""


from .exam_config import AnswerConfig
from .html_builders import escape_html


def process_choice_truefalse_answers(config: AnswerConfig) -> list[str]:
    """Process choice or truefalse exam answers.

    Args:
        config: Answer configuration

    Returns:
        List of HTML strings for each answer

    """
    answers = config.answers
    correct_idx = config.correct_idx

    # Auto-populate truefalse answers
    if config.exam_type == "truefalse":
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
    full_answers = []

    for i, ans in enumerate(answers):
        is_correct = i in correct_idx
        input_id = f"exam-{config.exam_id}-{i}"
        input_type = "checkbox" if as_checkboxes else "radio"
        correct = "correct" if is_correct else ""
        ans_escaped = escape_html(ans)
        feedback = escape_html(config.answer_feedbacks[i]) if i < len(config.answer_feedbacks) else ""
        feedback_attr = f' data-feedback="{feedback}"' if feedback else ""
        weight = config.answer_weights[i] if i < len(config.answer_weights) else 1.0
        weight_attr = f' data-weight="{weight}"' if config.partial_credit else ""
        full_answers.append(
            f'<div><input type="{input_type}" name="answer" value="{i}" id="{input_id}" {correct}{feedback_attr}{weight_attr}>'
            f'<label for="{input_id}">{ans_escaped}</label></div>'
        )

    return full_answers


def process_short_answer_fill_essay_answers(config: AnswerConfig) -> tuple[list[str], str]:
    """Process short-answer, fill, or essay exam answers.

    Args:
        config: Answer configuration

    Returns:
        Tuple of (list of HTML answer strings, possibly modified question)

    """
    correct_vals = [escape_html(config.answers[i]) for i in config.correct_idx] or [
        escape_html(a) for a in config.answers
    ]
    correct_attr = "|".join(correct_vals)
    full_answers = []
    question = config.question

    if config.exam_type == "essay":
        full_answers.append(f'<div><textarea name="answer" rows="4" correct="{correct_attr}"></textarea></div>')
    elif config.exam_type == "fill":
        # Modify question to include input field
        question = escape_html(question).replace("___", f'<input type="text" name="answer" correct="{correct_attr}">')
    else:  # short-answer
        full_answers.append(f'<div><input type="text" name="answer" correct="{correct_attr}" ></div>')

    return full_answers, question


def process_matching_answers(config: AnswerConfig) -> list[str]:
    """Process matching exam answers.

    Args:
        config: Answer configuration

    Returns:
        List of HTML strings for matching pairs

    """
    pairs = [ans.split("|") for ans in config.answers]
    left = [escape_html(p[0].strip()) for p in pairs]
    right = [escape_html(p[1].strip()) for p in pairs]
    options = "".join(f"<option>{r}</option>" for r in right)
    full_answers = []

    for i, left_item in enumerate(left):
        full_answers.append(
            f"<div><label>{left_item} "
            f'<select name="answer" correct="{right[i]}">{options}</select>'
            "</label></div>"
        )

    return full_answers


def process_numeric_answers(config: AnswerConfig) -> list[str]:
    """Process numeric range exam answers.

    Args:
        config: Answer configuration

    Returns:
        List with single HTML string for numeric input

    """
    tolerance = config.exam_data.get("tolerance", 0.01)
    correct_val = config.exam_data.get("answer-correct", [0])[0] if config.exam_data.get("answer-correct") else 0
    unit = config.exam_data.get("unit", "")

    return [
        f'<div><input type="number" step="any" name="answer" '
        f'data-correct="{correct_val}" data-tolerance="{tolerance}" data-unit="{escape_html(unit)}">'
        f" {escape_html(unit)}</div>"
    ]


def process_code_completion_answers(config: AnswerConfig) -> list[str]:
    """Process code completion exam answers.

    Args:
        config: Answer configuration

    Returns:
        List with single HTML string for code completion

    """
    template = config.exam_data.get("template", "")
    language = config.exam_data.get("language", "python")
    blanks = config.exam_data.get("blanks", [])

    # Split template by ___ and create inputs
    parts = escape_html(template).split("___")
    code_html = parts[0]
    for i, part in enumerate(parts[1:]):
        blank_correct = (
            "|".join([escape_html(str(c)) for c in blanks[i].get("correct", [])]) if i < len(blanks) else ""
        )
        code_html += f'<input type="text" name="answer" correct="{blank_correct}" class="code-blank">'
        code_html += part

    return [f'<div><pre><code class="language-{language}">{code_html}</code></pre></div>']


def process_ordering_answers(config: AnswerConfig) -> list[str]:
    """Process ordering/sequencing exam answers.

    Args:
        config: Answer configuration

    Returns:
        List with single HTML string for ordering interface

    """
    items = config.exam_data.get("items", [])
    correct_order = config.exam_data.get("correct-order", list(range(len(items))))
    items_html = ""

    for i, item in enumerate(items):
        items_html += f'<div class="ordering-item" data-index="{i}">{escape_html(str(item))}</div>'

    return [f'<div class="ordering-container" data-correct-order="{",".join(map(str, correct_order))}">{items_html}</div>']


def process_categorization_answers(config: AnswerConfig) -> list[str]:
    """Process categorization exam answers (drag items into categories).

    Args:
        config: Answer configuration

    Returns:
        List with single HTML string for categorization interface

    """
    items = config.exam_data.get("items", [])
    categories = config.exam_data.get("categories", [])
    correct_mapping = config.exam_data.get("correct-mapping", {})

    # Build categories HTML
    categories_html = '<div class="categorization-container">'
    categories_html += '<div class="categorization-items">'
    for i, item in enumerate(items):
        correct_cat = correct_mapping.get(str(i), correct_mapping.get(i, 0))
        item_escaped = escape_html(str(item))
        categories_html += f'<div class="categorization-item" data-item-index="{i}" data-correct-category="{correct_cat}" draggable="true">{item_escaped}</div>'
    categories_html += "</div>"
    categories_html += '<div class="categorization-categories">'
    for i, category in enumerate(categories):
        cat_escaped = escape_html(str(category))
        categories_html += f'<div class="categorization-category" data-category-index="{i}"><h4>{cat_escaped}</h4><div class="category-drop-zone"></div></div>'
    categories_html += "</div>"
    categories_html += "</div>"

    return [categories_html]


def process_hotspot_answers(config: AnswerConfig) -> list[str]:
    """Process hotspot/image map exam answers (click regions on image).

    Args:
        config: Answer configuration

    Returns:
        List with single HTML string for hotspot interface

    """
    image_src = escape_html(config.exam_data.get("image", ""))
    regions = config.exam_data.get("regions", [])

    # Build hotspot HTML
    hotspot_html = '<div class="hotspot-container">'
    hotspot_html += f'<div class="hotspot-image-wrapper"><img src="{image_src}" class="hotspot-image" alt="Hotspot question">'

    # Add clickable regions as overlays
    for i, region in enumerate(regions):
        x = region.get("x", 0)
        y = region.get("y", 0)
        width = region.get("width", 50)
        height = region.get("height", 50)
        is_correct = region.get("correct", False)
        correct_attr = "correct" if is_correct else ""
        hotspot_html += (
            f'<div class="hotspot-region" data-region-index="{i}" {correct_attr} '
            f'style="left:{x}%;top:{y}%;width:{width}%;height:{height}%;"></div>'
        )

    hotspot_html += "</div></div>"
    return [hotspot_html]
