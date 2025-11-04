"""Tests for mkdocs-exam plugin."""

import textwrap

import pytest

from mkdocs_exam.constants import CSSClasses
from mkdocs_exam.html_builder import build_exam_html, escape
from mkdocs_exam.parser import ExamData, ExamParseError, find_exam_blocks, parse_exam_block
from mkdocs_exam.plugin import MkDocsExamPlugin


class DummyPage:
    """Mock page object for testing."""

    def __init__(self, meta=None):
        """Initialize with optional metadata."""
        self.meta = meta or {}
        self.file = DummyFile()


class DummyFile:
    """Mock file object for testing."""

    def __init__(self):
        """Initialize with default path."""
        self.src_path = "test.md"


# Parser Tests


def test_find_exam_blocks():
    """Test finding exam blocks in markdown."""
    markdown = textwrap.dedent(
        """
        Some text before
        <exam>
        question: Test?
        answer-correct: Yes
        content:
        <p>Content</p>
        </exam>
        More text
        <exam>
        question: Another?
        answer-correct: No
        content:
        <p>More content</p>
        </exam>
        """
    )
    blocks = find_exam_blocks(markdown)
    assert len(blocks) == 2
    assert "question: Test?" in blocks[0]
    assert "question: Another?" in blocks[1]


def test_parse_exam_block_basic():
    """Test parsing a basic exam block."""
    block = textwrap.dedent(
        """
        question: Are you ready?
        answer-correct: Yes!
        answer: No!
        content:
        <h2>Great!</h2>
        """
    ).strip()

    exam_data = parse_exam_block(block, exam_id=0)
    assert exam_data.question == "Are you ready?"
    assert exam_data.answers == ["Yes!", "No!"]
    assert exam_data.correct_indices == [0]
    assert exam_data.question_type == "choice"
    assert "<h2>Great!</h2>" in exam_data.content_lines


def test_parse_exam_block_missing_content():
    """Test parsing fails when content section is missing."""
    block = "question: Test?\nanswer-correct: Yes"

    with pytest.raises(ExamParseError) as exc_info:
        parse_exam_block(block)

    assert "missing 'content:' section" in str(exc_info.value).lower()


def test_parse_exam_block_empty():
    """Test parsing fails on empty block."""
    with pytest.raises(ExamParseError) as exc_info:
        parse_exam_block("")

    assert "empty" in str(exc_info.value).lower()


def test_parse_exam_block_no_question():
    """Test validation fails when question is missing."""
    block = textwrap.dedent(
        """
        answer-correct: Yes
        content:
        <p>Test</p>
        """
    ).strip()

    with pytest.raises(ExamParseError) as exc_info:
        parse_exam_block(block)

    assert "question" in str(exc_info.value).lower()


def test_parse_exam_block_multiple_correct():
    """Test parsing multiple correct answers."""
    block = textwrap.dedent(
        """
        question: Select all that apply
        answer-correct: Option 1
        answer: Option 2
        answer-correct: Option 3
        content:
        <p>Correct!</p>
        """
    ).strip()

    exam_data = parse_exam_block(block)
    assert exam_data.correct_indices == [0, 2]
    assert len(exam_data.answers) == 3


# HTML Builder Tests


def test_escape_html():
    """Test HTML escaping prevents XSS."""
    dangerous = '<script>alert("XSS")</script>'
    escaped = escape(dangerous)
    assert "<script>" not in escaped
    assert "&lt;script&gt;" in escaped


def test_escape_quotes():
    """Test quote escaping."""
    text_with_quotes = 'Text with "quotes" and \'apostrophes\''
    escaped = escape(text_with_quotes)
    assert '"' not in escaped or "&quot;" in escaped


def test_build_exam_html_escapes_answers():
    """Test that answers are properly escaped."""
    exam_data = ExamData(
        question="Test question?",
        answers=["<script>alert('xss')</script>", "Safe answer"],
        correct_indices=[1],
        content_lines=["<p>Content</p>"],
    )

    html = build_exam_html(exam_data)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "Safe answer" in html


# Plugin Integration Tests


def test_exam_block_converts_to_html():
    """Test that exam blocks are converted to HTML."""
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
    plugin.config = {}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    # Check structure
    assert f'class="{CSSClasses.EXAM}"' in result
    assert 'data-type="choice"' in result
    assert "Are you ready?" in result
    assert 'type="radio"' in result  # Single correct answer = radio
    assert 'class="exam-button"' in result
    assert 'class="reset-button"' in result
    assert 'class="exam-score' in result


def test_short_answer_question():
    """Test short-answer question type."""
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
    plugin.config = {}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert 'data-type="short-answer"' in result
    assert 'type="text"' in result
    assert 'correct="blue"' in result


def test_fill_question():
    """Test fill-in-the-blank question type."""
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
    plugin.config = {}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert 'data-type="fill"' in result
    assert 'correct="4"' in result
    assert '2 + 2 =' in result


def test_true_false_default_answers():
    """Test true/false with default answers."""
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
    plugin.config = {}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert 'data-type="truefalse"' in result
    assert "True" in result
    assert "False" in result


def test_essay_question():
    """Test essay question type."""
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
    plugin.config = {}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert 'data-type="essay"' in result
    assert "<textarea" in result
    assert 'rows="4"' in result


def test_matching_question():
    """Test matching question type."""
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
    plugin.config = {}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert 'data-type="matching"' in result
    assert "<select" in result
    assert "Paris" in result
    assert "France" in result
    assert 'correct="France"' in result


def test_exam_disabled_leaves_markdown_unchanged():
    """Test that exams can be disabled per page."""
    markdown = textwrap.dedent(
        """
        <exam>
        question: Are you ready?
        answer-correct: Yes!
        answer: No!
        content:
        <h2>Content</h2>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    page = DummyPage(meta={"exam": "disable"})
    result = plugin.on_page_markdown(markdown, page, None)
    assert result == markdown


def test_plugin_config_submit_text():
    """Test custom submit button text."""
    markdown = textwrap.dedent(
        """
        <exam>
        question: Test?
        answer-correct: Yes
        content:
        <p>Content</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    plugin.config = {"submit_text": "Check Answer"}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "Check Answer" in result


def test_plugin_config_reset_text():
    """Test custom reset button text."""
    markdown = textwrap.dedent(
        """
        <exam>
        question: Test?
        answer-correct: Yes
        content:
        <p>Content</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    plugin.config = {"reset_text": "Start Over"}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "Start Over" in result


def test_plugin_config_no_retry():
    """Test disabling retry button."""
    markdown = textwrap.dedent(
        """
        <exam>
        question: Test?
        answer-correct: Yes
        content:
        <p>Content</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    plugin.config = {"allow_retry": False}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "reset-button" not in result


def test_plugin_config_no_score():
    """Test disabling score display."""
    markdown = textwrap.dedent(
        """
        <exam>
        question: Test?
        answer-correct: Yes
        content:
        <p>Content</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    plugin.config = {"show_score": False}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "exam-score" not in result


def test_multiple_choice_uses_checkboxes():
    """Test that multiple correct answers use checkboxes."""
    markdown = textwrap.dedent(
        """
        <exam>
        question: Select all that apply
        answer-correct: Option 1
        answer: Option 2
        answer-correct: Option 3
        content:
        <p>Correct!</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    plugin.config = {}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert 'type="checkbox"' in result
    assert 'type="radio"' not in result


def test_malformed_exam_shows_error():
    """Test that malformed exams show error message."""
    markdown = textwrap.dedent(
        """
        <exam>
        answer-correct: Yes
        content:
        <p>Missing question!</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    plugin.config = {}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "error" in result.lower()
    assert "parse" in result.lower() or "question" in result.lower()


def test_conditional_css_js_injection():
    """Test that CSS/JS are only injected when exams are present."""
    plugin = MkDocsExamPlugin()

    # Without exams
    html_without = "<p>Regular content</p>"
    result_without = plugin.on_page_content(html_without, page=DummyPage(), config=None, files=None)
    assert result_without == html_without

    # With exams
    html_with = f'<div class="{CSSClasses.EXAM}">Exam content</div>'
    result_with = plugin.on_page_content(html_with, page=DummyPage(), config=None, files=None)
    assert "<style" in result_with
    assert "<script" in result_with


def test_aria_attributes_present():
    """Test that ARIA attributes are added for accessibility."""
    markdown = textwrap.dedent(
        """
        <exam>
        question: Test?
        answer-correct: Yes
        answer: No
        content:
        <p>Content</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    plugin.config = {}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "aria-" in result  # Should contain ARIA attributes


def test_xss_in_question():
    """Test XSS prevention in question field."""
    markdown = textwrap.dedent(
        """
        <exam>
        question: <script>alert('xss')</script>What is this?
        answer-correct: Safe
        content:
        <p>Content</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    plugin.config = {}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "<script>" not in result or "&lt;script&gt;" in result


def test_special_characters_in_answers():
    """Test handling of special characters in answers."""
    markdown = textwrap.dedent(
        """
        <exam>
        question: What is the symbol?
        answer-correct: <>&"'
        content:
        <p>Content</p>
        </exam>
        """
    )
    plugin = MkDocsExamPlugin()
    plugin.config = {}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    # Should be escaped
    assert "&lt;" in result or "&gt;" in result or "&quot;" in result
