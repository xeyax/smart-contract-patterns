# Architecture Completeness Criteria

Set-level checks. Used by proposer (to find what to generate) and validator (to find what's missing).

## 1. Requirement Coverage

Criterion: every FR, NFR, and mitigated R from requirements has ≥1 architecture decision addressing it.

Gap: FR-003 says "fee on net gains" but no decision about HOW to track gains.

## 2. Component Decomposition

Criterion: all major components/contracts identified with clear responsibilities and boundaries.

Gap: "strategy" mentioned in decisions but never defined as a component with responsibility.

## 3. Interface Clarity

Criterion: for every pair of components that interact, the boundary is defined — who calls whom, with what data.

Gap: "vault delegates to strategy" but no decision about the interface between them.

## 4. State Completeness

Criterion: for each component, its state (what it stores) is identified.

Gap: component has decisions about behavior but no decision about what data it holds.

## 5. Flow Coverage

Criterion: every user-facing operation (from FRs) has a decision about how it flows through the components.

Gap: FR says "users can redeem" but no decision traces the redeem flow through components.

## 6. Error Handling

Criterion: for each external interaction and failure mode (from R items), there's a decision about how the system handles it.

Gap: R says "oracle may fail" but no decision about fallback behavior.

## 7. Access Control Model

Criterion: every privileged operation has a decision about who can perform it and how authorization works.

Gap: "owner can pause" but no decision about what "owner" means (EOA? multisig? timelock?).

## 8. Consistency

Criterion: no contradictions between decisions. No decision assumes something another decision contradicts.

Types of inconsistency to check:
- Behavioral: same operation described differently in two decisions
- Interface: caller and callee disagree on parameters
- State: two decisions imply different state for the same component

## 9. Constraint Satisfaction

Criterion: every constraint (C items) from requirements is reflected in architecture decisions.

Gap: C says "Ethereum mainnet" but decisions reference L2-specific features.

## 10. Risk Mitigation

Criterion: every risk with mitigation (not "accepted") has a concrete architectural mechanism.

Gap: R says "reentrancy protection needed" but no decision about which pattern to use.

## 11. Decision Dependencies

Criterion: if decision A depends on decision B, the dependency is explicit. No circular dependencies.

Gap: AD-005 assumes AD-003 but doesn't reference it.

## 12. Scope Alignment

Criterion: no decisions about things not covered by requirements. All requirements have decisions.

Gap: decision about "off-chain indexer" when no requirement mentions it (or it's deferred as out of scope in requirements).
