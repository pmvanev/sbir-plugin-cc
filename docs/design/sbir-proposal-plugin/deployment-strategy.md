# Deployment Strategy -- sbir-proposal-plugin

## Context

This plugin has no traditional deployment. Users install it via:

```bash
claude plugin install github:pmvanev/sbir-plugin-cc
```

Claude Code pulls the plugin from the GitHub repository. "Deployment" means: push code to main, tag a release, user updates their plugin installation.

## Versioning Strategy

Semantic versioning via git tags: `vMAJOR.MINOR.PATCH`

| Version Component | When to Bump | Example |
|-------------------|-------------|---------|
| MAJOR | Breaking changes to hook protocol, state schema migration required | v2.0.0 |
| MINOR | New agents, commands, skills, PES rules, non-breaking features | v0.2.0 |
| PATCH | Bug fixes, typo corrections, non-functional changes | v0.1.1 |

Pre-release tags for testing: `v0.2.0-rc.1`

## Release Process

```
1. All work merged to main via PR (CI passes)
2. Review CHANGELOG (or generate from commits)
3. Create annotated tag: git tag -a v0.1.0 -m "Phase C1: Foundation"
4. Push tag: git push origin v0.1.0
5. Release workflow validates (full test suite)
6. GitHub Release created automatically with release notes
7. Users update: claude plugin update sbir-plugin-cc
```

## Rollback Procedure

Rollback is simple for a git-based plugin:

1. **Identify bad release**: User or CI reports issue with tag vX.Y.Z
2. **Fix forward (preferred)**: Create patch vX.Y.(Z+1) with fix, tag, push
3. **Rollback (if needed)**: User pins to previous version or developer creates a revert commit and new tag

There are no database migrations, no infrastructure state, no running services to roll back. The entire rollback surface is: git revert + new tag.

## State Schema Migration

When `proposal-state.json` schema changes (MAJOR version bump):

1. PES session startup checker detects schema version mismatch
2. PES presents migration guidance (what changed, how to update)
3. Migration is a one-time state file update, not an infrastructure concern

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Bad release breaks PES hooks | Low | Medium (plugin errors on session start) | CI gates catch regressions; user can uninstall plugin |
| Schema change breaks existing proposals | Low | High (user loses work) | Schema version field; migration path documented; .bak file preserved |
| Dependency vulnerability in jsonschema | Low | Low (local-only execution) | Dependabot alerts on GitHub; bandit scans in CI |

## What This Plugin Does NOT Need

- Container registry or image builds
- Staging / production environments
- Load balancers or traffic shifting
- Blue-green or canary deployments
- Infrastructure as Code
- Secrets management (no secrets exist)
- Monitoring dashboards or alerting
