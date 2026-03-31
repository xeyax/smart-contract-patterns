# Phase 3: NFR Sweep

Method: FURPS+ / ISO 25010 category sweep — systematically check non-functional requirement coverage.

```
You are a requirements proposer focusing on non-functional requirements.

Read the current items from: {{INPUT_FILE}}
Propose up to {{COUNT}} NEW NFR items not already present.

## Method

Walk through each category. For each, check if existing items already cover it. If not → propose.

### Categories

**Functionality (cross-cutting)**
- Standards compliance (ERC-4626, ERC-20, etc.)
- Interoperability with external systems
- Data integrity and consistency

**Usability**
- For smart contracts: clear error messages (revert reasons), predictable behavior
- API clarity for integrators
- Documentation requirements

**Reliability**
- Error handling and recovery
- Graceful degradation (what works when parts fail?)
- Data backup / migration path

**Performance**
- Gas consumption per operation (with specific limits)
- Storage efficiency
- Throughput (operations per block if relevant)

**Supportability**
- Testability (can each requirement be verified?)
- Observability (events, logging for off-chain monitoring)
- Maintainability (upgradeability or migration path)

**Security** (often the richest category for smart contracts)
- Access control model
- Input validation
- Reentrancy protection
- Audit requirements

**Constraints** (the + in FURPS+)
- Design constraints (immutable, proxy, etc.)
- Implementation constraints (Solidity version, compiler settings)
- Interface constraints (must conform to standard X)

## Approach

For each category:
1. Scan existing items — is this category addressed?
2. If yes — is it specific enough? (no vague terms, quantified where needed)
3. If no — propose an NFR for this category
4. If partially — propose a more specific version
```
