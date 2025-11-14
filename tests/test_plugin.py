import textwrap
from unittest.mock import Mock

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page

from mkdocs_exam.plugin import MkDocsExamPlugin


def create_mock_page(meta: dict | None = None) -> Page:
    """Create a mock Page object for testing."""
    page = Mock(spec=Page)
    page.meta = meta or {}
    return page  # type: ignore[return-value]


def create_mock_config() -> MkDocsConfig:
    """Create a mock MkDocsConfig object for testing."""
    return Mock(spec=MkDocsConfig)  # type: ignore[return-value]


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
    result = plugin.on_page_markdown(markdown, create_mock_page(), create_mock_config())
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
    result = plugin.on_page_markdown(markdown, create_mock_page(), create_mock_config())
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
    result = plugin.on_page_markdown(markdown, create_mock_page(), create_mock_config())
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
    result = plugin.on_page_markdown(markdown, create_mock_page(), create_mock_config())
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
    result = plugin.on_page_markdown(markdown, create_mock_page(), create_mock_config())
    expected = (
        "\n"
        '<div class="exam" data-type="essay"><h3>Explain the theory of relativity in one paragraph.</h3><form><fieldset>'
        '<div><textarea name="answer" rows="4" correct="It deals with space and time."></textarea></div>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden"><p>Provide an explanation.</p></section></div>\n'
    )
    assert result == expected


def test_matching_question():
    markdown = textwrap.dedent(
        """
        <exam>

        type: matching
        question: Match the capitals to countries
        answer: Paris | France
        answer: Rome | Italy
        answer: Madrid | Spain
        content:

        <p>Capitals and their countries.</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, create_mock_page(), create_mock_config())
    expected = (
        "\n"
        '<div class="exam" data-type="matching"><h3>Match the capitals to countries</h3><form><fieldset>'
        '<div><label>Paris <select name="answer" correct="France"><option>France</option><option>Italy</option><option>Spain</option></select></label></div>'
        '<div><label>Rome <select name="answer" correct="Italy"><option>France</option><option>Italy</option><option>Spain</option></select></label></div>'
        '<div><label>Madrid <select name="answer" correct="Spain"><option>France</option><option>Italy</option><option>Spain</option></select></label></div>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden"><p>Capitals and their countries.</p></section></div>\n'
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
    page = create_mock_page(meta={"exam": "disable"})
    result = plugin.on_page_markdown(markdown, page, create_mock_config())
    assert result == markdown


def test_on_startup_sets_dirty_flag():
    plugin = MkDocsExamPlugin()
    assert plugin.dirty is False
    plugin.on_startup(command="build", dirty=True)
    assert plugin.dirty is True


def test_code_fence_preservation():
    markdown = textwrap.dedent(
        """
        ```python
        <exam>
        This should not be processed
        </exam>
        ```

        <exam>

        question: Real question?
        answer-correct: Yes
        content:

        <p>Test content</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, create_mock_page(), create_mock_config())
    # Code fence should remain unchanged with <exam> inside
    assert "```python" in result
    assert "```" in result
    # The exam block inside code fence should NOT be converted to HTML
    assert result.count('<div class="exam"') == 1  # Only the real exam outside code fence
    # Real exam should be processed
    assert "Real question?" in result


def test_truefalse_no_answers_defaults():
    markdown = textwrap.dedent(
        """
        <exam>

        type: truefalse
        question: Is this a test?
        content:

        <p>Additional info</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, create_mock_page(), create_mock_config())
    # Should default to True/False with True as correct
    assert '<label for="exam-0-0">True</label>' in result
    assert '<label for="exam-0-1">False</label>' in result
    assert 'id="exam-0-0" correct' in result


def test_truefalse_single_false_answer_adds_true():
    markdown = textwrap.dedent(
        """
        <exam>

        type: truefalse
        question: Is this wrong?
        answer-correct: False
        content:

        <p>Explanation here</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, create_mock_page(), create_mock_config())
    # Should add "True" as second option
    assert '<label for="exam-0-0">False</label>' in result
    assert '<label for="exam-0-1">True</label>' in result
    assert 'id="exam-0-0" correct' in result


def test_on_page_content_injects_css_and_js():
    plugin = MkDocsExamPlugin()
    html = "<div>test content</div>"
    result = plugin.on_page_content(
        html,
        page=create_mock_page(),
        config=create_mock_config(),
        files=Mock(),
    )
    assert result is not None
    assert "test content" in result
    assert '<style type="text/css">' in result
    assert '<script type="text/javascript" defer>' in result
