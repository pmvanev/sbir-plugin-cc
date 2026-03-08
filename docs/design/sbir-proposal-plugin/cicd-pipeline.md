# CI/CD Pipeline Design -- sbir-proposal-plugin

## Context

This is a Claude Code plugin installed via `claude plugin install`. There is no server deployment, no container builds, no cloud infrastructure. The only testable code is the PES enforcement system in `scripts/pes/` (Python 3.12+). Everything else is markdown.

The CI/CD pipeline validates PES code quality on every commit to main and every pull request. Releases are git tags that trigger a validation-then-release workflow.

## Rejected Simple Alternatives

### Alternative 1: No CI/CD at all
- **What**: Rely on developer discipline for linting and testing locally.
- **Expected Impact**: Works for solo developer, covers 60% of quality needs.
- **Why Insufficient**: No enforcement of quality gates. Regressions slip through. No audit trail of passing tests per commit. Trunk-based development requires automated gates on main.

### Alternative 2: Single lint-only workflow
- **What**: GitHub Actions workflow that only runs ruff.
- **Expected Impact**: Catches formatting and basic issues, covers 40% of quality needs.
- **Why Insufficient**: No test execution, no coverage tracking, no type checking, no security scanning. PES is an enforcement system -- its correctness matters.

## Pipeline Architecture

```
                    push to main / PR to main
                            |
              +-------------+-------------+
              |             |             |
           [Lint]     [Type Check]   [Security]
              |             |             |
              +------+------+             |
                     |                    |
                  [Test]                  |
                     |                    |
              +------+--------------------+
              |
        [All Checks]  <-- branch protection requires this
```

### Commit Stage (target: < 5 minutes)

All jobs run in parallel except the final gate.

| Job | Tool | Gate Criteria |
|-----|------|--------------|
| Lint and Format | ruff check, ruff format --check | Zero violations |
| Type Check | mypy --strict | Zero errors |
| Test | pytest with coverage | 100% pass, >= 80% coverage |
| Security Scan | bandit | Zero critical/high findings |
| All Checks | Aggregator | All upstream jobs pass |

### Path Filtering

The workflow only triggers on changes to Python code, test code, or CI configuration:
- `scripts/**`
- `tests/**`
- `pyproject.toml`
- `.github/workflows/ci.yml`

Markdown-only changes (agents, commands, skills) skip CI entirely. This prevents unnecessary workflow runs on the majority of plugin commits.

### Release Stage (tag push only)

```
    push tag v*
        |
   [Validate]  -- full test suite + lint + typecheck + security
        |
   [Release]   -- create GitHub Release with auto-generated notes
```

Pre-release tags (e.g., `v0.1.0-rc.1`) are marked as prerelease on GitHub.

## Quality Gates

| Gate | Threshold | Enforcement |
|------|-----------|-------------|
| Unit test pass rate | 100% | pytest exit code |
| Code coverage | >= 80% | pytest-cov + coverage.json check |
| Lint | Zero violations | ruff exit code |
| Type safety | Zero errors | mypy exit code |
| Security | Zero critical/high | bandit exit code |
| All checks | All pass | Aggregator job for branch protection |

## Branch Protection Rules (main)

| Rule | Setting |
|------|---------|
| Require pull request before merging | Yes |
| Required approvals | 1 (solo project; increase when team grows) |
| Require status checks to pass | `All Checks Pass` job |
| Require branches be up to date | Yes |
| Require linear history | Yes (rebase merge only) |
| Allow force pushes | No |
| Allow deletions | No |

## DORA Metrics Baseline

Target performance level: **High** (appropriate for a solo-developer plugin project).

| Metric | Target | How Measured |
|--------|--------|-------------|
| Deployment frequency | Weekly to on-demand | Git tag frequency |
| Lead time for changes | < 1 day | Commit to tag creation |
| Change failure rate | < 15% | Reverted tags / total tags |
| Time to restore | < 1 hour | Time from issue to fix tag |

## Tooling

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Runtime |
| pytest | >= 8.0 | Test runner |
| pytest-cov | >= 5.0 | Coverage measurement |
| ruff | >= 0.8 | Linter and formatter |
| mypy | >= 1.13 | Type checker |
| bandit | >= 1.8 | Security scanner (SAST) |
| mutmut | >= 3.2 | Mutation testing |

All tool configuration lives in `pyproject.toml`. Zero additional config files.
