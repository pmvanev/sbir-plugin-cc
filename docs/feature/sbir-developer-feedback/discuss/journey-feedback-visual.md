# Journey Map — /sbir:developer-feedback

**Persona**: Maya, a proposal writer at a small defense contractor, using the SBIR plugin for the first time on a real proposal.

**Trigger**: Maya is in Wave 3 (drafting). The plugin selected a past performance entry about an irrelevant project. She wants to flag it before she forgets.

---

## Journey Steps

```
MOMENT OF FRICTION
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: INVOKE                                                  │
│ Maya types: /sbir:developer-feedback                            │
│ Feeling: Slightly frustrated but hopeful something will happen  │
│ Mental model: "Like filing a ticket, but fast"                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: TYPE SELECTION                                          │
│ Agent asks: Bug / Suggestion / Quality issue?                   │
│ Maya selects: Quality issue                                     │
│ Feeling: Good — my category exists                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: QUALITY RATINGS (conditional on Quality Issue)          │
│ Agent presents 4 dimensions, each 1–5:                         │
│   - Past performance relevance                                  │
│   - Image quality                                               │
│   - Writing quality                                             │
│   - Topic scoring accuracy                                      │
│ Maya rates past performance: 2/5, skips others (N/A)           │
│ Feeling: Quick, right-sized effort                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: FREE TEXT                                               │
│ Agent asks: "Anything else to add?" (optional)                  │
│ Maya types: "The plugin selected our GPS work but this topic    │
│ is about radar metamaterials — no overlap"                      │
│ Feeling: Relieved — context is captured                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: AUTO-SNAPSHOT                                           │
│ Agent silently reads and captures:                              │
│   ✓ proposal_id, topic (id, title, agency)                      │
│   ✓ current_wave: 3, completed_waves: [0,1,2], skipped: []     │
│   ✓ rigor_profile: standard                                     │
│   ✓ company_profile_age: 14 days, company_name: "Acme Corp"    │
│   ✓ finder_results_age: 3 days                                  │
│   ✓ top_scored_topics: [topic_id, score, recommendation]        │
│   ✓ generated_artifacts: [strategy.md, outline.md, ...]         │
│   ✓ plugin_version: git SHA                                     │
│ Feeling: Nothing to do — it's automatic                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: PERSIST + CONFIRM                                       │
│ Written to: .sbir/feedback/feedback-{timestamp}.json            │
│ Agent confirms: "Feedback saved. Thank you."                    │
│ Shows: feedback ID and file path                                │
│ Feeling: Done. Back to work.                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Emotional Arc

```
Frustration ──► Hopeful ──► Acknowledged ──► Efficient ──► Relieved ──► Done
     1              2            3               4              5           5
```

Confidence builds at Step 3 (my category exists) and peaks at Step 5 (auto-capture means I don't have to explain the setup). There is no confidence dip — the interaction is designed to be faster than typing a Slack message.

## Error Paths

| Scenario | Behavior |
|----------|----------|
| No active proposal (no `.sbir/`) | Still saves feedback; context_snapshot has `proposal_id: null`, all proposal fields empty. |
| No company profile | Captures null for profile fields; does not block submission. |
| Finder results not yet run | `finder_results_age: null` in snapshot. |
| User skips all ratings | Valid — free text only is allowed. |
| User skips free text | Valid — ratings only is allowed. |
| Both ratings and text skipped | Agent prompts once: "Are you sure you want to submit with no details?" then allows. |
