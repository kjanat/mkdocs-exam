import textwrap

from mkdocs_exam.plugin import MkDocsExamPlugin


class DummyPage:
    def __init__(self, meta=None):
        self.meta = meta or {}


def test_exam_block_converts_to_html():
    markdown = textwrap.dedent(
        """
        <exam>

        question: Are you ready?
        answer-correct: Yes!
        answer: No!
        answer: Maybe!
        content:

        <h2>Provide some additional content</h2>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)
    expected = (
        "\n"
        '<div class="exam"><h3>Are you ready?</h3><form><fieldset>'
        '<div><input type="radio" name="answer" value="0" id="exam-0-0" correct>'
        '<label for="exam-0-0">Yes!</label></div>'
        '<div><input type="radio" name="answer" value="1" id="exam-0-1" >'
        '<label for="exam-0-1">No!</label></div>'
        '<div><input type="radio" name="answer" value="2" id="exam-0-2" >'
        '<label for="exam-0-2">Maybe!</label></div>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden">\n'
        "<h2>Provide some additional content</h2></section></div>\n"
    )
    assert result == expected


def test_exam_disabled_leaves_markdown_unchanged():
    markdown = textwrap.dedent(
        """
        <exam>

        question: Are you ready?
        answer-correct: Yes!
        answer: No!
        answer: Maybe!
        content:

        <h2>Provide some additional content</h2>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    page = DummyPage(meta={"exam": "disable"})
    result = plugin.on_page_markdown(markdown, page, None)
    assert result == markdown


def test_drag_exam_block_converts_to_html():
    markdown = textwrap.dedent(
        """
        <drag>

        question: Match
        pair: A -> 1
        pair: B -> 2
        content:

        <p>Hi</p>
        </drag>
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)
    expected = (
        "\n"
        '<div class="drag-exam"><h3>Match</h3><form><div class="drag-container">'
        '<div class="drag-item" draggable="true" data-id="drag-0-0">A</div>'
        '<div class="drag-item" draggable="true" data-id="drag-0-1">B</div>'
        '</div><div class="drop-container">'
        '<div class="drop-zone" data-target="drag-0-0">1</div>'
        '<div class="drop-zone" data-target="drag-0-1">2</div>'
        '</div><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden">\n'
        "<p>Hi</p></section></div>\n"
    )
    assert result == expected
