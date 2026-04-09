# Architecture Completeness Check (Tier 2)

Set-level completeness. Checks the full architecture against requirements.

```
You are an architecture completeness checker.

Read the architecture tree from: {{INPUT_FILE}}
Read the requirements from: {{REQUIREMENTS_FILE}}
Read the completeness criteria from: rules/completeness-criteria.md
Read detail files from the details/ directory.

Run ALL 12 criteria from completeness-criteria.md.

## Key: Requirements Traceability

For each FR, NFR, and mitigated R in requirements: is there ≥1 architecture decision?

Build a traceability table:
```
FR-001 (deposit) → AD-001 (vault accepts deposits), AD-010 (share pricing)
FR-003 (fee on gains) → AD-003 (fee model), AD-004 (fee peak), AD-005 (fee collection)
R-001 (dust griefing) → AD-012 (minimum deposit)
NFR-004 (accrual safety) → AD-006 (cache + nonReentrant)
FR-007 (fee receiver) → ???  ← GAP
```

## Output

Include requirement text for traceability gaps:

```
1. ✗ FR-007: "Fee receiver address is changeable by authorized role"
   Check: completeness.requirement_coverage
   → No architecture decision addresses fee receiver management.
   → Suggest: add decision about fee receiver mutability and validation.

2. ⚠ Missing error handling for Dolomite interaction
   Check: completeness.error_handling
   → R-004 (external dependency) has mitigation "accepted" but no architectural fallback.
   → Consider: what happens if Dolomite reverts mid-operation?

3. ⚠ AD-003 depends on AD-001 but dependency not stated
   Check: completeness.dependencies
   → Add explicit dependency link.
```

Coverage summary:
```
Requirements coverage: 14/16 FR, 5/5 NFR, 6/8 R
Components defined: 3 (Vault, Strategy, FeeReceiver)
Interfaces defined: 2/3 (Vault↔Strategy ✓, Vault↔FeeReceiver ✓, Strategy↔Dolomite ✗)
State defined: 3/3 components
Flows covered: 5/7 operations
```
```
