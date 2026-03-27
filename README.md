# SBIR Proposal Plugin for Claude Code

A multi-agent Claude Code plugin that guides you through the full SBIR/STTR proposal lifecycle — from topic discovery through submission and post-award learning.

All interaction happens in the Claude Code CLI. State persists as local JSON files. No web UI, no server, no database.

## Prerequisites

**Required:**
- [Claude Code](https://claude.ai/claude-code) installed and authenticated
- Python 3.12+
- Git

**Optional:**
- LaTeX distribution (e.g., TeX Live, MiKTeX) — only if you choose LaTeX output format instead of DOCX
- Gemini API key — only for AI-generated concept figures in Wave 5 (see [Image Generation Setup](docs/image-generation.md))

## Install

```bash
/plugin install sbir@pmvanev-plugins
```

## Quick Start

Never used the plugin before? Here's the complete path from install to your first proposal:

```bash
# 1. Create a project directory and open Claude Code in it
mkdir my-first-proposal && cd my-first-proposal
claude

# 2. Run setup — the wizard walks you through everything
/sbir:setup

# 3. Find solicitations that match your company
/sbir:solicitation-find

# 4. Start a proposal from a topic you like
/sbir:proposal-new AF263-042

# 5. Coming back later? Pick up where you left off
/sbir:continue
```

That's it. The plugin guides you through each step interactively. You don't need to memorize commands — `/sbir:continue` always tells you what to do next.

### What setup covers

The setup wizard detects your environment and adapts. First-time users build everything from scratch; returning users can keep their existing profile and corpus or update them.

1. **Prerequisites check** — verifies Python 3.12+, Git, and Claude Code
2. **Company profile** — searches the web for your company (SAM.gov, SBIR award history, capabilities), then lets you verify and fill gaps via document extraction, guided interview, or both
3. **Corpus ingestion** — locates past proposals, debriefs, and capability documents
4. **API key setup** (optional) — configures Gemini for concept figure generation in Wave 5
5. **Validation** — re-checks everything and displays a unified status summary
6. **Next steps** — tells you exactly what command to run next

Have your SAM.gov registration data (CAGE code, UEI) and any past proposals or capability statements handy. The wizard will tell you what it needs at each step.

### Sending feedback

```bash
/sbir:proposal-developer-feedback
```

Submit bug reports, feature suggestions, or quality ratings at any point. The agent automatically attaches a context snapshot so bug reports include enough information to reproduce the issue without exposing any proposal content.

## Documentation

| Document | What it covers |
|----------|---------------|
| [Proposal Lifecycle](docs/lifecycle.md) | Decision tree and the 10-wave lifecycle with artifacts and gates |
| [Command Reference](docs/commands.md) | Every command with wave and purpose |
| [Agents](docs/agents.md) | 18 specialized agents and what each one does |
| [Skills Reference](docs/skills.md) | Domain-knowledge files loaded on demand by agents |
| [Proposal Enforcement System](docs/enforcement.md) | How PES validates actions and prevents lifecycle mistakes |
| [Project Structure](docs/project-structure.md) | Directory layout for proposals and global config |
| [Image Generation Setup](docs/image-generation.md) | Optional Gemini API configuration for concept figures |
| [DSIP API Reference](docs/dsip-api-reference.md) | DSIP topic scraper API details |

## License

MIT
