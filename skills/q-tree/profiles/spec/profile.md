# Profile: Smart Contract Specification

## Output

tree_file: docs/q-tree.md

## Coverage Areas

1. **Protocol Goal** — what problem does this solve, for whom, what's the core value proposition
2. **Domain / State** — what contracts exist, what state each holds, responsibility boundaries
3. **Capital Flow** — how tokens enter, move through, and exit the system
4. **Pricing / Oracle** — how prices are determined, what oracle sources, staleness/manipulation handling
5. **Liquidity / Exit** — can users exit, under what conditions, what happens under stress
6. **Risk / Failure** — oracle failure, protocol pause, extreme price moves, attack vectors
7. **Permissions / Governance** — who can call what, admin vs user vs keeper, governance model
8. **Evolution / Extensibility** — upgradeability, strategy replacement, parameter changes

**Economic Questions** (cross-cutting) — weave into other areas, don't treat as a separate block:
- Who profits and how? Who bears costs?
- What are the incentive alignments / misalignments?
- Where can value be extracted (MEV, arbitrage, griefing)?
- Is the fee model sustainable? Does it create perverse incentives?

When decomposing any area above, check if there's an economic angle that needs a sub-question.

## Concern Categories

- Upgradeability / Admin roles / Oracle failure / MEV exposure
- Reentrancy / Emergency procedures / Token edge cases
- Precision loss / Initialization order / Gas limits

## Definition of Done

- **Coverage:** at least one ✓ leaf per relevant area from Coverage Areas (not all 8 apply to every project — skip irrelevant ones)
- **No blockers:** consistency checker found no BLOCKER-severity issues
- **Implementation drift:** questions from the last batch are increasingly implementation-scope (how to code it) rather than architecture-scope (which approach to take)

## Artifacts

Generated in dependency order (each uses prior artifacts as context):

1. `contracts.md` — contract decomposition + state variables
2. `interfaces/*.sol` — Solidity interface files, one per contract
3. `call-diagrams.md` — call sequence diagrams with postconditions
4. `token-flows.md` — token flow traces
5. `access-control.md` — access control matrix
6. `state-machines.md` — entity lifecycles *(only if entities with discrete states exist)*
7. `invariants.md` — invariants per contract
8. `risks.md` — risk mitigation map
9. `overview.md` — overview + key decisions
10. `plan.md` — development plan (tasks, dependencies, order)
11. `specs/*.t.sol` — Foundry test skeletons, one abstract contract per contract
12. `gaps.md` — collected gaps (only if gaps exist) — always last

## Summarizer

ref: profiles/spec/summarizer.md

## Review

enabled: yes
ref: profiles/spec/reviewer.md

## Pattern Library

url: https://raw.githubusercontent.com/xeyax/smart-contract-patterns/master/patterns

## Constraints

- Don't restate platform guarantees. EVM/Solidity already guarantees: transaction atomicity (all-or-nothing), msg.sender authentication, overflow protection (Solidity 0.8+), gas limits. These are given by the execution environment — don't generate questions, answers, or invariants about them. Only ask about things the architect must decide.

## Domain Model Cross-Validation

enabled: yes
file: docs/domain-model.md
