"""Configuration dataclasses for exam processing."""

from dataclasses import dataclass
from typing import Any


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
