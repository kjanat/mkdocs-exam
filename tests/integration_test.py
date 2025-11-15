"""Integration tests for mkdocs-exam plugin with actual MkDocs builds."""

import subprocess
import tempfile
import textwrap
from pathlib import Path

import pytest


@pytest.fixture
def temp_mkdocs_project():
    """Create a temporary MkDocs project for integration testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create mkdocs.yml
        mkdocs_yml = project_dir / "mkdocs.yml"
        mkdocs_yml.write_text(
            textwrap.dedent(
                """
                site_name: Test Site
                plugins:
                  - mkdocs-exam
                theme:
                  name: mkdocs
                """
            )
        )

        # Create docs directory
        docs_dir = project_dir / "docs"
        docs_dir.mkdir()

        yield project_dir, docs_dir


def test_basic_exam_build(temp_mkdocs_project):
    """Test that basic exam renders correctly in a full MkDocs build."""
    project_dir, docs_dir = temp_mkdocs_project

    # Create index.md with an exam
    index_md = docs_dir / "index.md"
    index_md.write_text(
        textwrap.dedent(
            """
            # Test Page

            Here's a test exam:

            ```yaml
            question: "What is 2 + 2?"
            answer-correct:
              - "4"
            answer:
              - "3"
              - "5"
            ```

            More content here.
            """
        )
    )

    # Build the site
    result = subprocess.run(
        ["mkdocs", "build", "--strict"],
        check=False,
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    # Check build succeeded
    assert result.returncode == 0, f"Build failed: {result.stderr}"

    # Check site was built
    site_dir = project_dir / "site"
    assert site_dir.exists()

    # Check index.html was created
    index_html = site_dir / "index.html"
    assert index_html.exists()

    # Check exam HTML is in output
    html_content = index_html.read_text()
    assert '<div class="exam"' in html_content
    assert 'data-type="choice"' in html_content
    assert "What is 2 + 2?" in html_content


def test_multiple_exam_types_build(temp_mkdocs_project):
    """Test building a page with multiple different exam types."""
    project_dir, docs_dir = temp_mkdocs_project

    index_md = docs_dir / "index.md"
    index_md.write_text(
        textwrap.dedent(
            """
            # Multiple Exam Types

            ## Choice Question

            ```yaml
            question: "Select correct answers"
            answer-correct:
              - "A"
              - "B"
            answer:
              - "C"
            ```

            ## True/False Question

            ```yaml
            type: truefalse
            question: "The sky is blue."
            answer-correct:
              - "True"
            ```

            ## Short Answer

            ```yaml
            type: short-answer
            question: "What color is the sky?"
            answer-correct:
              - "blue"
            ```
            """
        )
    )

    result = subprocess.run(
        ["mkdocs", "build", "--strict"],
        check=False,
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Build failed: {result.stderr}"

    index_html = project_dir / "site" / "index.html"
    html_content = index_html.read_text()

    # Check all exam types rendered
    assert 'data-type="choice"' in html_content
    assert 'data-type="truefalse"' in html_content
    assert 'data-type="short-answer"' in html_content


def test_exam_with_hints_and_explanation(temp_mkdocs_project):
    """Test exam with advanced features like hints and explanations."""
    project_dir, docs_dir = temp_mkdocs_project

    index_md = docs_dir / "index.md"
    index_md.write_text(
        textwrap.dedent(
            """
            # Advanced Exam

            ```yaml
            question: "What is the capital of France?"
            answer-correct:
              - "Paris"
            answer:
              - "London"
              - "Berlin"
            hints:
              - text: "It's known as the City of Light"
                penalty: 10
              - text: "The Eiffel Tower is located here"
                penalty: 20
            explanation: "Paris is the capital and most populous city of France."
            show-explanation: "on-correct"
            points: 10
            ```
            """
        )
    )

    result = subprocess.run(
        ["mkdocs", "build", "--strict"],
        check=False,
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Build failed: {result.stderr}"

    index_html = project_dir / "site" / "index.html"
    html_content = index_html.read_text()

    # Check hints rendered
    assert 'class="exam-hints' in html_content or "City of Light" in html_content

    # Check points attribute
    assert 'data-points="10"' in html_content


def test_multi_document_yaml_build(temp_mkdocs_project):
    """Test that multi-document YAML (--- separator) works."""
    project_dir, docs_dir = temp_mkdocs_project

    index_md = docs_dir / "index.md"
    index_md.write_text(
        textwrap.dedent(
            """
            # Multiple Exams

            ```yaml
            question: "First question"
            answer-correct:
              - "A"
            ---
            question: "Second question"
            answer-correct:
              - "B"
            ```
            """
        )
    )

    result = subprocess.run(
        ["mkdocs", "build", "--strict"],
        check=False,
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Build failed: {result.stderr}"

    index_html = project_dir / "site" / "index.html"
    html_content = index_html.read_text()

    # Should have two exam divs
    assert html_content.count('<div class="exam"') == 2
    assert "First question" in html_content
    assert "Second question" in html_content


def test_invalid_exam_graceful_fallback(temp_mkdocs_project):
    """Test that invalid exams are handled gracefully (warning, not error)."""
    project_dir, docs_dir = temp_mkdocs_project

    index_md = docs_dir / "index.md"
    index_md.write_text(
        textwrap.dedent(
            """
            # Invalid Exam Test

            ```yaml
            type: invalid-type
            question: "This exam has an invalid type"
            answer-correct:
              - "A"
            ```
            """
        )
    )

    result = subprocess.run(
        ["mkdocs", "build"],  # Don't use --strict for this test
        check=False,
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    # Should complete build (graceful fallback)
    assert result.returncode == 0

    # Should log warning
    assert "Invalid type" in result.stderr or "invalid-type" in result.stderr

    # Should fallback to choice type
    index_html = project_dir / "site" / "index.html"
    if index_html.exists():
        html_content = index_html.read_text()
        assert 'data-type="choice"' in html_content


def test_css_and_js_injection(temp_mkdocs_project):
    """Test that CSS and JS are properly injected into the page."""
    project_dir, docs_dir = temp_mkdocs_project

    index_md = docs_dir / "index.md"
    index_md.write_text(
        textwrap.dedent(
            """
            # Test Exam

            ```yaml
            question: "Test"
            answer-correct:
              - "A"
            ```
            """
        )
    )

    result = subprocess.run(
        ["mkdocs", "build", "--strict"],
        check=False,
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    index_html = project_dir / "site" / "index.html"
    html_content = index_html.read_text()

    # Check CSS injected
    assert '<style type="text/css">' in html_content
    assert ".exam" in html_content  # Should contain exam CSS classes

    # Check JS injected
    assert '<script type="text/javascript"' in html_content


def test_exam_disabled_via_metadata(temp_mkdocs_project):
    """Test that exams can be disabled via page metadata."""
    project_dir, docs_dir = temp_mkdocs_project

    index_md = docs_dir / "index.md"
    index_md.write_text(
        textwrap.dedent(
            """
            ---
            exam: disable
            ---

            # Test Page

            ```yaml
            question: "This should not be processed"
            answer-correct:
              - "A"
            ```
            """
        )
    )

    result = subprocess.run(
        ["mkdocs", "build", "--strict"],
        check=False,
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    index_html = project_dir / "site" / "index.html"
    html_content = index_html.read_text()

    # Exam should NOT be processed
    assert '<div class="exam"' not in html_content
    # Original YAML code block should remain
    assert "```yaml" in html_content or "question" in html_content
