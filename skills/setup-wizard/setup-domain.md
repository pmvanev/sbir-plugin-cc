---
name: setup-domain
description: Prerequisites check commands, validation rules, TUI display patterns, and next-steps guidance for the setup wizard
---

# Setup Domain Knowledge

## Prerequisite Checks

Run each check via Bash. Parse output for version extraction.

### Python 3.12+

```bash
python --version 2>&1 || python3 --version 2>&1
```

Extract version number (e.g., "Python 3.12.4" -> 3.12.4). Compare major.minor >= 3.12.
- Pass: `[ok]  Python {version}`
- Fail: `[!!]  Python {version} -- version 3.12+ required` or `[!!]  Python not found`
- Fix: "Install Python 3.12+ from https://python.org/downloads"
- Note: On Windows, `python` is more reliable than `python3`

### Git

```bash
git --version 2>&1
```

Extract version (e.g., "git version 2.44.0" -> 2.44.0).
- Pass: `[ok]  Git {version}`
- Fail: `[!!]  Git not found`
- Fix: "Install Git from https://git-scm.com/downloads. On Windows, ensure Git is added to PATH."

### LaTeX Compiler (optional)

```bash
pdflatex --version 2>&1 || xelatex --version 2>&1 || lualatex --version 2>&1
```

Check for any of: pdflatex, xelatex, lualatex. Extract engine name and version from output.
- Pass: `[ok]  LaTeX ({engine} {version})`
- Absent: `[--]  LaTeX not found (optional -- needed for LaTeX output format)`
- Fix: offer platform-specific install instructions (see LaTeX Installation section below)
- Note: LaTeX is only needed if the user wants LaTeX output format instead of DOCX. It is NOT a required prerequisite -- missing LaTeX does not halt setup.

### Claude Code Authentication

Claude Code is authenticated if the agent is running (the user is interacting with you). This check always passes in normal operation.
- Pass: `[ok]  Claude Code authenticated`

## Validation Status Indicators

Three indicators used throughout setup:

| Indicator | Meaning | When Used |
|-----------|---------|-----------|
| `[ok]` | Configured and valid | Prereqs pass, profile valid, corpus populated |
| `[!!]` | Warning -- works but with consequences | SAM.gov inactive (all topics NO-GO) |
| `[--]` | Not configured -- informational | GEMINI_API_KEY absent, corpus empty |

## Overall Status Computation

- **READY**: Profile exists and validates. All prerequisites pass.
- **READY (with warnings)**: Profile exists but SAM.gov inactive, or corpus empty, or both. Setup is functional but effectiveness reduced.
- Prerequisites failure: Setup halts. No status computed.

## Profile Detection

Use Python adapter to check for existing profile:

```bash
python -c "
import os, sys; sys.path.insert(0, os.path.join(os.environ['CLAUDE_PLUGIN_ROOT'], 'scripts'))
from pes.adapters.json_profile_adapter import JsonProfileAdapter
import json
adapter = JsonProfileAdapter('$HOME/.sbir')
meta = adapter.metadata()
print(json.dumps({'exists': meta.exists, 'company_name': meta.company_name}))
"
```

## Corpus Detection

Check `.sbir/corpus/` for indexed documents. If the directory does not exist or is empty, corpus count is 0.

## API Key Check

```bash
if [ -n "$GEMINI_API_KEY" ]; then echo "detected"; else echo "not_set"; fi
```

- Present: `[ok]  GEMINI_API_KEY detected`
- Absent: `[--]  GEMINI_API_KEY not configured (optional -- Wave 5 only)`
- Gemini enables concept figure generation in Wave 5. Not needed for Waves 0-4.

## Configuration Instructions for Gemini

1. Visit https://ai.google.dev
2. Create a Google AI Studio account
3. Generate an API key
4. Add to shell profile:
   - Bash: `echo 'export GEMINI_API_KEY="your-key"' >> ~/.bashrc && source ~/.bashrc`
   - PowerShell: `[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your-key', 'User')`
5. Restart terminal

## LaTeX Installation Instructions

Display when user selects (i) install during prerequisite check:

### Windows

```
Option A: MiKTeX (recommended for Windows)
  1. Download from https://miktex.org/download
  2. Run the installer, select "Install missing packages on-the-fly: Yes"
  3. Restart your terminal
  4. Verify: pdflatex --version

Option B: TeX Live
  1. Download install-tl-windows.exe from https://tug.org/texlive/acquire-netinstall.html
  2. Run the installer (full install is ~5 GB, basic scheme is ~300 MB)
  3. Restart your terminal
  4. Verify: pdflatex --version
```

### macOS

```
Option A: MacTeX (recommended)
  1. Download from https://tug.org/mactex/
  2. Run the installer (~5 GB full, or BasicTeX ~100 MB)
  3. Restart your terminal
  4. Verify: pdflatex --version

Option B: Homebrew
  brew install --cask mactex    # Full install
  brew install --cask basictex  # Minimal install
```

### Linux

```
Ubuntu/Debian:
  sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended

Fedora/RHEL:
  sudo dnf install texlive-scheme-basic texlive-latex

Arch:
  sudo pacman -S texlive-basic texlive-latexextra
```

After installation, restart the terminal and run `/sbir:setup` again to verify detection.

## Next Steps Commands

Display after successful validation:

```
What to do next:
  /sbir:solicitation find              -- discover SBIR/STTR topics matching your profile
  /sbir:solicitation find --agency X   -- filter by agency
  /sbir:proposal new <solicitation>    -- start a new proposal
  /sbir:proposal status                -- check proposal status

Run /sbir:setup again to update your configuration.
```

## Delegation Patterns

### Profile Builder Delegation

Invoke `sbir-profile-builder` via Task tool. Pass mode context if the user selected a mode. The profile builder handles its own interview/document/both flow, validation, and atomic write.

After profile builder returns:
- Re-read profile to confirm it was written
- Extract summary fields (company_name, capability count, SAM status) for display
- If profile builder reports cancellation, exit setup cleanly

### Corpus Ingestion Delegation

Delegate to existing corpus ingestion logic. Accept comma-separated directory paths. Validate each path exists before ingestion. Report results: ingested count, skipped count, already-indexed count.
