"""Shared strategy brief fixtures used across unit and acceptance tests."""

from __future__ import annotations

from pes.domain.strategy import StrategyBrief, StrategySection

SAMPLE_BRIEF = StrategyBrief(
    sections=[
        StrategySection(key="technical_approach", title="Technical Approach", content="approach"),
        StrategySection(key="trl", title="TRL", content="trl assessment"),
        StrategySection(key="teaming", title="Teaming", content="teaming plan"),
        StrategySection(key="phase_iii", title="Phase III", content="commercialization"),
        StrategySection(key="budget", title="Budget", content="budget plan"),
        StrategySection(key="risks", title="Risks", content="risk assessment"),
    ],
    tpoc_available=True,
)
