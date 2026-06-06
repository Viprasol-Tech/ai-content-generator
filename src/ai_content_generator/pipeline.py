"""The content-generation pipeline.

``ContentPipeline`` turns a :class:`ContentBrief` into a prompt, calls a
pluggable LLM, then runs deterministic post-processing: it splits the heading
from the body, title-cases the heading, and clamps the body to the brief's
word-count window.

Part of AI Content Generator by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from .models import ContentBrief, GeneratedContent
from .providers import LLM

DEFAULT_TEMPLATE = (
    "Write {tone} marketing content about: {topic}.\n"
    "Audience: {audience}.\n"
    "Keywords to include: {keywords}.\n"
    "Length: between {min_words} and {max_words} words.\n"
    "Start with a short heading on its own line, then the body."
)


def build_prompt(brief: ContentBrief, template: str = DEFAULT_TEMPLATE) -> str:
    """Render a prompt for ``brief`` using ``template``.

    The template is a ``str.format``-style string supporting the placeholders
    ``{topic}``, ``{tone}``, ``{audience}``, ``{keywords}``, ``{min_words}``
    and ``{max_words}``.

    Args:
        brief: The content brief to render.
        template: The prompt template.

    Returns:
        The fully rendered prompt string.
    """
    return template.format(
        topic=brief.topic,
        tone=brief.tone.value,
        audience=brief.audience or "a general audience",
        keywords=", ".join(brief.keywords) if brief.keywords else "none",
        min_words=brief.min_words,
        max_words=brief.max_words,
    )


def split_heading(text: str) -> tuple[str, str]:
    """Split raw LLM output into a heading and a body.

    The first non-empty line becomes the heading; the remainder is the body.
    If there is only one line, that line is the body and the heading is empty.

    Args:
        text: Raw model output.

    Returns:
        A ``(heading, body)`` tuple.
    """
    lines = [ln.strip() for ln in text.strip().splitlines()]
    non_empty = [ln for ln in lines if ln]
    if len(non_empty) <= 1:
        return "", " ".join(non_empty)
    heading = non_empty[0]
    body = " ".join(non_empty[1:])
    return heading, body


def title_case_heading(heading: str) -> str:
    """Title-case a heading, preserving common lowercase stop-words.

    Args:
        heading: The heading text.

    Returns:
        The title-cased heading.
    """
    small = {"a", "an", "and", "the", "of", "to", "in", "on", "for", "with", "or"}
    words = heading.split()
    out: list[str] = []
    for i, word in enumerate(words):
        lower = word.lower()
        if i != 0 and lower in small:
            out.append(lower)
        else:
            out.append(word[:1].upper() + word[1:].lower())
    return " ".join(out)


def clamp_words(body: str, min_words: int, max_words: int) -> tuple[str, int, bool]:
    """Clamp ``body`` to at most ``max_words`` words.

    Words are never invented to satisfy ``min_words`` (we cannot fabricate
    content), but the value is reported so callers can detect under-length
    output. Trailing punctuation on the final kept word is preserved.

    Args:
        body: The body text.
        min_words: Lower bound (used only for the returned flag logic).
        max_words: Upper bound; the body is truncated to this many words.

    Returns:
        A ``(body, word_count, trimmed)`` tuple.
    """
    words = body.split()
    trimmed = len(words) > max_words
    if trimmed:
        kept = words[:max_words]
        last = kept[-1]
        if not last.endswith((".", "!", "?")):
            kept[-1] = last.rstrip(",;:") + "."
        words = kept
    return " ".join(words), len(words), trimmed


class ContentPipeline:
    """Generate and post-process content for a brief using a pluggable LLM.

    Args:
        llm: Any ``Callable[[str], str]`` mapping a prompt to completion text.
        template: The prompt template (defaults to :data:`DEFAULT_TEMPLATE`).
    """

    def __init__(self, llm: LLM, template: str = DEFAULT_TEMPLATE) -> None:
        self.llm = llm
        self.template = template

    def generate(self, brief: ContentBrief) -> GeneratedContent:
        """Run the full pipeline for ``brief``.

        Args:
            brief: The content brief.

        Returns:
            The post-processed :class:`GeneratedContent`.
        """
        prompt = build_prompt(brief, self.template)
        raw = self.llm(prompt)
        heading, body = split_heading(raw)
        heading = title_case_heading(heading)
        body, word_count, trimmed = clamp_words(body, brief.min_words, brief.max_words)
        return GeneratedContent(
            brief=brief,
            prompt=prompt,
            heading=heading,
            body=body,
            word_count=word_count,
            trimmed=trimmed,
        )
