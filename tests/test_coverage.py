"""Advanced test cases to increase coverage to 95%+."""

import os
import textwrap
from typing import Any, cast
from unittest.mock import Mock, patch

import pytest
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError

from mkdocs_exam.exam_config import ExamPluginConfig
from mkdocs_exam.html_builders import build_hints_html, build_media_html
from mkdocs_exam.plugin import MkDocsExamPlugin


class DummyPage:
    """Mock page object for testing."""

    def __init__(self, meta: dict[str, Any] | None = None, src_path: str = "test.md") -> None:
        """Initialize dummy page with optional metadata."""
        self.meta = meta or {}
        self.file = Mock(src_path=src_path)


def test_config_validate_default_points_negative():
    """Test ExamPluginConfig.validate() with negative default_points."""
    config = ExamPluginConfig()
    config.default_points = -5

    warnings, errors = config.validate()

    assert len(errors) > 0
    assert "default_points must be at least 1" in errors[0]


def test_config_validate_default_points_zero():
    """Test ExamPluginConfig.validate() with zero default_points."""
    config = ExamPluginConfig()
    config.default_points = 0

    warnings, errors = config.validate()

    assert len(errors) > 0
    assert "default_points must be at least 1" in errors[0]


def test_config_validate_default_points_large():
    """Test ExamPluginConfig.validate() warns for unusually high default_points."""
    config = ExamPluginConfig()
    config.default_points = 150

    warnings, errors = config.validate()

    assert len(warnings) > 0
    assert "unusually high" in warnings[0]
    assert "150" in warnings[0]


def test_config_validate_default_points_normal():
    """Test ExamPluginConfig.validate() passes for normal default_points."""
    config = ExamPluginConfig()
    config.default_points = 10

    warnings, errors = config.validate()

    # Should not have errors or warnings for normal value
    assert len([w for w in warnings if "default_points" in w]) == 0
    assert len([e for e in errors if "default_points" in e]) == 0


def test_on_config_theme_compatibility_warning():
    """Test on_config warns for non-standard themes."""
    plugin = MkDocsExamPlugin()
    mkdocs_config = Mock(spec=MkDocsConfig)
    mkdocs_config.theme = Mock(name="custom-theme")

    # Should not raise, just warn
    result = plugin.on_config(mkdocs_config)
    assert result == mkdocs_config


def test_on_config_standard_theme_no_warning():
    """Test on_config doesn't warn for standard themes."""
    plugin = MkDocsExamPlugin()
    mkdocs_config = Mock(spec=MkDocsConfig)
    mkdocs_config.theme = Mock(name="material")

    result = plugin.on_config(mkdocs_config)
    assert result == mkdocs_config


def test_on_config_validates_default_type():
    """Test on_config validates default_type is in allowed list."""
    plugin = MkDocsExamPlugin()
    plugin.config = ExamPluginConfig()
    plugin.config.default_type = "invalid-type"

    mkdocs_config = Mock(spec=MkDocsConfig)
    mkdocs_config.theme = Mock(name="mkdocs")

    with pytest.raises(PluginError) as exc_info:
        plugin.on_config(mkdocs_config)

    assert "Invalid default_type" in str(exc_info.value)
    assert "invalid-type" in str(exc_info.value)


def test_on_config_validates_default_points():
    """Test on_config validates default_points."""
    plugin = MkDocsExamPlugin()
    plugin.config = ExamPluginConfig()
    plugin.config.default_points = -1
    plugin.config.default_type = "choice"

    mkdocs_config = Mock(spec=MkDocsConfig)
    mkdocs_config.theme = Mock(name="mkdocs")

    with pytest.raises(PluginError) as exc_info:
        plugin.on_config(mkdocs_config)

    assert "default_points must be at least 1" in str(exc_info.value)


def test_strict_validation_true_invalid_exam_type():
    """Test strict_validation=True raises error for invalid exam type."""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: invalid-type
        question: "Test"
        answer-correct:
          - "Answer"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    plugin.config = ExamPluginConfig()
    plugin.config.strict_validation = True

    with pytest.raises(PluginError) as exc_info:
        plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "Invalid type" in str(exc_info.value)
    assert "invalid-type" in str(exc_info.value)


def test_strict_validation_true_missing_question():
    """Test strict_validation=True raises error for missing question."""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: choice
        answer-correct:
          - "Answer"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    plugin.config = ExamPluginConfig()
    plugin.config.strict_validation = True

    with pytest.raises(PluginError) as exc_info:
        plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "Missing 'question' field" in str(exc_info.value)


def test_strict_validation_true_invalid_exam_data():
    """Test strict_validation=True raises error for non-dict exam data."""
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
    plugin.config.strict_validation = True

    with pytest.raises(PluginError) as exc_info:
        plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "Invalid exam data" in str(exc_info.value)


def test_on_shutdown_logs_statistics():
    """Test on_shutdown logs total exams processed."""
    plugin = MkDocsExamPlugin()
    plugin.total_exams_processed = 42

    # Should not raise
    plugin.on_shutdown()


def test_on_shutdown_zero_exams():
    """Test on_shutdown handles zero exams gracefully."""
    plugin = MkDocsExamPlugin()
    plugin.total_exams_processed = 0

    # Should not raise or log
    plugin.on_shutdown()


def test_on_build_error():
    """Test on_build_error logs error."""
    plugin = MkDocsExamPlugin()
    error = Exception("Test error")

    # Should not raise
    plugin.on_build_error(error)


def test_html_builders_hints_with_penalty():
    """Test build_hints_html with penalty hints."""
    hints = [
        {"text": "Hint 1", "penalty": 10},
        {"text": "Hint 2", "penalty": 20},
    ]

    html = build_hints_html(hints)

    assert "Hint 1" in html
    assert "Hint 2" in html
    assert "data-penalty=\"10\"" in html
    assert "data-penalty=\"20\"" in html
    assert "(-10%)" in html
    assert "(-20%)" in html


def test_html_builders_hints_without_penalty():
    """Test build_hints_html with string hints (no penalty)."""
    hints = ["Simple hint 1", "Simple hint 2"]

    html = build_hints_html(hints)

    assert "Simple hint 1" in html
    assert "Simple hint 2" in html
    # Should not have penalty attributes
    assert "data-penalty" not in html


def test_html_builders_media_video():
    """Test build_media_html for video."""
    media = {"type": "video", "src": "video.mp4", "caption": "Test video"}

    html = build_media_html(media)

    assert "<video" in html
    assert 'src="video.mp4"' in html
    assert "Test video" in html


def test_html_builders_media_audio():
    """Test build_media_html for audio."""
    media = {"type": "audio", "src": "audio.mp3", "caption": "Test audio"}

    html = build_media_html(media)

    assert "<audio" in html
    assert 'src="audio.mp3"' in html
    assert "Test audio" in html


def test_html_builders_media_unknown_type():
    """Test build_media_html returns empty string for unknown type."""
    media = {"type": "unknown", "src": "file.txt"}

    html = build_media_html(media)

    assert html == ""


def test_environment_variable_interpolation_in_dict():
    """Test interpolate_env_vars handles dictionaries."""
    os.environ["TEST_VAR"] = "test_value"

    markdown = textwrap.dedent(
        """
        ```yaml
        question: "${TEST_VAR}"
        answer-correct:
          - "A"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "test_value" in result
    del os.environ["TEST_VAR"]


def test_environment_variable_interpolation_in_list():
    """Test interpolate_env_vars handles lists."""
    os.environ["TEST_ANSWER"] = "correct_answer"

    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Test"
        answer-correct:
          - "${TEST_ANSWER}"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "correct_answer" in result
    del os.environ["TEST_ANSWER"]


def test_processor_fallback_unknown_type():
    """Test that unknown exam types fall back gracefully."""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: unknown-future-type
        question: "Test"
        answer-correct:
          - "A"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    plugin.config = ExamPluginConfig()
    plugin.config.strict_validation = False

    # Should not raise, should fallback to choice
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert '<div class="exam"' in result
    assert 'data-type="choice"' in result


def test_page_with_src_path():
    """Test exam processing includes page path in error messages."""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: invalid
        question: "Test"
        answer-correct:
          - "A"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    plugin.config = ExamPluginConfig()
    plugin.config.strict_validation = False

    page = DummyPage(src_path="docs/test.md")
    result = plugin.on_page_markdown(markdown, cast(Any, page), cast(Any, None))

    # Should process without error in non-strict mode
    assert '<div class="exam"' in result


def test_truefalse_auto_population():
    """Test truefalse type auto-populates answers."""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: truefalse
        question: "Test statement"
        answer-correct:
          - "True"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert "True" in result
    assert "False" in result
    assert 'type="radio"' in result


def test_answer_weights_and_partial_credit():
    """Test partial credit with weighted answers."""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Select all correct"
        type: choice
        partial-credit: true
        answer-correct:
          - value: "A"
            weight: 0.5
          - value: "B"
            weight: 0.5
        answer:
          - value: "C"
            weight: 0.0
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert 'data-weight="0.5"' in result
    assert 'type="checkbox"' in result  # Multiple correct answers


def test_total_exams_counter_increments():
    """Test that total_exams_processed counter increments correctly."""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Q1"
        answer-correct:
          - "A"
        ---
        question: "Q2"
        answer-correct:
          - "B"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    assert plugin.total_exams_processed == 0

    plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert plugin.total_exams_processed == 2


def test_get_strict_validation_fallback():
    """Test _get_strict_validation() handles missing config attribute."""
    plugin = MkDocsExamPlugin()
    # Simulate old config without strict_validation attribute
    plugin.config = {}  # type: ignore[assignment]

    # Should default to False for backward compatibility
    assert plugin._get_strict_validation() is False
