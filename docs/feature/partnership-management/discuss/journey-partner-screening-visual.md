# Journey: New Partner Readiness Screening

## Overview

Lightweight assessment of a new partner's commitment, bandwidth, and capability fit before investing weeks in coordination. Addresses the Q8 failure case (partner backed out after facility tour).

## Persona

Phil Santos -- evaluating SWRI as a potential new partner for an upcoming STTR proposal. Has been burned before (Q8).

## Emotional Arc

- **Start**: Cautious, protective ("I don't want to waste weeks again")
- **Middle**: Methodical, objective ("this gives me a structured way to assess")
- **End**: Informed and decisive ("I know the risks and I'm making a conscious choice")

---

## Flow Diagram

```
[Trigger]                    [Phase 1]              [Phase 2]           [Phase 3]
/proposal partner-screen     READINESS               FIT                 RECOMMENDATION
        |                    ASSESSMENT              SCORING                  |
        v                         |                     |                     v
  "Screen a new partner"     Timeline fit?          Capability overlap?   Summary with
  Phil provides partner      Bandwidth?             STTR eligibility?     risk flags.
  name + topic reference.    Prior SBIR/STTR exp?   Complementarity?      Go/caution/
                             Commitment signals?                          no-go.
        |                         |                     |                     |
  Feels: cautious            Feels: methodical      Feels: analytical    Feels: informed
  Sees: screening intro      Sees: checklist        Sees: gap analysis   Sees: clear
                             with status                                  recommendation
```

---

## Step Details

### Step 1: Trigger

```
+-- Partner Screening -------------------------------------------+
|                                                                 |
| > /proposal partner-screen                                      |
|                                                                 |
| PARTNER READINESS SCREENING                                     |
| -----------------------------------------------                 |
|                                                                 |
| This screens a potential new partner for commitment, fit,       |
| and readiness BEFORE you invest significant time.               |
|                                                                 |
| I'll ask about the partner's situation and assess risks.        |
| This takes about 5 minutes.                                     |
|                                                                 |
| Partner name: > Southwest Research Institute (SWRI)             |
| Target topic (optional): > N244-012                             |
+----------------------------------------------------------------+
```

### Step 2: Readiness Assessment (Conversational)

```
+-- Readiness Questions -----------------------------------------+
|                                                                 |
| READINESS ASSESSMENT: SWRI                                      |
| -----------------------------------------------                 |
|                                                                 |
| 1. TIMELINE                                                     |
|    Proposal deadline is March 15 (32 days).                     |
|    Has SWRI confirmed they can support this timeline?           |
|    > They said "probably" in our initial call.                  |
|    [!] CAUTION: "Probably" is not a commitment.                 |
|                                                                 |
| 2. BANDWIDTH                                                    |
|    Is SWRI currently committed to other proposals               |
|    in this same timeframe?                                      |
|    > Not sure. They have a large proposals team.                |
|    [?] UNKNOWN: Recommend asking directly.                      |
|                                                                 |
| 3. SBIR/STTR EXPERIENCE                                         |
|    Has SWRI participated in SBIR/STTR proposals before?         |
|    > Yes, they have 200+ awards.                                |
|    [OK] Strong SBIR/STTR track record.                          |
|                                                                 |
| 4. COMMITMENT SIGNALS                                           |
|    Have they assigned a specific person as point of contact?    |
|    > Yes, Dr. Rebecca Chen.                                     |
|    [OK] Named POC is a positive commitment signal.              |
|                                                                 |
| 5. SCOPE AGREEMENT                                              |
|    Have you discussed the work split (they do X, you do Y)?    |
|    > High level only -- they would do testing and simulation.   |
|    [~] PARTIAL: Rough agreement exists but needs formalization. |
+----------------------------------------------------------------+
```

### Step 3: Fit Scoring (if topic provided)

```
+-- Capability Fit Assessment -----------------------------------+
|                                                                 |
| CAPABILITY FIT: SWRI x Topic N244-012                           |
| -----------------------------------------------                 |
|                                                                 |
| Topic requires:        SWRI brings:            You bring:       |
| autonomous navigation  intelligent systems     RF engineering   |
| underwater sensing     sensor fusion           machine learning |
| real-time processing   autonomy                signal processing|
|                                                                 |
| Overlap with topic:    HIGH (3/3 areas)        MEDIUM (2/3)    |
| Complementarity:       STRONG -- SWRI covers gaps in your      |
|                        autonomous nav and underwater sensing    |
|                                                                 |
| STTR Eligibility:      nonprofit_research -- ELIGIBLE           |
| 30% Work Commitment:   Feasible (simulation + testing tasks)   |
+----------------------------------------------------------------+
```

### Step 4: Recommendation

```
+-- Screening Summary -------------------------------------------+
|                                                                 |
| PARTNER READINESS: SWRI for N244-012                            |
| -----------------------------------------------                 |
|                                                                 |
| RECOMMENDATION: PROCEED WITH CAUTION                            |
|                                                                 |
| Strengths:                                                      |
|   [OK] Strong SBIR/STTR track record (200+ awards)             |
|   [OK] Named POC assigned (Dr. Rebecca Chen)                   |
|   [OK] Strong capability complementarity                       |
|   [OK] STTR eligible (nonprofit research)                      |
|                                                                 |
| Risks:                                                          |
|   [!] Timeline commitment is soft ("probably")                  |
|   [?] Bandwidth unknown -- may have competing proposals        |
|   [~] Work split agreement is high-level only                   |
|                                                                 |
| Suggested next steps before investing further:                  |
|   1. Get explicit timeline commitment (yes/no by date X)        |
|   2. Ask about competing proposals in same timeframe            |
|   3. Draft preliminary work split for mutual review             |
|                                                                 |
| -----------------------------------------------                 |
| Risk level: MEDIUM                                              |
| Compare to Q8 failure: 2 of 3 risk flags present that were     |
| also present in the prior partner dropout.                      |
| -----------------------------------------------                 |
|                                                                 |
|   (p) proceed  -- continue to /proposal partner-setup           |
|   (w) wait     -- revisit after resolving risks                 |
|   (s) save     -- save screening notes for later                |
|   (c) cancel                                                    |
+----------------------------------------------------------------+
```

**Emotional state**: Informed and empowered. Phil has objective data to make a go/no-go decision on investing time, rather than discovering problems after weeks of meetings.

---

## Error Paths

### E1: All signals positive

```
RECOMMENDATION: PROCEED
All readiness signals are positive. Low risk of partner dropout.
  (p) proceed to /proposal partner-setup
```

### E2: Critical red flags

```
RECOMMENDATION: DO NOT PROCEED

Critical risks:
  [X] No timeline commitment
  [X] No named POC (talking to "someone in the proposals office")
  [X] No prior SBIR/STTR experience

This partner shows 3 critical red flags. Consider alternative
partners before investing coordination time.
```

### E3: No topic provided

```
Screening without a specific topic. Capability fit assessment
will be skipped -- only readiness signals will be evaluated.

To include capability fit, re-run with a topic:
  /proposal partner-screen --topic N244-012
```
