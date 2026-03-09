"""Markdown TPOC question adapter.

Renders a TpocQuestionSet to human-editable markdown
that the user modifies before the TPOC call.
"""

from __future__ import annotations

from pathlib import Path

from pes.domain.tpoc import TpocQuestionSet


class MarkdownTpocAdapter:
    """Renders TPOC questions as editable markdown."""

    def render(self, question_set: TpocQuestionSet) -> str:
        """Render TPOC questions to markdown, ordered by priority."""
        sorted_qs = question_set.sorted_by_priority()
        lines = [
            "# TPOC Questions",
            "",
            "Edit this file before your TPOC call. Add, remove, or reorder questions.",
            "Mark questions with `[x]` after the call to indicate they were asked.",
            "",
        ]

        current_category = None
        for q in sorted_qs:
            category_label = q.category.value.replace("_", " ").title()
            if category_label != current_category:
                current_category = category_label
                lines.append(f"## {current_category}")
                lines.append("")

            rationale = f" *({q.rationale})*" if q.rationale else ""
            lines.append(f"- [ ] **Q{q.question_id}**: {q.text}{rationale}")

        lines.append("")
        return "\n".join(lines)

    def write(self, question_set: TpocQuestionSet, path: Path) -> None:
        """Write TPOC questions to markdown file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(question_set), encoding="utf-8")
