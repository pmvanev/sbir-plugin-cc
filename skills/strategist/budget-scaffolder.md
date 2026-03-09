---
name: budget-scaffolder
description: Rough cost modeling by labor category, indirect rates, materials, and phase -- scaffolds realistic SBIR budgets aligned with agency norms and company rate structures.
---

# Budget Scaffolding Methodology

## Agency Budget Norms

### Phase I
- Award range: $50K-$275K (varies by agency; DoD typical $250K, NIH $275K, NSF $275K)
- Duration: 6-12 months (DoD typically 6-9 months)
- Expected allocation: Labor 60-70% | Overhead/fringe 15-25% | Materials/travel 5-15%

### Phase II
- Award range: $500K-$1.7M (varies by agency; DoD typical $1.7M, NIH $1M, NSF $1M)
- Duration: 24 months
- Expected allocation: Labor 55-65% | Overhead/fringe 15-25% | Materials/equipment 10-20% | Subcontracts 5-15%

## Scaffolding Process

### Step 1: Establish Rate Structure
Source from company profile (`~/.sbir/company-profile.json`):
- Direct labor rates by category (PI, engineer, technician, admin)
- Overhead rate (or provisional rate if DCAA-approved)
- Fringe benefit rate
- G&A rate (if applicable)
- Fee/profit rate (typically 7% for SBIR)

If company profile lacks rates, use industry benchmarks and flag as "estimated -- verify with actuals."

### Step 2: Map Scope to Labor Hours
From compliance matrix requirements and technical approach:
1. Identify major task areas from solicitation work breakdown
2. Estimate hours per task area by labor category
3. Validate total hours against period of performance (1 FTE ~ 1,880 hours/year)
4. Ensure PI commitment meets agency minimums (typically 51% for SBC PI)

### Step 3: Build Cost Categories

| Category | Calculation | Typical % (Phase I) |
|----------|------------|-------------------|
| Direct Labor | Hours x rates | 35-45% |
| Fringe Benefits | Direct labor x fringe rate | 8-12% |
| Overhead | (Direct labor + fringe) x OH rate | 15-25% |
| Materials & Supplies | Bottom-up estimate from technical approach | 3-8% |
| Travel | TPOC visit + 1 conference (use GSA per diem) | 2-5% |
| Subcontracts | Task-based SOW with partner rates | 0-33% |
| Other Direct Costs | Equipment, software licenses, testing fees | 0-5% |
| G&A | (Total cost - subcontracts) x G&A rate | 0-10% |
| Fee/Profit | Total cost x fee rate | 5-7% |

### Step 4: Validate Against Thresholds

Run these checks and flag violations:

**Subcontract thresholds**:
- Phase I: subcontracts exceeding 33% require justification
- Phase II: subcontracts exceeding 50% require justification
- STTR Phase I: research institution minimum 30%
- STTR Phase II: research institution minimum 40%

**Realism checks**:
- No travel budget -> flag (reviewers expect PI engagement with end users and TPOC)
- Materials too low for claimed prototyping scope -> flag
- Labor rates inconsistent with company profile -> flag
- Consultant rates exceed $600/day (common agency cap) -> flag
- Total exceeds agency ceiling -> flag
- PI effort below 51% for SBC -> flag

### Step 5: Document Assumptions
Record every assumption in the scaffold:
- Rate sources (company profile, estimates, or benchmarks)
- Hours estimation basis (analogous projects, engineering judgment)
- Material cost basis (vendor quotes, catalog prices, estimates)
- Subcontract basis (LOI, teaming agreement, or assumed)

## Output Format

Budget scaffold is a structured summary, not a formal cost volume:

```
Budget Scaffold -- [Topic ID]
Phase: I | Duration: [months] | Ceiling: $[amount]

Labor:           $XXX,XXX  (XX%)
Fringe:          $XX,XXX   (XX%)
Overhead:        $XX,XXX   (XX%)
Materials:       $XX,XXX   (XX%)
Travel:          $X,XXX    (X%)
Subcontracts:    $XX,XXX   (XX%)
Other Direct:    $X,XXX    (X%)
G&A:             $XX,XXX   (XX%)
Fee:             $XX,XXX   (X%)
---------------------------------
Total:           $XXX,XXX

Flags: [list any threshold violations or realism concerns]
Assumptions: [list key assumptions]
```

## Common Budget Pitfalls

- Padding labor to consume ceiling without scope justification
- Forgetting ITAR/clearance costs for classified work
- Underestimating prototype materials (especially hardware)
- Not accounting for software license costs in technical approach
- Assuming zero travel when solicitation expects TPOC engagement
- Using commercial rates when DCAA-approved rates are required
