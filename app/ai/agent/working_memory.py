"""
Working Memory — Phase 5.3.
Stores intermediate results and collected evidence during an engineering investigation.
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class WorkingMemory(BaseModel):
    """
    In-memory notebook storing the execution steps and factual findings
    gathered by the Task Executor.
    """
    goal: str
    steps: list[dict[str, Any]] = Field(default_factory=list)

    def add_step(self, task_id: int, task_type: str, description: str, result: str, raw_result: Any = None) -> None:
        """Record the findings of a completed task step."""
        self.steps.append({
            "task_id": task_id,
            "type": task_type,
            "description": description,
            "result": result,
            "raw_result": raw_result
        })

    def as_text(self) -> str:
        """Render the accumulated memory as a clear, structured text notebook."""
        if not self.steps:
            return "No evidence collected."

        lines = [
            f"INVESTIGATION GOAL: {self.goal}\n",
            "COLLECTED EVIDENCE:",
            "============================================================"
        ]
        for step in self.steps:
            lines.append(f"\n[Task {step['task_id']} - {step['type'].upper()}]")
            lines.append(f"Objective: {step['description']}")
            lines.append("Findings:")
            lines.append(step['result'])
            lines.append("─" * 60)

        return "\n".join(lines)

    def clear(self) -> None:
        """Reset the working memory."""
        self.steps.clear()
