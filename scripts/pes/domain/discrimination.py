"""Discrimination domain models -- value objects for proposal discrimination.

Pure domain objects with no infrastructure imports.
DiscriminatorItem captures a single discriminator with category, claim, and evidence.
DiscriminationTable aggregates discriminator items.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DiscriminatorItem:
    """A single discriminator item with category, claim, and evidence citation.

    Frozen value object -- immutable after creation.
    """

    category: str
    claim: str
    evidence_citation: str


@dataclass
class DiscriminationTable:
    """Collection of discriminator items for a proposal."""

    items: list[DiscriminatorItem] = field(default_factory=list)
