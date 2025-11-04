"""Parser for exam block syntax."""

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from .constants import ExamFields, ExamTags, QuestionTypes

logger = logging.getLogger("mkdocs.plugins.mkdocs-exam")


class ExamParseError(Exception):
    """Raised when an exam block cannot be parsed."""

    pass


@dataclass
class ExamData:
    """Structured data from a parsed exam block."""

    question_type: str = QuestionTypes.CHOICE
    question: str = ""
    answers: list[str] = field(default_factory=list)
    correct_indices: list[int] = field(default_factory=list)
    content_lines: list[str] = field(default_factory=list)
    exam_id: int = 0

    def validate(self) -> list[str]:
        """
        Validate the exam data structure.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors: list[str] = []

        if not self.question.strip():
            errors.append("Question is required but was empty or missing")

        if self.question_type not in QuestionTypes.all():
            errors.append(f"Unknown question type: {self.question_type}")

        # Validate based on question type
        if self.question_type in {QuestionTypes.CHOICE, QuestionTypes.TRUEFALSE}:
            if not self.answers and self.question_type != QuestionTypes.TRUEFALSE:
                errors.append(f"{self.question_type} questions require at least one answer")
            if not self.correct_indices and self.question_type != QuestionTypes.TRUEFALSE:
                errors.append(f"{self.question_type} questions require at least one correct answer")

        elif self.question_type in {QuestionTypes.SHORT_ANSWER, QuestionTypes.FILL}:
            if not self.answers:
                errors.append(f"{self.question_type} questions require at least one answer-correct")

        elif self.question_type == QuestionTypes.MATCHING:
            if not self.answers:
                errors.append("Matching questions require at least one answer pair")
            for i, ans in enumerate(self.answers):
                if "|" not in ans:
                    errors.append(f"Matching answer {i+1} must contain a pipe separator (|): {ans}")

        return errors


def find_exam_blocks(markdown: str) -> list[str]:
    """
    Find all exam blocks in markdown content.

    Args:
        markdown: Markdown content to search.

    Returns:
        List of exam block contents (without tags).
    """
    pattern = f"{re.escape(ExamTags.START)}(.*?){re.escape(ExamTags.END)}"
    matches = re.findall(pattern, markdown, re.DOTALL)
    return matches


def parse_exam_block(block_content: str, exam_id: int = 0) -> ExamData:
    """
    Parse a single exam block into structured data.

    Args:
        block_content: Content between <exam> tags.
        exam_id: Unique identifier for this exam.

    Returns:
        ExamData instance with parsed content.

    Raises:
        ExamParseError: If the block cannot be parsed.
    """
    exam_data = ExamData(exam_id=exam_id)

    try:
        # Split into lines and remove empty ones
        lines = [ln.strip() for ln in block_content.splitlines() if ln.strip()]

        if not lines:
            raise ExamParseError("Exam block is empty")

        # Find content section
        content_idx = None
        for i, line in enumerate(lines):
            if line.strip() == ExamFields.CONTENT:
                content_idx = i
                break

        if content_idx is None:
            raise ExamParseError(f"Exam block missing '{ExamFields.CONTENT}' section")

        # Parse header lines
        header_lines = lines[:content_idx]
        exam_data.content_lines = lines[content_idx + 1 :]

        # Parse header fields
        for line in header_lines:
            try:
                if line.startswith(ExamFields.TYPE):
                    exam_data.question_type = line.split(ExamFields.TYPE, 1)[1].strip().lower()
                elif line.startswith(ExamFields.QUESTION):
                    exam_data.question = line.split(ExamFields.QUESTION, 1)[1].strip()
                elif line.startswith(ExamFields.ANSWER_CORRECT):
                    answer = line.split(ExamFields.ANSWER_CORRECT, 1)[1].strip()
                    exam_data.answers.append(answer)
                    exam_data.correct_indices.append(len(exam_data.answers) - 1)
                elif line.startswith(ExamFields.ANSWER):
                    answer = line.split(ExamFields.ANSWER, 1)[1].strip()
                    exam_data.answers.append(answer)
            except IndexError as e:
                logger.warning(f"Failed to parse line '{line}': {e}")
                continue

        # Handle true/false defaults
        if exam_data.question_type == QuestionTypes.TRUEFALSE:
            if not exam_data.answers:
                exam_data.answers = ["True", "False"]
                exam_data.correct_indices = [0]
            elif len(exam_data.answers) == 1:
                # If only one answer provided, add the opposite
                if exam_data.answers[0].strip().lower() in {"true", "yes"}:
                    exam_data.answers.append("False")
                else:
                    exam_data.answers.append("True")

        # Validate the parsed data
        validation_errors = exam_data.validate()
        if validation_errors:
            error_msg = "Exam validation failed:\n  - " + "\n  - ".join(validation_errors)
            raise ExamParseError(error_msg)

        return exam_data

    except ExamParseError:
        raise
    except Exception as e:
        raise ExamParseError(f"Unexpected error parsing exam block: {e}") from e


def replace_exam_blocks(markdown: str, replacements: dict[str, str]) -> str:
    """
    Replace exam blocks in markdown with HTML.

    Args:
        markdown: Original markdown content.
        replacements: Dict mapping original exam blocks to replacement HTML.

    Returns:
        Markdown with exam blocks replaced.
    """
    for original, replacement in replacements.items():
        markdown = markdown.replace(original, replacement)
    return markdown
