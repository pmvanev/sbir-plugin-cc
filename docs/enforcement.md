# Proposal Enforcement System (PES)

The PES is a Python-based guardrail system that validates every action against proposal lifecycle rules. It runs automatically via Claude Code hooks — you never invoke it directly, but it prevents mistakes like skipping waves, drafting before strategy approval, or modifying a submitted proposal.

Inspired by nWave's [Design Enforcement System (DES)](https://github.com/nwave-ai/nwave), which enforces wave ordering in software development workflows. PES adapts the same concept for the SBIR proposal domain.

## How it works

PES hooks into two Claude Code events:

- **SessionStart** — validates state file integrity when you open a project. If `.sbir/proposal-state.json` is corrupted, PES attempts recovery from the `.bak` backup.
- **PreToolUse** — evaluates every tool call against active enforcement rules before it executes. If a rule is violated, PES blocks the action with an explanation of what's wrong and what to do instead.

## What PES enforces

| Rule | Example |
|------|---------|
| **Wave ordering** | Can't start Wave 4 drafting until Wave 3 outline is approved |
| **Gate compliance** | Can't proceed past strategy brief until it's explicitly approved |
| **Deadline awareness** | Warnings at 7 days, blocks at critical thresholds |
| **Submission immutability** | Can't modify proposal content after submission is confirmed |
| **Quality gates** | Validates quality profile consistency when quality discovery is active |

## Architecture

PES uses ports-and-adapters architecture to keep domain rules pure and testable:

- **Domain** (`scripts/pes/domain/`) — pure Python business rules with no infrastructure imports
- **Ports** (`scripts/pes/ports/`) — abstract interfaces (StateReader, StateWriter, RulePort)
- **Adapters** (`scripts/pes/adapters/`) — JSON file persistence, Claude Code hook protocol translation

Hook protocol: JSON on stdin/stdout, exit codes 0 (allow), 1 (block with explanation).
