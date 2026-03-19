"""Topic scoring service -- five-dimension fit scoring for SBIR/STTR topics.

Application service (driving port) that scores candidate topics against
a company profile using five weighted dimensions:
  - Subject Matter Expertise (SME): 0.35
  - Past Performance (PP): 0.25
  - Certifications (Cert): 0.15
  - Eligibility (Elig): 0.15
  - STTR/Partnership (STTR): 0.10

Recommendation thresholds:
  - GO: composite >= 0.60 with no disqualifiers
  - EVALUATE: composite >= 0.30 (or data gaps)
  - NO-GO: composite < 0.30 or disqualifier present
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Dimension weights
WEIGHT_SME = 0.35
WEIGHT_PP = 0.25
WEIGHT_CERT = 0.15
WEIGHT_ELIG = 0.15
WEIGHT_STTR = 0.10

# Recommendation thresholds
THRESHOLD_GO = 0.60
THRESHOLD_EVALUATE = 0.30

# Clearance hierarchy: higher index = higher clearance
CLEARANCE_LEVELS = {
    "none": 0,
    "confidential": 1,
    "secret": 2,
    "top_secret": 3,
}


@dataclass
class ScoredTopic:
    """Result of scoring a single topic."""

    topic_id: str
    composite_score: float
    dimensions: dict[str, float]
    recommendation: str
    disqualifiers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    key_personnel_match: list[str] = field(default_factory=list)


class TopicScoringService:
    """Driving port for five-dimension topic scoring.

    Scores topics against a company profile. Pure domain logic -- no I/O.
    """

    def score_topic(
        self,
        topic: dict[str, Any],
        profile: dict[str, Any],
        partner_profile: dict[str, Any] | None = None,
    ) -> ScoredTopic:
        """Score a single topic against the company profile.

        Args:
            topic: Topic metadata dict with topic_id, title, program,
                   requires_clearance, agency, etc.
            profile: Company profile dict.
            partner_profile: Optional partner profile dict. When provided,
                   SME uses combined capabilities and STTR uses partner type.

        Returns:
            ScoredTopic with composite score, dimensions, and recommendation.
        """
        disqualifiers: list[str] = []
        warnings: list[str] = []

        # Build effective profile for scoring (merged capabilities when partnered)
        effective_profile = self._build_effective_profile(profile, partner_profile)

        # Check disqualifiers against effective profile
        disqualifiers.extend(self._check_disqualifiers(topic, effective_profile))

        # Score each dimension using effective profile
        sme = self._score_sme(topic, effective_profile)
        pp = self._score_past_performance(topic, profile, warnings)
        cert = self._score_certifications(topic, profile)
        elig = self._score_eligibility(topic, profile)
        sttr = self._score_sttr(topic, effective_profile)

        dimensions = {
            "subject_matter": sme,
            "past_performance": pp,
            "certifications": cert,
            "eligibility": elig,
            "sttr": sttr,
        }

        composite = self._compute_composite(dimensions)

        # Match key personnel from both company and partner
        key_personnel = self._match_key_personnel(topic, effective_profile)

        # Determine recommendation
        recommendation = self._recommend(
            composite, dimensions, disqualifiers, profile, warnings,
        )

        return ScoredTopic(
            topic_id=topic.get("topic_id", ""),
            composite_score=round(composite, 2),
            dimensions={k: round(v, 2) for k, v in dimensions.items()},
            recommendation=recommendation,
            disqualifiers=disqualifiers,
            warnings=warnings,
            key_personnel_match=key_personnel,
        )

    def score_batch(
        self,
        topics: list[dict[str, Any]],
        profile: dict[str, Any],
        partner_profile: dict[str, Any] | None = None,
    ) -> list[ScoredTopic]:
        """Score a batch of topics and return sorted by composite descending.

        Args:
            topics: List of topic dicts.
            profile: Company profile dict.
            partner_profile: Optional partner profile for partnership-aware scoring.

        Returns:
            List of ScoredTopic sorted by composite_score descending.
        """
        results = [self.score_topic(t, profile, partner_profile) for t in topics]
        results.sort(key=lambda r: r.composite_score, reverse=True)
        return results

    def apply_recommendation(self, composite_score: float) -> str:
        """Apply recommendation thresholds to a raw composite score.

        This is a convenience for scenarios that test threshold rules
        directly without full topic/profile context.

        Args:
            composite_score: Pre-computed composite score.

        Returns:
            Recommendation string: GO, EVALUATE, or NO-GO.
        """
        if composite_score >= THRESHOLD_GO:
            return "GO"
        if composite_score >= THRESHOLD_EVALUATE:
            return "EVALUATE"
        return "NO-GO"

    # ----- Private scoring methods -----

    def _build_effective_profile(
        self,
        profile: dict[str, Any],
        partner_profile: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Build an effective profile merging company and partner data.

        When a partner is provided, combines capabilities and key_personnel
        from both entities. Also synthesizes research_institution_partners
        from the partner profile for STTR scoring.

        Returns a new dict (never mutates the originals).
        """
        if partner_profile is None:
            return profile

        effective = dict(profile)

        # Union of capabilities (deduplicated, case-insensitive, preserving original case)
        company_caps = profile.get("capabilities", [])
        partner_caps = partner_profile.get("capabilities", [])
        seen_lower: set[str] = set()
        combined_caps: list[str] = []
        for cap in company_caps + partner_caps:
            if cap.lower() not in seen_lower:
                seen_lower.add(cap.lower())
                combined_caps.append(cap)
        effective["capabilities"] = combined_caps

        # Merge key personnel
        company_personnel = profile.get("key_personnel", [])
        partner_personnel = partner_profile.get("key_personnel", [])
        effective["key_personnel"] = company_personnel + partner_personnel

        # Synthesize research_institution_partners for STTR scoring
        partner_type = partner_profile.get("partner_type", "")
        partner_name = partner_profile.get("partner_name", "")
        if partner_type and partner_name:
            effective["research_institution_partners"] = [
                {"name": partner_name, "type": partner_type}
            ]

        return effective

    def _check_disqualifiers(
        self,
        topic: dict[str, Any],
        profile: dict[str, Any],
    ) -> list[str]:
        """Check for hard disqualifiers."""
        disqualifiers: list[str] = []

        # Clearance check
        required = topic.get("requires_clearance", "none").lower()
        certs = profile.get("certifications", {})
        held = certs.get("security_clearance", "none").lower()

        req_level = CLEARANCE_LEVELS.get(required, 0)
        held_level = CLEARANCE_LEVELS.get(held, 0)

        if req_level > held_level and req_level > 0:
            held_label = held.replace("_", " ").title()
            req_label = "TS" if required == "top_secret" else required.replace("_", " ").title()
            disqualifiers.append(
                f"Requires {req_label} clearance (profile: {held_label})"
            )

        # STTR without research partner
        program = topic.get("program", "SBIR").upper()
        partners = profile.get("research_institution_partners", [])
        if program == "STTR" and not partners:
            disqualifiers.append("No research institution partner")

        return disqualifiers

    def _score_sme(
        self,
        topic: dict[str, Any],
        profile: dict[str, Any],
    ) -> float:
        """Score subject matter expertise based on keyword overlap.

        Full phrase matches (capability substring in title) score higher
        than partial word overlaps. Score is normalized by total capabilities.
        """
        capabilities = [c.lower() for c in profile.get("capabilities", [])]
        if not capabilities:
            return 0.0

        title = topic.get("title", "").lower()

        # Two-tier matching: full phrase match (1.0) vs partial word overlap (0.3)
        total_score = 0.0
        for cap in capabilities:
            if cap in title:
                # Full capability phrase found in title
                total_score += 1.0
            else:
                # Check individual word overlap (weaker signal)
                cap_words = set(cap.split())
                title_words = set(title.split())
                overlap = cap_words & title_words
                if overlap:
                    total_score += 0.3 * len(overlap) / len(cap_words)

        ratio = total_score / len(capabilities)
        # Map ratio to score range: high ratio -> high SME
        if ratio >= 0.3:
            return min(0.70 + ratio, 1.0)
        if ratio >= 0.1:
            return 0.30 + ratio * 2.0
        if ratio > 0:
            return ratio * 3.0
        return 0.0

    def _score_past_performance(
        self,
        topic: dict[str, Any],
        profile: dict[str, Any],
        warnings: list[str],
    ) -> float:
        """Score past performance relevance.

        Strong match: same agency AND domain overlap with positive outcome.
        Medium match: same agency OR strong domain overlap (not both).
        Weak match: partial domain overlap across different agency.
        """
        past_perf = profile.get("past_performance", [])
        if not past_perf:
            warnings.append("Profile incomplete: past_performance empty")
            return 0.0

        topic_agency = topic.get("agency", "").lower()
        title = topic.get("title", "").lower()
        title_words = set(title.lower().split()) - {"for", "the", "a", "of", "in", "and", "or"}

        best_score = 0.0
        for pp in past_perf:
            pp_agency = pp.get("agency", "").lower()
            pp_area = pp.get("topic_area", "").lower()
            outcome = pp.get("outcome", "").lower()

            agency_match = pp_agency == topic_agency
            # Domain overlap: intersection of meaningful words
            area_words = set(pp_area.lower().split()) - {"for", "the", "a", "of", "in", "and", "or"}
            overlap_count = len(area_words & title_words)
            domain_overlap = overlap_count / max(len(area_words), 1)

            if agency_match and domain_overlap >= 0.5:
                # Strong match: same agency + significant domain overlap
                outcome_factor = 1.0 if outcome in ("awarded", "won", "completed") else 0.7
                score = 0.80 * outcome_factor
                best_score = max(best_score, score)
            elif agency_match and domain_overlap > 0:
                # Same agency, weak domain overlap
                score = 0.50
                best_score = max(best_score, score)
            elif domain_overlap >= 0.5:
                # Different agency, strong domain overlap
                score = 0.40
                best_score = max(best_score, score)
            elif agency_match:
                # Same agency, no domain overlap
                score = 0.30
                best_score = max(best_score, score)

        return best_score

    def _score_certifications(
        self,
        topic: dict[str, Any],
        profile: dict[str, Any],
    ) -> float:
        """Score certifications and registrations."""
        certs = profile.get("certifications", {})
        if not certs:
            return 0.0

        sam = certs.get("sam_gov", {})
        if not sam.get("active", False):
            return 0.0

        # Active SAM = baseline 1.0, degrade if missing required certs
        score = 1.0

        # Check if topic requires ITAR
        # (simplified: not all topics specify this)
        return score

    def _score_eligibility(
        self,
        topic: dict[str, Any],
        profile: dict[str, Any],
    ) -> float:
        """Score phase eligibility."""
        employee_count = profile.get("employee_count", 0)

        # SBIR requires < 500 employees
        if employee_count >= 500:
            return 0.0

        # Phase I: small business status sufficient
        phase = topic.get("phase", "I")
        if phase == "I":
            return 1.0

        # Phase II: would need prior Phase I award (simplified)
        return 0.5

    def _score_sttr(
        self,
        topic: dict[str, Any],
        profile: dict[str, Any],
    ) -> float:
        """Score STTR research institution requirements."""
        program = topic.get("program", "SBIR").upper()
        if program != "STTR":
            return 1.0  # Not STTR, no institution needed

        partners = profile.get("research_institution_partners", [])
        if partners:
            return 1.0
        return 0.0

    def _compute_composite(self, dimensions: dict[str, float]) -> float:
        """Compute weighted composite score."""
        composite = (
            dimensions["subject_matter"] * WEIGHT_SME
            + dimensions["past_performance"] * WEIGHT_PP
            + dimensions["certifications"] * WEIGHT_CERT
            + dimensions["eligibility"] * WEIGHT_ELIG
            + dimensions["sttr"] * WEIGHT_STTR
        )
        # Clamp to [0.0, 1.0]
        return max(0.0, min(1.0, composite))

    def _match_key_personnel(
        self,
        topic: dict[str, Any],
        profile: dict[str, Any],
    ) -> list[str]:
        """Find key personnel whose expertise matches the topic."""
        personnel = profile.get("key_personnel", [])
        title = topic.get("title", "").lower()
        matches = []
        for person in personnel:
            expertise = [e.lower() for e in person.get("expertise", [])]
            if any(exp in title for exp in expertise):
                matches.append(person.get("name", ""))
        return matches

    def _recommend(
        self,
        composite: float,
        dimensions: dict[str, float],
        disqualifiers: list[str],
        profile: dict[str, Any],
        warnings: list[str],
    ) -> str:
        """Determine recommendation based on score and disqualifiers."""
        # Disqualifiers always produce NO-GO
        if disqualifiers:
            return "NO-GO"

        # Eligibility = 0.0 always NO-GO
        if dimensions.get("eligibility", 0.0) == 0.0:
            return "NO-GO"

        # Certifications = 0.0 (no SAM) always NO-GO
        if dimensions.get("certifications", 0.0) == 0.0:
            return "NO-GO"

        # Empty past performance caps at EVALUATE
        past_perf = profile.get("past_performance", [])
        if not past_perf:
            if composite >= THRESHOLD_EVALUATE:
                return "EVALUATE"
            return "NO-GO"

        # Standard thresholds
        if composite >= THRESHOLD_GO:
            return "GO"
        if composite >= THRESHOLD_EVALUATE:
            return "EVALUATE"
        return "NO-GO"
