"""Test for nested YAML codeblocks edge case."""

import textwrap
from typing import Any, cast

from mkdocs_exam.plugin import MkDocsExamPlugin


class DummyPage:
    """Mock page object for testing."""

    def __init__(self, meta: dict[str, Any] | None = None) -> None:
        """Initialize dummy page with optional metadata."""
        self.meta = meta or {}


def test_exam_with_nested_yaml_in_content():
    """Test exam with nested YAML codeblock in content field.

    This tests if the parser can handle a YAML codeblock inside the exam's content.
    This is a common use case for programming documentation exams.
    """
    markdown = textwrap.dedent(
        """
        # Test Page

        ```yaml
        question: "What is the correct YAML syntax for a list?"
        answer-correct:
          - "Using dashes"
        answer:
          - "Using brackets"
          - "Using parentheses"
        content: |
          Here's an example of correct YAML syntax:

          ```yaml
          items:
            - first
            - second
            - third
          ```

          The above shows proper list formatting.
        ```

        More content after the exam.
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    print("=" * 80)
    print("RESULT:")
    print(result)
    print("=" * 80)

    # Check if exam was processed
    assert '<div class="exam"' in result, "Exam should be rendered"
    assert "What is the correct YAML syntax" in result, "Question should be present"

    # Check if nested YAML content is preserved AS A CODE BLOCK
    # The nested ```yaml should be converted to markdown code block
    # MkDocs will later convert it to <code> tags, but we should see the fence markers preserved
    assert "```yaml" in result, "Nested YAML code fence should be preserved"
    assert "items:" in result, "Nested YAML content should be present"
    assert "- first" in result, "Nested YAML list items should be present"


def test_exam_with_nested_yaml_in_question():
    """Test exam with nested YAML codeblock in question field."""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: |
          Which YAML is valid?

          ```yaml
          key: value
          ```
        answer-correct:
          - "First one"
        answer:
          - "Second one"
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    print("=" * 80)
    print("RESULT WITH NESTED YAML IN QUESTION:")
    print(result)
    print("=" * 80)

    # This test will likely FAIL due to the regex issue
    # The regex will match up to the first ``` it finds
    assert '<div class="exam"' in result


def test_exam_with_nested_code_non_yaml():
    """Test exam with nested code block (non-YAML) in content.

    This should work fine since the nested block isn't ```yaml.
    """
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "What is the correct Python syntax?"
        answer-correct:
          - "Using def"
        answer:
          - "Using function"
        content: |
          Example Python code:

          ```python
          def hello():
              print("Hello")
          ```

          This is the correct syntax.
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    assert '<div class="exam"' in result
    assert "What is the correct Python syntax" in result
    # Non-YAML nested blocks should work fine
    assert "def hello" in result or "Example Python code" in result


def test_multiple_exams_with_code_examples():
    """Test multiple exams where some have code examples."""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Question 1"
        answer-correct:
          - "A"
        ```

        Some text between exams.

        ```yaml
        question: "Question 2 with code example"
        answer-correct:
          - "B"
        content: |
          Example:
          ```python
          x = 5
          ```
        ```
        """
    )

    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, cast(Any, DummyPage()), cast(Any, None))

    # Should have two exams
    assert result.count('<div class="exam"') == 2
    assert "Question 1" in result
    assert "Question 2" in result


if __name__ == "__main__":
    # Run the problematic test to see what happens
    test_exam_with_nested_yaml_in_content()
