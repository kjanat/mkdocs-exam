"""Constants and configuration for the mkdocs-exam plugin."""

from typing import Final


class ExamFields:
    """Field names used in exam block syntax."""

    TYPE: Final[str] = "type:"
    QUESTION: Final[str] = "question:"
    ANSWER: Final[str] = "answer:"
    ANSWER_CORRECT: Final[str] = "answer-correct:"
    CONTENT: Final[str] = "content:"


class QuestionTypes:
    """Supported question types."""

    CHOICE: Final[str] = "choice"
    TRUEFALSE: Final[str] = "truefalse"
    SHORT_ANSWER: Final[str] = "short-answer"
    FILL: Final[str] = "fill"
    ESSAY: Final[str] = "essay"
    MATCHING: Final[str] = "matching"

    @classmethod
    def all(cls) -> list[str]:
        """Return list of all supported question types."""
        return [cls.CHOICE, cls.TRUEFALSE, cls.SHORT_ANSWER, cls.FILL, cls.ESSAY, cls.MATCHING]


class ExamTags:
    """HTML tags for exam blocks."""

    START: Final[str] = "<exam>"
    END: Final[str] = "</exam>"


class CSSClasses:
    """CSS class names used in generated HTML."""

    EXAM: Final[str] = "exam"
    CONTENT: Final[str] = "content"
    HIDDEN: Final[str] = "hidden"
    CORRECT: Final[str] = "correct"
    WRONG: Final[str] = "wrong"
    EXAM_BUTTON: Final[str] = "exam-button"
    RESET_BUTTON: Final[str] = "reset-button"
    SCORE: Final[str] = "exam-score"


class DefaultConfig:
    """Default configuration values for the plugin."""

    SUBMIT_TEXT: Final[str] = "Submit"
    RESET_TEXT: Final[str] = "Try Again"
    SHOW_SCORE: Final[bool] = True
    ALLOW_RETRY: Final[bool] = True
    ESSAY_ROWS: Final[int] = 4
    TRUE_VALUES: Final[list[str]] = ["True", "False"]
    FILL_PLACEHOLDER: Final[str] = "___"
