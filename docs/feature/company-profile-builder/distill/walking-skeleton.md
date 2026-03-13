# Company Profile Builder -- Walking Skeletons

## Walking Skeleton Design

Three walking skeletons trace thin vertical slices of user value end-to-end.

### WS-1: Founder creates a valid company profile and retrieves it

**User goal**: "I want to create a profile so fit scoring works."

**Driving ports exercised**: ProfileValidationService, ProfilePort (write + read)

**Journey**:
1. Rafael has no existing profile
2. Rafael provides complete company information
3. System validates the profile (passes)
4. System saves the profile atomically
5. Rafael retrieves the profile and sees his company name and capabilities

**Why this is first**: This is the simplest complete journey -- validate, save, read back. It touches both driving ports and proves the core loop works. A stakeholder can see "yes, Rafael can create a profile and the system remembers it."

**Enables implementation of**:
- `scripts/pes/domain/profile_validation.py` (validation service)
- `scripts/pes/ports/profile_port.py` (abstract interface)
- `scripts/pes/adapters/json_profile_adapter.py` (file adapter)
- `templates/company-profile-schema.json` (schema template)

### WS-2: Founder sees validation errors before profile is saved

**User goal**: "I want to catch mistakes before they corrupt fit scoring."

**Driving ports exercised**: ProfileValidationService

**Journey**:
1. Rafael provides profile data with invalid CAGE code and zero employee count
2. System validates and reports 2 specific errors
3. Profile is not saved

**Why second**: Proves the validation gate works as a safety net. Stakeholder can see "the system catches mistakes before saving."

**Enables implementation of**:
- CAGE code format validation (5 alphanumeric)
- Employee count positive integer check
- ProfileFieldError reporting model

### WS-3: Founder updates one section and all other sections are preserved

**User goal**: "I want to add my NASA award without re-entering everything else."

**Driving ports exercised**: ProfilePort (read + write), ProfileValidationService

**Journey**:
1. Rafael has an existing profile with 5 capabilities and 2 past performance entries
2. Rafael adds a NASA past performance entry
3. System validates and saves
4. Profile now has 3 past performance entries
5. Capabilities still has 5 entries (unchanged)

**Why third**: Proves the update flow works without data loss. Stakeholder can see "updating one section does not destroy the rest."

**Enables implementation of**:
- Profile read-modify-write cycle
- Array append behavior
- Section preservation guarantee

---

## Litmus Test

Each walking skeleton passes the 4-point litmus test from test-design-mandates:

| Check | WS-1 | WS-2 | WS-3 |
|-------|------|------|------|
| Title describes user goal | Create profile | Catch errors | Update section |
| Given/When describe user actions | Prepares info, submits | Provides bad data | Adds entry |
| Then describe user observations | Sees company name | Sees error messages | Sees preserved data |
| Non-technical stakeholder confirms | "Yes, I need this" | "Yes, catch mistakes" | "Yes, preserve my data" |
