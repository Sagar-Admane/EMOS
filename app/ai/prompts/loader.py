"""
PromptLoader — reads skill prompt templates from .txt files.

Prompts live in app/ai/prompts/<skill_name>.txt.
Loaded prompts are cached in memory after the first read.
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Absolute path to the prompts directory
_PROMPTS_DIR = Path(__file__).parent

# In-memory cache: skill_name → prompt text
_cache: dict[str, str] = {}


class PromptLoader:
    """
    Loads and caches prompt templates from the prompts directory.
    Prompts are plain text files named <skill_name>.txt.
    """

    @staticmethod
    def load(skill_name: str) -> str:
        """
        Return the prompt text for the given skill name.
        Raises FileNotFoundError if the prompt file does not exist.
        """
        if skill_name in _cache:
            return _cache[skill_name]

        prompt_path = _PROMPTS_DIR / f"{skill_name}.txt"
        if not prompt_path.exists():
            logger.error("Prompt file not found: %s", prompt_path)
            raise FileNotFoundError(
                f"No prompt file found for skill '{skill_name}' at {prompt_path}"
            )

        text = prompt_path.read_text(encoding="utf-8").strip()
        _cache[skill_name] = text
        logger.debug("Loaded prompt for skill '%s' (%d chars)", skill_name, len(text))
        return text

    @staticmethod
    def clear_cache() -> None:
        """Clear the prompt cache (useful in tests)."""
        _cache.clear()
