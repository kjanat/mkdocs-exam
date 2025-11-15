"""Edge case tests to push coverage above 95%."""

import textwrap
from typing import Any, cast

from mkdocs_exam.plugin import MkDocsExamPlugin


class DummyPage:
    """Mock page object for testing."""

    def __init__(self, meta: dict[str, Any] | None = None) -> None:
        """Initialize dummy page with optional metadata."""
        self.meta = meta or {}


def test_truefalse_with_no_answers():
    """Test truefalse type with no answers auto-populates True/False."""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: truefalse
        question: "Test statement"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "True" in result
    assert "False" in result
    # First option (True) should be marked correct by default
    assert 'value="0" id="exam-0-0" correct' in result


def test_truefalse_with_one_answer_no():
    """Test truefalse with one answer 'No' auto-adds True."""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: truefalse
        question: "Test statement"
        answer-correct:
          - "No"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "No" in result
    assert "True" in result  # Should auto-add True as second option


def test_truefalse_with_one_answer_false():
    """Test truefalse with one answer 'False' auto-adds True."""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: truefalse
        question: "Test statement"
        answer-correct:
          - "false"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "false" in result or "False" in result
    assert "True" in result


def test_answer_correct_as_single_string():
    """Test answer-correct can be a single string instead of list."""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Test"
        answer-correct: "Single Answer"
        answer:
          - "Wrong 1"
          - "Wrong 2"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "Single Answer" in result
    assert "Wrong 1" in result
    assert "Wrong 2" in result


def test_answer_correct_as_none():
    """Test answer-correct as None is handled."""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Test"
        answer-correct:
        answer:
          - "Option 1"
          - "Option 2"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    # Should not crash, should render options
    assert "Option 1" in result
    assert "Option 2" in result


def test_answer_as_single_string():
    """Test answer can be a single string instead of list."""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Test"
        answer-correct:
          - "Correct"
        answer: "Wrong"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "Correct" in result
    assert "Wrong" in result


def test_answer_as_none():
    """Test answer as None is handled."""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Test"
        answer-correct:
          - "Only answer"
        answer:
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "Only answer" in result


def test_answer_with_dict_value():
    """Test answer with dict containing value field."""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Test"
        answer-correct:
          - value: "Correct"
            feedback: "Great!"
        answer:
          - value: "Wrong"
            feedback: "Try again"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    # Should handle dict answers properly
    assert '<div class="exam"' in result


def test_empty_yaml_block():
    """Test empty YAML block is skipped."""
    markdown = textwrap.dedent(
        """
        ```yaml
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    # Should return original markdown unchanged (empty block)
    assert "```yaml" in result or result == "\n\n"


def test_yaml_with_only_comments():
    """Test YAML with only comments is skipped."""
    markdown = textwrap.dedent(
        """
        ```yaml
        # Just a comment
        # Another comment
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    # Should skip empty documents
    # Result should be mostly unchanged
    assert "```yaml" in result or "comment" not in result


def test_multiple_correct_checkbox_rendering():
    """Test multiple correct answers render as checkboxes."""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Select all"
        answer-correct:
          - "A"
          - "B"
        answer:
          - "C"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    # Should use checkboxes for multiple correct answers
    assert 'type="checkbox"' in result
    assert "A" in result
    assert "B" in result
    assert "C" in result


def test_exam_without_answers():
    """Test exam with question but no answers."""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Question with no answers"
        type: choice
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    # Should still render exam container
    assert '<div class="exam"' in result
    assert "Question with no answers" in result


def test_exam_with_media_no_caption():
    """Test exam with media without caption."""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Test"
        answer-correct:
          - "A"
        media:
          type: image
          src: image.png
          alt: Test image
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "image.png" in result
    assert "Test image" in result
