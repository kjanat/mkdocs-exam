"""Configuration dataclasses for exam processing."""

from dataclasses import dataclass
from typing import Any

from mkdocs.config import config_options
from mkdocs.config.base import Config


@dataclass
class AnswerConfig:
    """Configuration for processing exam answers."""

    exam_type: str
    answers: list[str]
    correct_idx: list[int]
    answer_feedbacks: list[str]
    answer_weights: list[float]
    exam_id: int
    partial_credit: bool
    exam_data: dict[str, Any]
    question: str


@dataclass
class ExamMetadata:
    """Metadata for building exam HTML wrapper."""

    question: str
    exam_type: str
    points: int
    time_limit: int | None
    media_html: str
    hints_html: str
    answers_html: str
    explanation_html: str
    content_html: str


class ExamPluginConfig(Config):
    """Modern configuration schema for mkdocs-exam plugin.

    This replaces the legacy tuple-based config_scheme with a typed Config subclass
    that provides better validation, autocomplete, and error messages.
    """

    enabled = config_options.Type(bool, default=True)

    default_type = config_options.Choice(
        choices=[
            "choice",
            "truefalse",
            "short-answer",
            "fill",
            "essay",
            "matching",
            "numeric",
            "code-completion",
            "ordering",
            "categorization",
            "hotspot",
        ],
        default="choice",
    )

    default_points = config_options.Type(int, default=1)
    show_answers = config_options.Type(bool, default=False)
    randomize_answers = config_options.Type(bool, default=False)

    theme = config_options.Choice(
        choices=["default", "minimal", "accessible"], default="default"
    )

    strict_validation = config_options.Type(bool, default=False)
