"""PDC gate rule evaluation -- domain logic for pre-draft checklist prerequisites."""

from __future__ import annotations

from typing import Any

from pes.domain.rules import EnforcementRule


class PdcGateEvaluator:
    """Evaluate PDC gate rules against proposal state.

    Blocks Wave 5 entry when any section has RED Tier 1 or Tier 2 PDC items.
    PDC status is read from state['pdc_status'] (schema v2.0.0).
    """

    def triggers(self, rule: EnforcementRule, state: dict[str, Any], tool_name: str, tool_context: dict[str, Any] | None = None) -> bool:
        """Check if a PDC gate rule blocks the given tool invocation.

        Returns True if the rule triggers (blocks the action).
        """
        condition = rule.condition
        target_wave = condition.get("target_wave")

        if target_wave is None:
            return False

        if f"wave_{target_wave}" not in tool_name:
            return False

        if not condition.get("requires_pdc_green"):
            return False

        pdc_status = state.get("pdc_status", {})
        if not pdc_status:
            return False

        for _section_id, section_pdc in pdc_status.items():
            if section_pdc.get("tier_1") == "RED" or section_pdc.get("tier_2") == "RED":
                return True

        return False

    def build_block_message(self, rule: EnforcementRule, state: dict[str, Any]) -> str:
        """Build a detailed block message listing RED sections and items."""
        pdc_status = state.get("pdc_status", {})
        red_sections: list[str] = []

        for section_id, section_pdc in pdc_status.items():
            red_tiers: list[str] = []
            if section_pdc.get("tier_1") == "RED":
                red_tiers.append("Tier 1")
            if section_pdc.get("tier_2") == "RED":
                red_tiers.append("Tier 2")
            if red_tiers:
                items = section_pdc.get("red_items", [])
                items_str = f" ({', '.join(items)})" if items else ""
                red_sections.append(
                    f"Section {section_id}: {' and '.join(red_tiers)} RED{items_str}"
                )

        if red_sections:
            details = "; ".join(red_sections)
            return f"{rule.message}. RED PDC items: {details}"
        return rule.message
