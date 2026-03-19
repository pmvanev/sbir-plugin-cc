---
description: "Screen a potential research institution partner for readiness before committing to a proposal"
argument-hint: "- Required: partner name or institution (e.g., 'MIT Lincoln Lab')"
---

# /proposal partner-screen

Lightweight readiness screening for a new potential research institution partner. Assesses 5 readiness signals through conversational questions and produces a risk-assessed recommendation.

## Usage

```
/proposal partner-screen "MIT Lincoln Lab"
/proposal partner-screen
```

## Flow

1. **Identify partner** -- Ask for the institution name if not provided as argument
2. **Screen 5 readiness signals** -- Conversational assessment of each signal
3. **Assess and recommend** -- Produce PROCEED / PROCEED WITH CAUTION / DO NOT PROCEED
4. **Save results** -- Write screening results to .sbir/partner-screenings/{slug}.json
5. **Next steps** -- On PROCEED, offer to transition to `/proposal partner-setup` for full profile creation

## 5 Readiness Signals

| Signal | What it assesses | Good indicator |
|--------|-----------------|----------------|
| Timeline commitment | Can they commit to the proposal deadline? | Explicit agreement to timeline |
| Bandwidth | Do they have capacity to co-work this project? | Named staff available, not overcommitted |
| SBIR experience | Have they participated in SBIR/STTR before? | Prior awards or proposals |
| POC assignment | Can they name a point of contact / Co-PI? | Named individual with relevant expertise |
| Scope agreement | Do they agree on the general technical approach? | Alignment on objectives and methods |

## Recommendation Logic

| Signals | Recommendation |
|---------|---------------|
| All ok | PROCEED |
| 1-2 caution, rest ok | PROCEED WITH CAUTION (with specific next steps) |
| 3+ caution or any unknown | DO NOT PROCEED (with explanation) |

## Output Format

```
PARTNER READINESS SCREENING
----------------------------
Partner: MIT Lincoln Laboratory
Date: 2026-03-19

Timeline:     OK -- confirmed availability through June deadline
Bandwidth:    CAUTION -- PI has competing proposal, backup named
SBIR Exp:     OK -- 3 prior STTR awards with Navy
POC:          OK -- Dr. Jane Smith, RF Systems Group
Scope:        OK -- aligned on autonomous sensing approach

Recommendation: PROCEED WITH CAUTION
Next steps:
- Confirm Dr. Smith's availability window
- Get written timeline commitment before proposal kickoff
```

## Prerequisites

- No existing partner profile required (this is pre-profile screening)
- Active proposal recommended but not required

## Agent Invocation

@sbir-partner-builder

Screen a potential research institution partner for readiness. Use screening mode: ask about 5 readiness signals (timeline, bandwidth, SBIR experience, POC, scope), assess each signal, produce recommendation, save results to .sbir/partner-screenings/{slug}.json, and offer transition to /proposal partner-setup on PROCEED.
