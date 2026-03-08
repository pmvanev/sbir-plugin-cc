# ADR-007: GitHub Actions CI/CD with Trunk-Based Development

## Status

Accepted

## Context

The SBIR Proposal Plugin needs automated quality gates for its Python PES code. The plugin is a Claude Code plugin distributed via GitHub -- no servers, no containers, no cloud deployment. The only testable code is ~12 Python files in `scripts/pes/`.

We need to decide:
1. CI/CD platform
2. Git branching strategy
3. Quality gate composition
4. Release mechanism

## Decision

**CI/CD platform**: GitHub Actions. The repository is on GitHub. No additional tooling or accounts needed.

**Branching strategy**: Trunk-based development. Single `main` branch. Short-lived feature branches (< 1 day target). PRs with CI gates before merge. Releases from main via annotated git tags.

**Quality gates** (all must pass before merge to main):
- Lint and format: ruff
- Type check: mypy --strict
- Test with coverage: pytest >= 80% coverage
- Security scan: bandit (SAST for Python)

**Release mechanism**: Push annotated tag `v*` triggers release workflow. Full validation re-runs. GitHub Release created with auto-generated notes.

**Mutation testing**: per-feature using mutmut, run locally after each feature delivery, >= 80% kill rate gate. Not in CI (too slow for commit stage).

## Alternatives Considered

### GitFlow
Rejected. Over-engineered for a solo-developer plugin. Multiple long-lived branches add merge complexity with no benefit when there is one developer and no production environment.

### No CI/CD
Rejected. Trunk-based development requires automated gates on main. Without CI, quality enforcement depends entirely on developer discipline, which degrades over time.

### GitHub Flow (vs trunk-based)
Similar to what we chose but implies longer-lived feature branches. Trunk-based is more appropriate for the small, focused changes expected in this project.

## Consequences

- Every PR to main runs lint + typecheck + test + security in < 5 minutes
- Branch protection on main prevents merging without passing CI
- Releases are a deliberate act (tag push), not automatic on every merge
- Mutation testing is a developer responsibility, not a CI gate (keeps CI fast)
- Path filtering means markdown-only changes skip CI entirely
