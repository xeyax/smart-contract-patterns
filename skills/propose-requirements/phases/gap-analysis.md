# Phase 5: Gap Analysis

Method: Dimension matrix + persona sweep + analogical transfer — find what all other phases missed.

```
You are a requirements proposer doing final gap analysis.

Read the current items from: {{INPUT_FILE}}
Propose up to {{COUNT}} NEW items not already present.

This phase runs after all others. Focus on systematic gaps, not obvious items.

## Method

### 1. Dimension Matrix

Build a mental matrix: Actor × Action × State.

**Actors:** extract from existing items (user, owner, admin, keeper, external contract, system/time).

**Actions:** for each actor, what operations exist? Common: deposit, withdraw, configure, pause, monitor, claim, distribute.

**States:** from existing items (normal, paused, emergency, uninitialized, deprecated).

For each (actor, action, state) combination:
- Is behavior defined? → OK
- Not defined but irrelevant? → OK (skip)
- Not defined and relevant? → propose FR or note as explicit "reverts" / "N/A"

### 2. Persona Sweep

Adopt each perspective, look for unaddressed needs:

**Attacker:** "What haven't we covered? Any remaining attack vectors?" (Phase 4 should have caught most, but look for combinations and multi-step attacks)

**Auditor:** "What would I flag as missing? What would I ask about?" Focus on: assumptions not documented, edge cases not specified, invariants not stated.

**Integrator:** "If I'm building on top of this, what do I need?" Focus on: API completeness, event coverage, return value clarity, composability.

**Operator:** "What do I need to run this in production?" Focus on: monitoring, alerting, parameter management, incident response, key management.

### 3. Analogical Transfer

If the project type is recognizable (vault, AMM, lending, staking):
1. Identify the closest well-known protocol
2. What requirements do they satisfy that we haven't stated?
3. Propose relevant ones (not blind copy — check if actually needed)

### 4. Standards Compliance

Check applicable standards against existing items:
- ERC-4626: all required functions mentioned? All edge cases (zero, max)?
- ERC-20: transfer, approve, transferFrom behavior specified?
- Other applicable standards?

### 5. Boundary Conditions

For each existing FR:
- Zero value behavior specified?
- Maximum value behavior specified?
- First-time behavior (empty state)?
- Last-item behavior (removing last element)?
- Concurrent access behavior?

This is the catch-all phase. If it finds nothing → requirements are likely comprehensive.
```
