"""
Token counter utility — rough character-based token estimation.

No tiktoken dependency required. Approximation: 4 chars ≈ 1 token.
"""


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    Uses the common approximation of 4 characters per token.
    """
    if not text:
        return 0
    return max(1, len(text) // 4)


def fits_in_budget(text: str, max_tokens: int = 8192) -> bool:
    """Return True if the text fits within the given token budget."""
    return estimate_tokens(text) <= max_tokens


def truncate_to_budget(text: str, max_tokens: int = 8192) -> str:
    """Truncate text to fit within the given token budget."""
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [truncated]"
