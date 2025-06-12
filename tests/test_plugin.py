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
        '<div class="exam" data-type="choice"><h3>Are you ready?</h3><form><fieldset>'
        '<div><input type="radio" name="answer" value="0" id="exam-0-0" correct><label for="exam-0-0">Yes!</label></div>'
        '<div><input type="radio" name="answer" value="1" id="exam-0-1" ><label for="exam-0-1">No!</label></div>'
        '<div><input type="radio" name="answer" value="2" id="exam-0-2" ><label for="exam-0-2">Maybe!</label></div>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden"><h2>Provide some additional content</h2></section></div>\n'
    )
    assert result == expected


def test_short_answer_question():
    markdown = textwrap.dedent(
        """
        <exam>

        type: short-answer
        question: What color is the sky?
        answer-correct: blue
        content:

        <p>It is often blue.</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)
    expected = (
        "\n"
        '<div class="exam" data-type="short-answer"><h3>What color is the sky?</h3><form><fieldset>'
        '<div><input type="text" name="answer" correct="blue" ></div>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden"><p>It is often blue.</p></section></div>\n'
    )
    assert result == expected


def test_fill_question():
    markdown = textwrap.dedent(
        """
        <exam>

        type: fill
        question: 2 + 2 = ___
        answer-correct: 4
        content:

        <p>Easy math.</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)
    expected = (
        "\n"
        '<div class="exam" data-type="fill"><h3>2 + 2 = <input type="text" name="answer" correct="4"></h3><form><fieldset>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden"><p>Easy math.</p></section></div>\n'
    )
    assert result == expected


def test_true_false_default_answers():
    markdown = textwrap.dedent(
        """
        <exam>

        type: truefalse
        question: The Earth orbits the Sun.
        answer-correct: True
        content:

        <p>This is obviously true.</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)
    expected = (
        "\n"
        '<div class="exam" data-type="truefalse"><h3>The Earth orbits the Sun.</h3><form><fieldset>'
        '<div><input type="radio" name="answer" value="0" id="exam-0-0" correct><label for="exam-0-0">True</label></div>'
        '<div><input type="radio" name="answer" value="1" id="exam-0-1" ><label for="exam-0-1">False</label></div>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden"><p>This is obviously true.</p></section></div>\n'
    )
    assert result == expected


def test_essay_question():
    markdown = textwrap.dedent(
        """
        <exam>

        type: essay
        question: Explain the theory of relativity in one paragraph.
        answer-correct: It deals with space and time.
        content:

        <p>Provide an explanation.</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)
    expected = (
        "\n"
        '<div class="exam" data-type="essay"><h3>Explain the theory of relativity in one paragraph.</h3><form><fieldset>'
        '<div><textarea name="answer" rows="4" correct="It deals with space and time."></textarea></div>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden"><p>Provide an explanation.</p></section></div>\n'
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
