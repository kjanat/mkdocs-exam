import textwrap

from mkdocs_exam.plugin import MkDocsExamPlugin


class DummyPage:
    def __init__(self, meta=None):
        self.meta = meta or {}


def test_exam_block_converts_to_html():
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Are you ready?"
        answer-correct:
          - "Yes!"
        answer:
          - "No!"
          - "Maybe!"
        content: |
          ## Provide some additional content
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)
    expected = (
        "\n"
        '<div class="exam" data-type="choice" data-points="1"><h3>Are you ready?</h3><form><fieldset>'
        '<div><input type="radio" name="answer" value="0" id="exam-0-0" correct><label for="exam-0-0">Yes!</label></div>'
        '<div><input type="radio" name="answer" value="1" id="exam-0-1" ><label for="exam-0-1">No!</label></div>'
        '<div><input type="radio" name="answer" value="2" id="exam-0-2" ><label for="exam-0-2">Maybe!</label></div>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden">## Provide some additional content</section></div>\n'
    )
    assert result == expected


def test_short_answer_question():
    markdown = textwrap.dedent(
        """
        ```yaml
        type: short-answer
        question: "What color is the sky?"
        answer-correct:
          - "blue"
        content: |
          It is often blue.
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)
    expected = (
        "\n"
        '<div class="exam" data-type="short-answer" data-points="1"><h3>What color is the sky?</h3><form><fieldset>'
        '<div><input type="text" name="answer" correct="blue" ></div>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden">It is often blue.</section></div>\n'
    )
    assert result == expected


def test_fill_question():
    markdown = textwrap.dedent(
        """
        ```yaml
        type: fill
        question: "2 + 2 = ___"
        answer-correct:
          - "4"
        content: |
          Easy math.
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)
    expected = (
        "\n"
        '<div class="exam" data-type="fill" data-points="1"><h3>2 + 2 = <input type="text" name="answer" correct="4"></h3><form><fieldset>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden">Easy math.</section></div>\n'
    )
    assert result == expected


def test_true_false_default_answers():
    markdown = textwrap.dedent(
        """
        ```yaml
        type: truefalse
        question: "The Earth orbits the Sun."
        answer-correct:
          - "True"
        content: |
          This is obviously true.
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)
    expected = (
        "\n"
        '<div class="exam" data-type="truefalse" data-points="1"><h3>The Earth orbits the Sun.</h3><form><fieldset>'
        '<div><input type="radio" name="answer" value="0" id="exam-0-0" correct><label for="exam-0-0">True</label></div>'
        '<div><input type="radio" name="answer" value="1" id="exam-0-1" ><label for="exam-0-1">False</label></div>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden">This is obviously true.</section></div>\n'
    )
    assert result == expected


def test_essay_question():
    markdown = textwrap.dedent(
        """
        ```yaml
        type: essay
        question: "Explain the theory of relativity in one paragraph."
        answer-correct:
          - "It deals with space and time."
        content: |
          Provide an explanation.
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)
    expected = (
        "\n"
        '<div class="exam" data-type="essay" data-points="1"><h3>Explain the theory of relativity in one paragraph.</h3><form><fieldset>'
        '<div><textarea name="answer" rows="4" correct="It deals with space and time."></textarea></div>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden">Provide an explanation.</section></div>\n'
    )
    assert result == expected


def test_matching_question():
    markdown = textwrap.dedent(
        """
        ```yaml
        type: matching
        question: "Match the capitals to countries"
        answer:
          - "Paris | France"
          - "Rome | Italy"
          - "Madrid | Spain"
        content: |
          Capitals and their countries.
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)
    expected = (
        "\n"
        '<div class="exam" data-type="matching" data-points="1"><h3>Match the capitals to countries</h3><form><fieldset>'
        '<div><label>Paris <select name="answer" correct="France"><option>France</option><option>Italy</option><option>Spain</option></select></label></div>'
        '<div><label>Rome <select name="answer" correct="Italy"><option>France</option><option>Italy</option><option>Spain</option></select></label></div>'
        '<div><label>Madrid <select name="answer" correct="Spain"><option>France</option><option>Italy</option><option>Spain</option></select></label></div>'
        '</fieldset><button type="submit" class="exam-button">Submit</button>'
        '</form><section class="content hidden">Capitals and their countries.</section></div>\n'
    )
    assert result == expected


def test_exam_disabled_leaves_markdown_unchanged():
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Are you ready?"
        answer-correct:
          - "Yes!"
        answer:
          - "No!"
          - "Maybe!"
        content: |
          ## Provide some additional content
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    page = DummyPage(meta={"exam": "disable"})
    result = plugin.on_page_markdown(markdown, page, None)
    assert result == markdown


def test_multi_document_yaml():
    """Test that multiple exams can be defined in a single YAML block using ---"""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "First question?"
        answer-correct:
          - "Answer 1"
        content: |
          First content
        ---
        question: "Second question?"
        answer-correct:
          - "Answer 2"
        content: |
          Second content
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)
    # Should contain both exams
    assert "First question?" in result
    assert "Second question?" in result
    assert "Answer 1" in result
    assert "Answer 2" in result
    assert "First content" in result
    assert "Second content" in result
    # Should have both exam divs
    assert result.count('<div class="exam"') == 2


def test_environment_variable_interpolation():
    """Test that environment variables are interpolated in YAML"""
    import os

    os.environ["TEST_API_KEY"] = "secret123"
    os.environ["TEST_URL"] = "https://example.com"

    markdown = textwrap.dedent(
        """
        ```yaml
        question: "What is the API key?"
        answer-correct:
          - "${TEST_API_KEY}"
        content: |
          The URL is ${TEST_URL}
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "secret123" in result
    assert "https://example.com" in result
    # Should not contain the ${...} syntax
    assert "${TEST_API_KEY}" not in result
    assert "${TEST_URL}" not in result

    # Clean up
    del os.environ["TEST_API_KEY"]
    del os.environ["TEST_URL"]


def test_environment_variable_with_default():
    """Test that environment variables with defaults work"""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "What is the value?"
        answer-correct:
          - "${NONEXISTENT_VAR:-default_value}"
        content: |
          Testing ${ALSO_MISSING:-fallback}
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "default_value" in result
    assert "fallback" in result
    assert "${NONEXISTENT_VAR" not in result


def test_yaml_anchors_and_aliases():
    """Test that YAML anchors and aliases work correctly"""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Select the correct options"
        answer-correct: &correct_answers
          - "Option A"
          - "Option B"
        answer:
          - "Option C"
        content: |
          Correct answers are referenced
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    # Should contain both correct answers
    assert "Option A" in result
    assert "Option B" in result
    assert "Option C" in result


def test_exam_with_exam_fence():
    """Test that ```exam fence type works in addition to ```yaml"""
    markdown = textwrap.dedent(
        """
        ```exam
        question: "Using exam fence"
        answer-correct:
          - "Yes"
        content: |
          This uses ```exam instead of ```yaml
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "Using exam fence" in result
    assert "Yes" in result
    assert '<div class="exam"' in result


# ============================================================================
# NEW FEATURES TESTS
# ============================================================================


def test_hints_system():
    """Test hints with score penalties"""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "What is the capital of France?"
        answer-correct:
          - "Paris"
        hints:
          - text: "City of Light"
            penalty: 10
          - text: "Eiffel Tower location"
            penalty: 20
        points: 10
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert 'data-points="10"' in result
    assert "exam-hints" in result
    assert "City of Light" in result
    assert "Eiffel Tower location" in result
    assert 'data-penalty="10"' in result
    assert 'data-penalty="20"' in result


def test_explanation_on_correct():
    """Test explanation shown only on correct answer"""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "What is 2 + 2?"
        answer-correct:
          - "4"
        explanation: "Addition combines numbers"
        show-explanation: "on-correct"
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "exam-explanation" in result
    assert "Addition combines numbers" in result
    assert 'data-show="on-correct"' in result


def test_explanation_always():
    """Test explanation always shown"""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Test question"
        answer-correct:
          - "Answer"
        explanation: "This is the explanation"
        show-explanation: "always"
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "exam-explanation" in result
    assert "This is the explanation" in result
    assert 'data-show="always"' in result


def test_answer_feedback():
    """Test answer-specific feedback"""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Which is closest to the Sun?"
        answer-correct:
          - value: "Mercury"
            feedback: "Correct! Mercury is closest."
        answer:
          - value: "Venus"
            feedback: "Venus is second."
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "Mercury" in result
    assert "Venus" in result
    assert "Correct! Mercury is closest." in result
    assert "Venus is second." in result
    assert "data-feedback=" in result


def test_numeric_exam_type():
    """Test numeric answer with tolerance"""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: numeric
        question: "What is π to 2 decimal places?"
        answer-correct:
          - 3.14
        tolerance: 0.01
        unit: ""
        points: 5
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert 'data-type="numeric"' in result
    assert 'type="number"' in result
    assert 'data-correct="3.14"' in result
    assert 'data-tolerance="0.01"' in result
    assert 'data-points="5"' in result


def test_numeric_with_unit():
    """Test numeric answer with unit"""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: numeric
        question: "Meters in a kilometer?"
        answer-correct:
          - 1000
        tolerance: 0
        unit: "m"
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert 'data-type="numeric"' in result
    assert 'data-correct="1000"' in result
    assert 'data-unit="m"' in result


def test_code_completion_exam_type():
    """Test code completion with blanks"""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: code-completion
        question: "Complete the function:"
        template: |
          def add(a, b):
              return a ___ b
        language: python
        blanks:
          - correct: ["+"]
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert 'data-type="code-completion"' in result
    assert "code-blank" in result
    assert "def add(a, b):" in result
    assert "return a" in result


def test_ordering_exam_type():
    """Test ordering/sequencing questions"""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: ordering
        question: "Arrange in order:"
        items:
          - "First"
          - "Second"
          - "Third"
        correct-order: [0, 1, 2]
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert 'data-type="ordering"' in result
    assert "ordering-container" in result
    assert "ordering-item" in result
    assert "First" in result
    assert "Second" in result
    assert "Third" in result
    assert 'data-correct-order="0,1,2"' in result


def test_rich_media_image():
    """Test image media support"""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "What shape is this?"
        media:
          type: image
          src: "https://example.com/triangle.png"
          alt: "A shape"
          caption: "Geometric shape"
        answer-correct:
          - "Triangle"
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "exam-media" in result
    assert "<img" in result
    assert 'src="https://example.com/triangle.png"' in result
    assert 'alt="A shape"' in result
    assert "Geometric shape" in result


def test_rich_media_video():
    """Test video media support"""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "What is shown?"
        media:
          type: video
          src: "https://example.com/video.mp4"
          caption: "Demo video"
        answer-correct:
          - "Demo"
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert "exam-media" in result
    assert "<video" in result
    assert 'src="https://example.com/video.mp4"' in result
    assert "Demo video" in result


def test_time_limit():
    """Test time limit with countdown"""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Quick question"
        answer-correct:
          - "Fast"
        time-limit: 30
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert 'data-time-limit="30"' in result


def test_custom_points():
    """Test custom point values"""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Hard question"
        answer-correct:
          - "Answer"
        points: 25
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    assert 'data-points="25"' in result


def test_xss_prevention():
    """Test that HTML is escaped to prevent XSS"""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "<script>alert('xss')</script>Question"
        answer-correct:
          - "<img src=x onerror=alert(1)>"
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    # Should escape HTML tags
    assert "<script>" not in result
    assert "&lt;script&gt;" in result
    assert "<img src=x" not in result
    assert "&lt;img" in result


def test_invalid_exam_type_rejected():
    """Test that invalid exam types are rejected and default to choice"""
    markdown = textwrap.dedent(
        """
        ```yaml
        type: malicious-type
        question: "Test"
        answer-correct:
          - "Answer"
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    # Should log warning and default to 'choice' type
    assert '<div class="exam"' in result
    assert 'data-type="choice"' in result
    # Invalid type should not appear in output
    assert "malicious-type" not in result


def test_combined_features():
    """Test multiple features together"""
    markdown = textwrap.dedent(
        """
        ```yaml
        question: "Combined test"
        answer-correct:
          - value: "Correct"
            feedback: "Great job!"
        answer:
          - value: "Wrong"
            feedback: "Try again"
        hints:
          - text: "Think carefully"
            penalty: 15
        explanation: "This is why"
        show-explanation: "always"
        points: 20
        time-limit: 60
        ```
        """
    )
    plugin = MkDocsExamPlugin()
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    # Check all features are present
    assert 'data-points="20"' in result
    assert 'data-time-limit="60"' in result
    assert "exam-hints" in result
    assert 'data-penalty="15"' in result
    assert "exam-explanation" in result
    assert 'data-show="always"' in result
    assert "Great job!" in result
    assert "Try again" in result
