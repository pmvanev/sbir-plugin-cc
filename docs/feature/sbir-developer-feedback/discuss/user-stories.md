# User Stories — sbir-developer-feedback

Each story traces to at least one JTBD job story.

---

## Story 1 — Submit feedback with context snapshot
**Traces to**: Job 1 (Capture friction in-context), Job 2 (Receive actionable developer feedback)

> **As a** plugin user writing an SBIR proposal,
> **I want to** invoke `/sbir:developer-feedback` and have the plugin automatically capture my current proposal state alongside my feedback,
> **so that** the developer receives enough context to understand and act on my report without asking me follow-up questions.

**Size**: M (new command + snapshot assembly)
**Priority**: Must-have

---

## Story 2 — Rate specific AI output quality dimensions
**Traces to**: Job 3 (Rate specific AI output quality)

> **As a** plugin user who has just reviewed generated content (figures, past performance selections, draft text),
> **I want to** rate each quality dimension on a 1–5 scale when submitting feedback,
> **so that** the developer can see precisely which aspect disappointed me without reading a prose explanation.

**Size**: S (conditional step within command)
**Priority**: Must-have

---

## Story 3 — Feedback works without an active proposal
**Traces to**: Job 1 (Capture friction in-context)

> **As a** plugin user exploring the plugin or running setup commands,
> **I want to** submit feedback even when no active proposal exists,
> **so that** I can report first-time-setup friction or documentation issues without being blocked.

**Size**: S (graceful null handling in snapshot)
**Priority**: Must-have

---

## Story 4 — Developer reads structured feedback entries
**Traces to**: Job 2 (Receive actionable developer feedback)

> **As the** plugin developer,
> **I want to** open `.sbir/feedback/feedback-*.json` and see a structured snapshot of what the user was doing — wave, topic, rigor profile, company profile freshness, finder results age, top scored topics, and artifacts generated,
> **so that** I can reproduce the issue and prioritize fixes based on real session context.

**Size**: XS (output schema definition — no UI needed)
**Priority**: Must-have

---

## Story 5 — Feedback persists across sessions
**Traces to**: Job 2 (Receive actionable developer feedback)

> **As the** plugin developer,
> **I want** feedback entries to accumulate in `.sbir/feedback/` with unique timestamped filenames,
> **so that** I can review all feedback from a proposal lifecycle in one place after the work is done.

**Size**: XS (directory + filename convention)
**Priority**: Must-have

---

## Story 6 — Privacy: no company IP in snapshot
**Traces to**: Job 2 (Receive actionable developer feedback)

> **As a** plugin user at a defense company,
> **I want to** be confident that submitting feedback does not capture my proposal draft text, past performance descriptions, or full company profile,
> **so that** I can share the feedback file with the developer without reviewing it for sensitive content first.

**Size**: XS (field exclusion in snapshot builder)
**Priority**: Must-have

---

## Story 7 — Empty submission guard
**Traces to**: Job 1 (Capture friction in-context)

> **As a** plugin user,
> **I want** the command to ask me once if I really want to submit with no details,
> **so that** I don't accidentally create meaningless feedback entries.

**Size**: XS (single confirmation prompt)
**Priority**: Should-have
