# Infrastructure -- sbir-proposal-plugin

## Context

This plugin has no infrastructure. It runs locally inside Claude Code on the user's machine.

This document exists for completeness in the platform design package and to explicitly record what was considered and rejected.

## Rejected Infrastructure Options

### Alternative 1: Cloud-hosted PES enforcement
- **What**: Run PES as a cloud function, plugin calls it remotely.
- **Expected Impact**: Could enable centralized rule updates.
- **Why Rejected**: Adds network dependency to a local tool. Violates the architecture's "local-only execution" principle (ADR-002). Introduces latency to every hook invocation. Over-engineered for a single-user CLI plugin.

### Alternative 2: Docker container for PES
- **What**: Package PES in a container, run locally via Docker.
- **Expected Impact**: Consistent Python environment.
- **Why Rejected**: Adds Docker as a dependency. Python 3.12+ is sufficient. Claude Code already requires a local environment. Unnecessary abstraction layer.

## What Exists

| Concern | Solution |
|---------|----------|
| Runtime | User's local Python 3.12+ |
| State persistence | JSON files in `.sbir/` directory |
| Plugin distribution | GitHub repository via `claude plugin install` |
| Dependency management | `pyproject.toml` with `pip install -e ".[dev]"` |
| CI/CD | GitHub Actions (see `cicd-pipeline.md`) |

## Developer Infrastructure

The only "infrastructure" is the development environment:

```bash
# Clone and set up
git clone https://github.com/pmvanev/sbir-plugin-cc.git
cd sbir-plugin-cc
python3 -m venv .venv
source .venv/bin/activate    # or .venv/Scripts/activate on Windows
pip install -e ".[dev]"

# Verify setup
pytest tests/ -v
ruff check scripts/
mypy scripts/pes/
```

No Docker, no Terraform, no Kubernetes, no cloud accounts required.
