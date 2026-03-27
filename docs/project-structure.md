# Project Structure

```
my-proposal-project/
  .sbir/
    proposal-state.json          # Lifecycle state (wave, status, decisions)
    corpus/                      # Indexed past proposals, debriefs, boilerplate
  artifacts/
    wave-0-intelligence/         # Topic digest, go-no-go, approach brief
    wave-1-strategy/             # Compliance matrix, TPOC Q&A, strategy brief
    wave-2-research/             # Technical landscape, market research, TRL
    wave-3-outline/              # Discrimination table, outline, figure plan
    wave-4-drafts/               # Drafted sections + review records
    wave-5-visuals/              # Figure specs + generated figures
    wave-6-format/               # Formatted volumes + compliance check
    wave-7-review/               # Scorecard, red team, sign-off
    wave-8-submission/           # Portal package + immutable archive
    wave-9-learning/             # Debrief analysis + lessons learned
  pdcs/                          # Proposal Design Criteria per section

~/.sbir/
  company-profile.json           # Global company profile (shared across all proposals)
  partners/                      # Research institution partner profiles (one JSON per partner)
    cu-boulder.json              # Partner profile: capabilities, personnel, facilities, STTR eligibility
    swri.json
  quality-preferences.json       # Writing style preferences (tone, detail, evidence style)
  winning-patterns.json          # Proposal ratings and winning practices by agency
  writing-quality-profile.json   # Evaluator feedback patterns by agency and section
```
