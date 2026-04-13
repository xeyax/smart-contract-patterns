# Generate specs/*

You are a subagent generating executable specifications. **Fresh context is critical here** — you need full attention on coverage.

## Domain

{{DOMAIN}}

Spec format and test framework conventions are specified in the domain block above and in `{{PROFILE_DIR}}/formats/specs.md` (e.g. Solidity + Foundry `.t.sol` abstract test contracts / Python + pytest abstract base classes / TypeScript + Vitest suites).

## Read (in this order)

1. Tree: `{{DATA_FILE}}` — source of truth for all decisions
2. Details: `{{DETAILS_DIR}}/AD-*.md`
3. All prior artifacts via named placeholders — whichever the profile generated. Use only named placeholders (e.g. `{{COMPONENTS_OUTPUT}}`, `{{INTERFACES_OUTPUT}}`, `{{CALL_DIAGRAMS_OUTPUT}}`, `{{DATA_FLOWS_OUTPUT}}`, `{{ACCESS_CONTROL_OUTPUT}}`, `{{STATE_MACHINES_OUTPUT}}`, `{{INVARIANTS_OUTPUT}}`, `{{RISKS_OUTPUT}}`, `{{PUBLIC_API_OUTPUT}}`, `{{ERROR_TAXONOMY_OUTPUT}}`, and any domain-specific ones the profile declares). If a placeholder is empty, the profile skipped that entry — skip the read.
4. Formatting rules: `{{PROFILE_DIR}}/formats/specs.md`

## Write

`{{OUTPUT}}` — a glob pattern (e.g. `artifacts/specs/*.py`). Write one abstract test file per component under the directory of the pattern.

**Zero-item case:** if no component has any checkable claim to spec (no invariants, no postconditions, no guards — extremely rare), write a sentinel file `<glob-dir>/.none` (e.g. `artifacts/specs/.none`) containing a one-line explanation, and return `written: {{OUTPUT}} (none)`.

## Why this artifact exists

Expressing decisions as executable checks exposes gaps that prose hides. If a claim cannot be tested, the architecture is underspecified.

## specs/* structure

Five sections per file (adapt naming to the test framework — see format rules):

1. **Invariants** ← from `{{INVARIANTS_OUTPUT}}`
2. **Access control / permissions / guards** ← from `{{ACCESS_CONTROL_OUTPUT}}` (if present) or from rules in interfaces. Every guard → a negative test. Includes typed error checks, reentrancy/concurrency guards, input validation, bound checks.
3. **Postconditions** ← from `{{CALL_DIAGRAMS_OUTPUT}}`. Every quantitative `POST:` → an assertion with exact formula. For compound operations (function calls another internally), verify ALL side-effects, not just the return value. For data-moving functions, assert BOTH source and destination states with exact values.
4. **State machine / lifecycle** ← from `{{STATE_MACHINES_OUTPUT}}` (if present). Every valid transition → positive test. Every invalid transition → negative test. Also verify functions NOT mentioned in the state machine still work in each state.
5. **Behavioral properties** — system-wide correctness: proportionality, round-trip, linearity, conservation, idempotency, rounding direction, entry-point equivalence (multiple functions doing the same thing → same result), recovery scenarios (behavior after adverse conditions).

Rules:
- **Abstract helpers / fixtures at the top** — one per external dependency. Developer inherits / implements the concrete wiring.
- **No implementation logic.** Specs only assert what must be true.
- **Use interfaces from `{{INTERFACES_OUTPUT}}`** for all calls. Never import concrete implementations.
- **Traceability matrix at the top of each file** — map every checkable claim to a spec function or `[GAP]`. Sources: call-diagrams POST lines, invariants, access-control restrictions, state-machine transitions, risk mitigations marked COVERED, ✓ AD nodes with Details.

## Tree completeness checklist

After generating all 5 sections, walk every `✓` AD node that has a Details section. For each miss, add a test to the matching section or record `[GAP]` in the traceability matrix.

1. **Formula check** — every formula in Details (`## Formula` section) → an exact-value assertion.
2. **Guard check** — every guard from access-control (or interface-level validation) has a negative test. Includes reentrancy/concurrency tests with a callback, bound checks, input validation.
3. **Recovery check** — every ✓ AD about behavior after adverse conditions (drawdown, pause, zero state, failed external call) → end-to-end scenario.
4. **Equivalence check** — multiple entry points for the same operation → equality on outputs + verify the simple path does NOT trigger the rich path's side-effects.
5. **Boundary/delta check** — every function that moves value/data between entities → assert BOTH source and destination states with exact values.

## Rules

- **Do not invent.** If information is missing → `[GAP]` in the traceability matrix. `gaps.md` is produced by a separate step (`gen-gaps`) that collects these from all artifacts and specs.
- **Every ✓ node with Details MUST be covered** — by at least one spec or traceability-matrix entry (which can be `[GAP]`).
- Specs reference interface types — no concrete component types, no deployment logic.

## Return

`written: {{OUTPUT}}` (`N specs`).
