"""Tests for deterministic multi-variation generation."""

from __future__ import annotations

import pytest

from ai_content_generator.models import ContentBrief
from ai_content_generator.providers import FakeLLM
from ai_content_generator.variations import (
    ANGLES,
    angle_for,
    generate_variations,
    variation_template,
)


def test_angle_for_cycles() -> None:
    assert angle_for(0) == ANGLES[0]
    assert angle_for(len(ANGLES)) == ANGLES[0]
    assert angle_for(1) != angle_for(0)


def test_variation_template_differs_by_index() -> None:
    t0 = variation_template(0)
    t1 = variation_template(1)
    assert t0 != t1
    assert "Angle (1)" in t0
    assert "Angle (2)" in t1


def test_generate_variations_returns_n_distinct_prompts_and_outputs() -> None:
    brief = ContentBrief(topic="our product", min_words=10, max_words=40)
    llm = FakeLLM(target_words=60)
    results = generate_variations(brief, llm, count=4)

    assert len(results) == 4
    prompts = {r.prompt for r in results}
    bodies = {r.body for r in results}
    assert len(prompts) == 4  # all prompts distinct
    assert len(bodies) == 4  # deterministic fake yields distinct bodies


def test_generate_variations_is_reproducible() -> None:
    brief = ContentBrief(topic="repeat", min_words=5, max_words=30)
    llm = FakeLLM(target_words=50)
    a = generate_variations(brief, llm, count=3)
    b = generate_variations(brief, llm, count=3)
    assert [x.body for x in a] == [x.body for x in b]


def test_generate_variations_rejects_non_positive_count() -> None:
    brief = ContentBrief(topic="x")
    with pytest.raises(ValueError):
        generate_variations(brief, FakeLLM(), count=0)
