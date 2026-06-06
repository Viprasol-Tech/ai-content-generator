"""Generate multiple deterministic variations from a single brief.

Each variation perturbs the prompt with a distinct, index-derived "angle"
instruction, so a deterministic LLM yields distinct prompts and outputs while
the underlying brief stays fixed.

Part of AI Content Generator by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from .models import ContentBrief, GeneratedContent
from .pipeline import DEFAULT_TEMPLATE, ContentPipeline
from .providers import LLM

# Distinct creative angles cycled through by variation index.
ANGLES = (
    "Lead with a surprising statistic.",
    "Open with a relatable question.",
    "Frame it as a short success story.",
    "Emphasise the core benefit first.",
    "Use a bold, contrarian hook.",
    "Start with a clear call to action.",
)


def angle_for(index: int) -> str:
    """Return the deterministic angle instruction for ``index``.

    Args:
        index: Zero-based variation index.

    Returns:
        The angle instruction string.
    """
    return ANGLES[index % len(ANGLES)]


def variation_template(index: int, base_template: str = DEFAULT_TEMPLATE) -> str:
    """Build the prompt template for variation ``index``.

    The angle for the index is appended to ``base_template`` so each variation
    produces a deterministically different prompt.

    Args:
        index: Zero-based variation index.
        base_template: The template to extend.

    Returns:
        A new template string for this variation.
    """
    return f"{base_template}\nAngle ({index + 1}): {angle_for(index)}"


def generate_variations(
    brief: ContentBrief,
    llm: LLM,
    count: int,
    base_template: str = DEFAULT_TEMPLATE,
) -> list[GeneratedContent]:
    """Generate ``count`` distinct variations for ``brief``.

    Args:
        brief: The shared content brief.
        llm: The pluggable LLM provider.
        count: Number of variations to produce (must be >= 1).
        base_template: Base prompt template to vary.

    Returns:
        A list of ``count`` :class:`GeneratedContent` items.

    Raises:
        ValueError: If ``count`` is less than 1.
    """
    if count < 1:
        raise ValueError("count must be >= 1")
    results: list[GeneratedContent] = []
    for i in range(count):
        pipeline = ContentPipeline(llm, template=variation_template(i, base_template))
        results.append(pipeline.generate(brief))
    return results
