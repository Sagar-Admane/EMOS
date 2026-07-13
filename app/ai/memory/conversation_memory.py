"""
Conversation Memory — in-process session history store.

Stores (question, answer) pairs keyed by session_id.
Kept intentionally simple — no Redis dependency required.
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import NamedTuple


class Turn(NamedTuple):
    question: str
    answer: str


# Maximum number of turns to keep per session
_MAX_HISTORY = 10


class ConversationMemory:
    """
    In-memory conversation history.

    Each session_id maps to a deque of (question, answer) Turns.
    The history is bounded to prevent unbounded memory growth.
    """

    def __init__(self, max_history: int = _MAX_HISTORY) -> None:
        self._max_history = max_history
        self._sessions: dict[str, deque[Turn]] = defaultdict(
            lambda: deque(maxlen=self._max_history)
        )

    def add(self, session_id: str, question: str, answer: str) -> None:
        """Record a new Q&A turn for the session."""
        self._sessions[session_id].append(Turn(question=question, answer=answer))

    def get_history(self, session_id: str) -> list[Turn]:
        """Return all turns for a session (oldest first)."""
        return list(self._sessions.get(session_id, []))

    def format_history(self, session_id: str) -> str:
        """
        Return conversation history as a formatted text block
        suitable for inclusion in an LLM prompt.
        """
        turns = self.get_history(session_id)
        if not turns:
            return ""
        lines: list[str] = ["Previous conversation:"]
        for i, turn in enumerate(turns, start=1):
            lines.append(f"  Q{i}: {turn.question}")
            lines.append(f"  A{i}: {turn.answer[:300]}{'...' if len(turn.answer) > 300 else ''}")
        return "\n".join(lines)

    def clear(self, session_id: str) -> None:
        """Clear history for a specific session."""
        if session_id in self._sessions:
            del self._sessions[session_id]

    def session_count(self) -> int:
        """Return the number of active sessions."""
        return len(self._sessions)


# Global singleton instance
memory = ConversationMemory()
