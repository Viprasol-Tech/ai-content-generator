"""Core data models for the content pipeline.

Part of AI Content Generator by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Tone(str, Enum):
    """Editorial tone applied to generated content."""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    PLAYFUL = "playful"
    AUTHORITATIVE = "authoritative"


class ContentBrief(BaseModel):
    """A structured request describing the content to generate.

    Attributes:
        topic: The subject of the content.
        tone: The editorial tone to write in.
        min_words: Lower bound on the post-processed word count.
        max_words: Upper bound on the post-processed word count.
        audience: Optional description of the intended reader.
        keywords: Optional keywords to weave into the prompt.
    """

    topic: str = Field(min_length=1)
    tone: Tone = Tone.PROFESSIONAL
    min_words: int = Field(default=40, ge=1)
    max_words: int = Field(default=120, ge=1)
    audience: str = ""
    keywords: list[str] = Field(default_factory=list)

    def model_post_init(self, __context: object) -> None:
        """Validate that the word-count window is coherent."""
        if self.max_words < self.min_words:
            raise ValueError("max_words must be >= min_words")


class GeneratedContent(BaseModel):
    """The result of running a brief through the pipeline.

    Attributes:
        brief: The brief that produced this content.
        prompt: The exact prompt sent to the LLM.
        heading: The title-cased heading extracted from the output.
        body: The post-processed body text.
        word_count: Word count of ``body`` after post-processing.
        trimmed: Whether the body was trimmed to ``brief.max_words``.
    """

    brief: ContentBrief
    prompt: str
    heading: str
    body: str
    word_count: int
    trimmed: bool
