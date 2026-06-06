"""Tests for prompt building and post-processing in the pipeline."""

from __future__ import annotations

from ai_content_generator.models import ContentBrief, Tone
from ai_content_generator.pipeline import (
    ContentPipeline,
    build_prompt,
    clamp_words,
    split_heading,
    title_case_heading,
)
from ai_content_generator.providers import FakeLLM, echo_llm


def test_build_prompt_includes_brief_fields() -> None:
    brief = ContentBrief(
        topic="launch day",
        tone=Tone.PLAYFUL,
        min_words=30,
        max_words=80,
        audience="founders",
        keywords=["growth", "speed"],
    )
    prompt = build_prompt(brief)
    assert "launch day" in prompt
    assert "playful" in prompt
    assert "founders" in prompt
    assert "growth, speed" in prompt
    assert "30" in prompt and "80" in prompt


def test_build_prompt_defaults_for_empty_fields() -> None:
    brief = ContentBrief(topic="x")
    prompt = build_prompt(brief)
    assert "a general audience" in prompt
    assert "none" in prompt


def test_split_heading_separates_first_line() -> None:
    heading, body = split_heading("My Heading\n\nThis is the body text.")
    assert heading == "My Heading"
    assert body == "This is the body text."


def test_split_heading_single_line_has_no_heading() -> None:
    heading, body = split_heading("just one line")
    assert heading == ""
    assert body == "just one line"


def test_title_case_heading_keeps_stopwords_lower() -> None:
    assert title_case_heading("the future of work") == "The Future of Work"


def test_clamp_words_truncates_to_max() -> None:
    body = " ".join(f"w{i}" for i in range(50))
    clamped, count, trimmed = clamp_words(body, min_words=10, max_words=20)
    assert count == 20
    assert trimmed is True
    assert clamped.endswith(".")


def test_clamp_words_no_trim_when_within_bounds() -> None:
    body = "one two three four five"
    clamped, count, trimmed = clamp_words(body, min_words=1, max_words=10)
    assert count == 5
    assert trimmed is False
    assert clamped == body


def test_pipeline_enforces_word_count_clamp() -> None:
    brief = ContentBrief(topic="dashboards", min_words=10, max_words=25)
    pipeline = ContentPipeline(FakeLLM(target_words=200))
    result = pipeline.generate(brief)
    assert result.word_count <= 25
    assert result.trimmed is True
    assert result.heading == title_case_heading(result.heading)


def test_pipeline_uses_built_prompt() -> None:
    brief = ContentBrief(topic="echo me")
    pipeline = ContentPipeline(echo_llm)
    result = pipeline.generate(brief)
    # echo_llm returns the prompt; the prompt must match build_prompt output.
    assert result.prompt == build_prompt(brief, pipeline.template)


def test_fake_llm_is_deterministic() -> None:
    llm = FakeLLM(target_words=30)
    assert llm("same prompt") == llm("same prompt")
    assert llm("prompt a") != llm("prompt b")
