"""Command-line interface for AI Content Generator.

``ai-content-generator demo`` generates a few content variations from a brief
using the built-in deterministic fake LLM — no API keys, no network.

Part of AI Content Generator by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

import typer
from rich.console import Console

from ai_content_generator import __version__
from ai_content_generator.models import ContentBrief, Tone
from ai_content_generator.providers import FakeLLM
from ai_content_generator.variations import generate_variations

app = typer.Typer(add_completion=False, help="AI Content Generator — by Viprasol Tech.")
console = Console()


@app.command()
def version() -> None:
    """Print the installed version."""
    console.print(f"ai-content-generator [bold cyan]{__version__}[/] - by Viprasol Tech")


@app.command()
def demo(
    topic: str = typer.Option("our new analytics dashboard", help="Topic to write about."),
    tone: Tone = typer.Option(Tone.PROFESSIONAL, help="Editorial tone."),
    count: int = typer.Option(3, min=1, help="Number of variations to generate."),
    max_words: int = typer.Option(40, min=1, help="Max words per variation."),
) -> None:
    """Generate content variations from a brief using the offline fake LLM."""
    brief = ContentBrief(
        topic=topic,
        tone=tone,
        min_words=20,
        max_words=max_words,
        audience="busy product teams",
        keywords=["insights", "fast", "no-code"],
    )
    llm = FakeLLM(target_words=max_words + 20)
    variations = generate_variations(brief, llm, count=count)

    console.print(f"Brief topic: [bold]{brief.topic}[/]  (tone: {brief.tone.value})")
    console.print(f"Generated [bold green]{len(variations)}[/] variations:\n")
    for i, item in enumerate(variations, start=1):
        flag = " [yellow](trimmed)[/]" if item.trimmed else ""
        console.print(f"[bold cyan]Variation {i}[/]: {item.heading}{flag}")
        console.print(f"  words: {item.word_count}")
        console.print(f"  {item.body}\n")


if __name__ == "__main__":
    app()
