# SBIR Proposal Plugin for Claude Code

A multi-agent Claude Code plugin that guides you through the full SBIR/STTR proposal lifecycle — from topic identification through submission and post-award learning.

## What It Does

The plugin provides specialized AI agents that handle each phase of writing an SBIR/STTR proposal:

- **Wave 0** — Find and evaluate open solicitations, score company fit, make Go/No-Go decisions
- **Wave 1** — Extract compliance requirements, prepare TPOC questions, build strategy briefs
- **Wave 2** — Conduct technical and market research
- **Wave 3** — Build discrimination tables and proposal outlines
- **Wave 4** — Draft all proposal sections with iterative human review
- **Wave 5** — Generate figures, diagrams, and concept illustrations
- **Wave 6** — Format and assemble submission-ready document packages
- **Wave 7** — Red team review and government evaluator simulation
- **Wave 8** — Submission portal packaging
- **Wave 9** — Post-submission debrief analysis and lessons learned

An enforcement layer (PES) runs as Python hooks to maintain proposal integrity — enforcing wave ordering, compliance gates, and audit logging.

All interaction happens in the Claude Code CLI. State persists as local JSON files. No web UI, no server, no database.

## Quickstart

### Prerequisites

- [Claude Code](https://claude.ai/claude-code) installed and authenticated
- Python 3.12+
- Git

### Install

```bash
claude plugin install github:pmvanev/sbir-plugin-cc
```

### Start a Proposal

```bash
# Open your project directory
cd my-proposal-project

# Start a new proposal from a solicitation file
/sbir:proposal new ./solicitation.pdf

# Check status at any time
/sbir:proposal status
```

The plugin creates a `.sbir/` directory in your project to store proposal state and artifacts.

## Image Generation Setup (Optional)

The plugin can generate concept figures, technical illustrations, and infographics using Google's Gemini Nano Banana API. This is optional — without it, the formatter will produce structural diagrams (SVG, Mermaid, Graphviz) and write specification briefs for any concept figures you need to create manually.

### Get an API Key

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Sign in and create an API key
3. The free tier allows 500 images per day

### Configure

Add the key to your shell profile (`~/.bashrc`, `~/.zshrc`, or equivalent):

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Restart your terminal or run `source ~/.bashrc` for the change to take effect.

The formatter agent will automatically detect the key and use Nano Banana for concept figures during Wave 5.

## License

MIT
