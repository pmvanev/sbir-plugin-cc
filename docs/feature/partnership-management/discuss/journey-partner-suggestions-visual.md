# Journey: Partnership-Aware AI Suggestions

## Overview

How partner profiles integrate into existing agent workflows to produce partnership-aware content across scoring, strategy, approach selection, and drafting.

## Persona

Phil Santos -- engineer, has partner profiles on file (CU Boulder, NDSU). Working on a partnered STTR proposal.

## Emotional Arc

- **Start**: Hopeful but skeptical ("will partner data actually improve the suggestions?")
- **Middle**: Surprised and delighted ("it used the partner's actual capabilities, not boilerplate")
- **End**: Trusting ("the AI understands our partnership")

---

## Flow Diagram

```
[Entry Points -- existing commands, enhanced with partner awareness]

/solicitation-find          /proposal-shape           /proposal-wave-strategy      /proposal-draft
       |                          |                          |                          |
       v                          v                          v                          v
  PARTNER-AWARE             PARTNER-AWARE              PARTNER-AWARE             PARTNER-AWARE
  TOPIC SCORING             APPROACH GEN               STRATEGY BRIEF            SECTION DRAFTING
       |                          |                          |                          |
  Show company-only         Generate approaches        Teaming section            Write sections
  AND partnership           that leverage combined     auto-populated from        referencing partner
  scores side-by-side.      capabilities. Score        partner profile data.      capabilities,
  Highlight topics          with partner data.         Work-split from            facilities, and
  elevated by               Flag approaches only       capability analysis.       personnel by name.
  partnership.              viable with partner.
       |                          |                          |                          |
  Feels: "found             Feels: "approaches        Feels: "the teaming       Feels: "this reads
  opportunities I           I wouldn't have            section wrote itself"      like we actually
  would have missed"        thought of alone"                                    work together"
```

---

## Scenario 1: Partnership-Aware Topic Scoring (`/solicitation-find`)

### Current State (before partnership management)

```
+-- Solicitation Scoring ----------------------------------------+
|                                                                 |
| Topic N244-012: Autonomous UUV Navigation                       |
| Type: STTR Phase I                                              |
|                                                                 |
| Dimension           Score                                       |
| SME                 0.45  (your capabilities partially match)   |
| Past Performance    0.30                                        |
| Certifications      1.00                                        |
| Eligibility         1.00                                        |
| STTR                0.50  (partner listed but no profile)       |
| -----------------------------------------------                 |
| Composite:          0.56  -- EVALUATE                           |
+----------------------------------------------------------------+
```

### Enhanced State (with partner profiles)

```
+-- Solicitation Scoring (Partnership-Aware) --------------------+
|                                                                 |
| Topic N244-012: Autonomous UUV Navigation                       |
| Type: STTR Phase I                                              |
|                                                                 |
|                    You Only    + CU Boulder    Delta             |
| SME                0.45        0.78           +0.33             |
| Past Performance   0.30        0.55           +0.25             |
| Certifications     1.00        1.00            --               |
| Eligibility        1.00        1.00            --               |
| STTR               0.50        1.00           +0.50             |
| -----------------------------------------------                 |
| Composite:         0.56        0.82           +0.26             |
| Recommendation:    EVALUATE    GO                               |
|                                                                 |
| Partnership elevated this topic from EVALUATE to GO.            |
| CU Boulder adds: autonomous navigation, underwater acoustics,  |
| sensor fusion (Dr. Sarah Kim, Co-PI)                            |
+----------------------------------------------------------------+
```

**Emotional state**: Discovery -- "I would have passed on this topic without the partnership score."

---

## Scenario 2: Partnership-Aware Approach Generation (`/proposal-shape`)

```
+-- Approach Selection (Partnership-Aware) ----------------------+
|                                                                 |
| Topic: N244-012 -- Autonomous UUV Navigation                    |
| Partnership: Acme Defense + CU Boulder                          |
|                                                                 |
| APPROACH 1: Acoustic-Inertial Fusion (RECOMMENDED)              |
|   Score: 8.2/10                                                 |
|   Leverages: CU Boulder acoustic signal processing expertise    |
|     (Dr. Sarah Kim) + your RF engineering + inertial nav        |
|   Work split: CU Boulder leads acoustic algorithms (40%),       |
|     you lead system integration + RF backup nav (60%)           |
|   Facility: CU Boulder underwater acoustics lab for testing     |
|                                                                 |
| APPROACH 2: Vision-Based Navigation                             |
|   Score: 6.8/10                                                 |
|   Leverages: Your ML capabilities                               |
|   Gap: Neither entity has underwater vision expertise           |
|   [!] Weaker partnership utilization                            |
|                                                                 |
| APPROACH 3: Multi-Modal Sensor Fusion                           |
|   Score: 7.5/10                                                 |
|   Leverages: Combined sensor expertise across both entities     |
|   Note: Broader scope -- may be ambitious for Phase I           |
|                                                                 |
| -----------------------------------------------                 |
| Approach 1 maximizes combined team strengths.                   |
| CU Boulder's acoustic expertise is uniquely applicable.         |
|                                                                 |
| Select an approach: (1) (2) (3) (e)dit (q)uit                  |
+----------------------------------------------------------------+
```

**Emotional state**: Confident -- suggestions are grounded in actual partner capabilities, not generic.

---

## Scenario 3: Partnership-Aware Strategy Brief (`/proposal-wave-strategy`)

```
+-- Strategy Brief: Teaming Section (Auto-generated) -----------+
|                                                                 |
| ## 3. Teaming Strategy                                          |
|                                                                 |
| ### 3.1 Partnership Structure                                   |
| Acme Defense (prime, small business) + CU Boulder (research     |
| institution, STTR partner). CU Boulder performs 35% of Phase I  |
| work, meeting the STTR 30% minimum.                             |
|                                                                 |
| ### 3.2 Capability Complementarity                              |
| | Capability          | Acme Defense | CU Boulder |            |
| |---------------------|:----------:|:----------:|              |
| | RF engineering      |     X      |            |              |
| | Machine learning    |     X      |     X      |              |
| | Acoustic processing |            |     X      |              |
| | Sensor fusion       |            |     X      |              |
| | System integration  |     X      |            |              |
|                                                                 |
| ### 3.3 Work Split                                              |
| Acme Defense: System architecture, RF subsystem, integration    |
|   (Phil Santos, PI -- directed energy, systems engineering)     |
| CU Boulder: Acoustic algorithms, sensor fusion, testing         |
|   (Dr. Sarah Kim, Co-PI -- autonomous nav, underwater acoustics)|
|                                                                 |
| ### 3.4 Facilities                                              |
| CU Boulder: Underwater acoustics laboratory, GPU compute        |
|   cluster for ML training                                       |
| Acme Defense: RF test range, rapid prototyping facility          |
|                                                                 |
| [Source: partner profile cu-boulder.json + company-profile.json]|
+----------------------------------------------------------------+
```

**Emotional state**: Delighted -- "the teaming section wrote itself, and it used real names and facilities."

---

## Error Paths

### E1: No partner profile exists for an STTR topic

```
Topic N244-012 is STTR. No partner profiles found.

  STTR topics require a research institution partner.
  Current STTR score: 0.0

  Options:
    /proposal partner-setup  -- create a partner profile
    (s) skip                 -- score without partner data
```

### E2: Partner capabilities do not improve scoring

```
                    You Only    + NDSU          Delta
SME                 0.85        0.87           +0.02
[...]
Composite:          0.72        0.73           +0.01

Partnership has minimal impact on this topic.
NDSU's strengths (agricultural engineering, soil science)
do not align with this topic's requirements.
Consider: Is NDSU the right partner for this topic?
```

### E3: Approach generation with no partner match

```
[!] None of the generated approaches strongly leverage
CU Boulder's capabilities for this topic. The topic
focus (cybersecurity) does not align with CU Boulder's
profile (acoustics, navigation).

Consider:
  - Proceeding without a partner (SBIR track)
  - A different partner with cybersecurity expertise
```
