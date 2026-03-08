"""Step definitions for walking skeleton scenarios.

Walking skeletons trace thin vertical slices of user value E2E.
These step definitions delegate to the same driving ports as focused
scenarios but compose longer journeys.
"""

from __future__ import annotations

import pytest
from pytest_bdd import scenarios

# Link to walking skeleton feature file
scenarios("../features/walking_skeleton.feature")

# Walking skeleton steps reuse step definitions from other domain modules.
# pytest-bdd discovers steps by importing them.
# All Given/When/Then steps are already defined in:
#   - common_steps.py (plugin active, proposal state setup)
#   - proposal_steps.py (new proposal, status, Go/No-Go)
#   - enforcement_steps.py (PES blocking, guidance)
#   - corpus_steps.py (corpus ingestion)
#
# No additional step definitions needed here -- walking skeletons
# compose existing domain steps into E2E journeys.
