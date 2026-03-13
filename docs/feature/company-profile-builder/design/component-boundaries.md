# Company Profile Builder -- Component Boundaries

## Component Inventory

### New Components (8 files)

| # | Component | Type | Location | Owner |
|---|-----------|------|----------|-------|
| 1 | Profile builder agent | Markdown | `agents/sbir-profile-builder.md` | Conversational logic |
| 2 | Profile domain skill | Markdown | `skills/profile-builder/profile-domain.md` | Domain knowledge |
| 3 | Profile setup command | Markdown | `commands/sbir-proposal-profile-setup.md` | CLI entry point |
| 4 | Profile update command | Markdown | `commands/sbir-proposal-profile-update.md` | CLI entry point |
| 5 | Profile validation service | Python | `scripts/pes/domain/profile_validation.py` | Schema enforcement |
| 6 | Profile port | Python | `scripts/pes/ports/profile_port.py` | Abstract interface |
| 7 | Profile adapter | Python | `scripts/pes/adapters/json_profile_adapter.py` | File persistence |
| 8 | Profile schema template | JSON | `templates/company-profile-schema.json` | Schema source of truth |

### Modified Components (1 file)

| Component | Location | Change |
|-----------|----------|--------|
| Fit scoring skill | `skills/topic-scout/fit-scoring-methodology.md` | Update missing-profile message to reference `/sbir:proposal profile setup` |

---

## Boundary Definitions

### Boundary 1: Commands (Driving Adapters)

**Responsibility**: Parse user intent, dispatch to agent.

| Command | Dispatches To | Context Passed |
|---------|--------------|----------------|
| `sbir-proposal-profile-setup.md` | `@sbir-profile-builder` | Mode: setup (new profile creation) |
| `sbir-proposal-profile-update.md` | `@sbir-profile-builder` | Mode: update (modify existing section) |

**Does NOT**: Contain business logic, validate data, read/write files.

### Boundary 2: Agent (Application Core)

**Responsibility**: Orchestrate the multi-step profile creation and update flows.

Owns:
- Mode selection (documents / interview / both)
- Document content interpretation (LLM extracts fields from text)
- Conversational interview (asks questions, records responses)
- Profile draft assembly (merge extraction + interview data)
- Preview rendering (human-readable display)
- User interaction control flow (confirm / edit / cancel)
- Overwrite protection dialog (detect existing, offer options)

Does NOT own:
- Schema validation (delegates to Python validation service)
- File I/O (delegates to Python adapter)
- Schema definition (reads from template)

### Boundary 3: Skill (Knowledge Layer)

**Responsibility**: Supply domain knowledge loaded on demand.

Owns:
- Profile schema field definitions with business context
- Fit scoring impact explanation per field (weights, thresholds)
- Interview question templates per section
- Valid value enumerations (socioeconomic categories, clearance levels)
- Validation rule explanations (why CAGE must be 5 chars, etc.)

Does NOT own:
- Validation execution (that is the Python service)
- Conversational flow control (that is the agent)

### Boundary 4: Validation Service (Domain Layer)

**Responsibility**: Deterministic schema validation of profile data.

Owns:
- JSON Schema validation (structural completeness, type checking)
- Business rule validation (CAGE = 5 alphanumeric, clearance in enum, employee_count > 0)
- Field-level error reporting (field name, current value, expected format)
- Validation result aggregation (pass/fail with error list)

Does NOT own:
- File I/O (pure domain -- receives dict, returns result)
- Profile assembly (that is the agent)
- Schema definition storage (reads schema from template at invocation)

### Boundary 5: Profile Port + Adapter (Infrastructure Layer)

**Responsibility**: Profile persistence with atomic writes and crash safety.

Owns:
- File existence detection
- File metadata reading (last modified date)
- Atomic write pattern (tmp -> bak -> rename)
- Directory creation (~/.sbir/ if absent)
- File permission setting (600 on Unix)
- Profile loading (read and parse JSON)
- Backup creation

Does NOT own:
- Validation (delegates to domain service)
- Profile content construction (receives complete dict)

---

## Dependency Direction

```
Commands (driving adapter)
    |
    v
Agent (application core) --loads--> Skill (knowledge)
    |
    v
Validation Service (domain) <--- no infrastructure imports
    ^
    |
Profile Port (abstract interface)
    ^
    |
Profile Adapter (driven adapter) --depends on--> Port
```

All dependencies point inward. Adapter depends on port interface. Domain has zero infrastructure imports. Agent orchestrates but does not contain validation or persistence logic.

---

## Cross-Component Integration Points

### Profile Builder <-> Topic Scout

- **Shared artifact**: `~/.sbir/company-profile.json`
- **Contract**: JSON structure defined in `templates/company-profile-schema.json`
- **Direction**: Profile builder writes; topic scout reads
- **Risk**: Schema mismatch causes silent scoring degradation
- **Mitigation**: Single schema template is source of truth for both

### Profile Builder Agent <-> Validation Service

- **Interface**: Agent passes profile dict to validation service; receives pass/fail with errors
- **Direction**: Agent invokes validation; validation returns result
- **No coupling**: Agent does not know validation implementation; validation does not know agent

### Profile Builder Agent <-> Profile Adapter

- **Interface**: Agent requests read/write/exists/metadata through port interface
- **Direction**: Agent uses port abstraction; adapter implements it
- **No coupling**: Agent does not know file paths or write mechanics
