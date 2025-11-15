"""Final coverage tests to reach 100% for plugin.py."""

import textwrap
from typing import Any, cast
from unittest.mock import Mock

import pytest
from mkdocs.exceptions import PluginError

from mkdocs_exam.exam_config import ExamPluginConfig
from mkdocs_exam.plugin import MkDocsExamPlugin


class DummyPage:
    """Mock page object for testing."""

    def __init__(self, meta: dict[str, Any] | None = None, src_path: str = "test.md") -> None:
        """Initialize dummy page with optional metadata."""
        self.meta = meta or {}
        self.file = Mock(src_path=src_path)


def test_on_startup_sets_dirty_flag():
    """Test on_startup method sets dirty flag."""
    plugin = MkDocsExamPlugin()
    assert plugin.dirty is False

    plugin.on_startup(command="serve", dirty=True)
    assert plugin.dirty is True

    plugin.on_startup(command="build", dirty=False)
    assert plugin.dirty is False


def test_invalid_exam_data_non_strict_mode():
    """Test invalid exam data (non-dict) in non-strict mode returns empty string."""
    markdown = textwrap.dedent(
        """
        ```yaml
        - "Not a dict"
        - "Another item"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    plugin.config = ExamPluginConfig()
    plugin.config.strict_validation = False

    # Should return markdown unchanged (just removes the invalid block)
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    # Invalid exam should be skipped with warning
    assert '<div class="exam"' not in result


def test_invalid_exam_type_non_strict_mode():
    """Test invalid exam type in non-strict mode logs warning and continues."""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: totally-invalid-type-12345
        question: "Test"
        answer-correct:
          - "A"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    plugin.config = ExamPluginConfig()
    plugin.config.strict_validation = False

    # Should fall back to choice type
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    # Should still render as choice type (fallback)
    assert '<div class="exam"' in result
    assert 'data-type="choice"' in result


def test_yaml_parsing_error_raises_plugin_error():
    """Test malformed YAML raises PluginError."""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Test"
        answer-correct:
          - "A"
          invalid yaml syntax here: {{{
        ```
        """
    )

    plugin = MkDocsExamPlugin()

    with pytest.raises(PluginError) as exc_info:
        plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "YAML parsing error" in str(exc_info.value)


def test_on_page_content_injects_style_and_script():
    """Test on_page_content appends CSS and JavaScript."""
    plugin = MkDocsExamPlugin()

    html_input = "<p>Test content</p>"
    result = plugin.on_page_content(
        html_input, cast(Any, DummyPage()), cast(Any, None), cast(Any, None)
    )

    # Should append style and script
    assert html_input in result
    assert "<style" in result
    assert "</style>" in result
    assert "<script" in result
    assert "</script>" in result
    assert ".exam" in result  # CSS content
    assert "function" in result or "const" in result  # JS content


def test_unknown_exam_type_fallback():
    """Test unknown exam type falls back gracefully."""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: future-exam-type-2030
        question: "Test question"
        answer-correct:
          - "Correct answer"
        answer:
          - "Wrong answer"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    plugin.config = ExamPluginConfig()
    plugin.config.strict_validation = False

    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    # Should render with fallback to choice type
    assert '<div class="exam"' in result
    assert "Test question" in result
    assert "Correct answer" in result
    assert "Wrong answer" in result


def test_missing_question_non_strict_mode():
    """Test missing question field in non-strict mode logs warning."""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: choice
        answer-correct:
          - "Answer without question"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    plugin.config = ExamPluginConfig()
    plugin.config.strict_validation = False

    # Should return empty string for invalid exam
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    # Invalid exam should be skipped
    assert '<div class="exam"' not in result


def test_generate_answers_html_fallback():
    """Test _generate_answers_html fallback for unknown exam types."""
    from dataclasses import dataclass

    @dataclass
    class MockConfig:
        """Mock answer config."""

        exam_type: str = "unknown-future-type"
        question: str = "Test question"

    plugin = MkDocsExamPlugin()
    config = MockConfig()

    # Call the internal method directly to test the fallback
    answers, question = plugin._generate_answers_html(config)

    # Should return empty answers and the question
    assert answers == []
    assert question == "Test question"
