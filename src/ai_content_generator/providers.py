"""Pluggable LLM providers for the content pipeline.

An LLM provider is any ``Callable[[str], str]`` — it takes a prompt and returns
generated text. Real providers (OpenAI, Anthropic, a local server, etc.) are
supplied by the caller; this module ships a deterministic ``FakeLLM`` so the
demo and the test-suite run fully offline with no API keys and no network.

Part of AI Content Generator by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable

# An LLM provider maps a prompt string to a completion string.
LLM = Callable[[str], str]

_LOREM = [
    "discover",
    "unlock",
    "proven",
    "simple",
    "powerful",
    "trusted",
    "modern",
    "seamless",
    "smart",
    "reliable",
    "effortless",
    "results",
    "today",
    "teams",
    "growth",
    "value",
    "clear",
    "fast",
    "bold",
    "insight",
    "strategy",
    "craft",
    "build",
    "ship",
    "deliver",
    "scale",
    "focus",
    "impact",
]


class FakeLLM:
    """A deterministic, offline LLM stand-in for demos and tests.

    The output is derived from a stable hash of the prompt, so the same prompt
    always yields the same text, and different prompts yield different text.
    It produces a short heading line followed by a body of pseudo-words whose
    length is controlled by ``target_words``.

    Args:
        target_words: Approximate number of words to emit in the body.
        seed: Extra salt mixed into the hash to vary a whole run.
    """

    def __init__(self, target_words: int = 60, seed: int = 0) -> None:
        self.target_words = max(1, target_words)
        self.seed = seed

    def _rng_stream(self, prompt: str) -> list[int]:
        """Return a deterministic stream of ints derived from the prompt."""
        digest = hashlib.sha256(f"{self.seed}:{prompt}".encode()).digest()
        # Expand the 32-byte digest into a longer stream by re-hashing.
        stream: list[int] = list(digest)
        while len(stream) < self.target_words + 8:
            digest = hashlib.sha256(digest).digest()
            stream.extend(digest)
        return stream

    def __call__(self, prompt: str) -> str:
        """Generate deterministic text for ``prompt``."""
        stream = self._rng_stream(prompt)
        heading_words = [_LOREM[stream[i] % len(_LOREM)] for i in range(3)]
        heading = " ".join(heading_words)
        body_words = [_LOREM[stream[i + 3] % len(_LOREM)] for i in range(self.target_words)]
        body = " ".join(body_words)
        return f"{heading}\n\n{body}."


def echo_llm(prompt: str) -> str:
    """A trivial LLM provider that echoes the prompt back.

    Useful as the simplest possible deterministic provider in tests.

    Args:
        prompt: The prompt to echo.

    Returns:
        The prompt unchanged.
    """
    return prompt
