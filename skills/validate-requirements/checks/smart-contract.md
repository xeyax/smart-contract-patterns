# Smart Contract Domain Check (Tier 3)

Domain-specific checks for smart contract requirements. Based on Hacken 15 categories, OWASP SCSVS, and common audit findings.

```
You are a smart contract requirements domain checker.

Read the requirements from: {{INPUT_FILE}}
Read the threat categories from: rules/smart-contract-threats.md

For each category in smart-contract-threats.md, check: is there at least one requirement addressing it? If the category is relevant to this project but not addressed → flag. If clearly not relevant → skip.

## 1. Access Control

- For each state-changing function implied by FRs: who can call it?
- Are roles defined (owner, admin, keeper, guardian, user)?
- Is role management described (grant, revoke, transfer)?
- Is there a requirement for privilege escalation prevention?
- Timelock on critical operations?
- Multi-sig or governance requirements?

## 2. Reentrancy

- Are there requirements involving external calls (token transfers, oracle reads, cross-contract calls)?
- If yes: is reentrancy protection required?
- Cross-function reentrancy? Cross-contract read-only reentrancy?

## 3. Arithmetic & Precision

- Are there calculations (fees, shares, ratios, prices)?
- If yes: is rounding direction specified (favor user vs protocol)?
- Is decimal handling specified (18 decimals, 6 decimals, mixed)?
- Dust amount behavior?
- Overflow considerations (even with Solidity 0.8+, casting)?

## 4. Initialization & Upgradeability

- Is the system upgradeable or immutable? Must be explicitly stated.
- If upgradeable: storage layout compatibility? Upgrade authorization? Rollback?
- If immutable: migration path described?
- Initialization: can it be called more than once?

## 5. Business Logic & State Transitions

- Are all state transitions defined (see completeness check)?
- Are invariants stated (what must ALWAYS be true)?
- Are there operations that must be atomic (all-or-nothing)?
- Are there operations with ordering requirements (X before Y)?

## 6. Economic Attacks

- Oracle manipulation: price source requirements? TWAP vs spot? Deviation bounds?
- Flash loan attacks: can state be manipulated within a single tx?
- MEV/sandwich: are value-extractable operations identified?
- Incentive alignment: does the fee model create perverse incentives?
- Token economics: inflation, deflation, supply caps?

## 7. Denial of Service

- Are there loops over user-controlled data (arrays, mappings)?
- Gas limits on batch operations?
- Can one user block others (griefing)?
- Can the contract get stuck (state-locking)?

## 8. Asset & Balance Safety

- Are all token flows described (entry, exit, internal movement)?
- Emergency withdrawal mechanism?
- Fund reconciliation (can assets get stuck in the contract)?
- Are there accounting invariants (sum of balances = total)?

## 9. Front-running & MEV

- Are there operations where transaction ordering matters?
- Slippage protection? Deadline parameters?
- Commit-reveal scheme needed?
- Are deposit/withdrawal queues sequential or parallel?

## 10. Randomness

- Does the system use randomness? If yes: source specified?
- Block hash, Chainlink VRF, or other?
- (Skip if not applicable)

## 11. Time Manipulation

- Does the system depend on block.timestamp?
- If yes: tolerance for miner manipulation (~15 seconds)?
- Lock periods, cooldowns, deadlines: are they specified?

## 12. External Interaction Risks

- External calls: what happens on revert? On unexpected return value?
- Token standards: fee-on-transfer? Rebasing? ERC-777 hooks? Missing return value (USDT)?
- External protocol dependencies: what if they upgrade? Pause? Get hacked?
- Bridge interactions? Cross-chain message handling?

## 13. Chain & Ecosystem Specific

- Target chain(s) specified?
- EVM version constraints?
- Available opcodes (PUSH0, MCOPY, transient storage)?
- L2-specific: sequencer downtime, forced transactions, gas model differences?

## 14. Gas Efficiency

- Gas budgets per operation specified?
- Are there operations that could exceed block gas limit?
- Storage optimization requirements?

## 15. Documentation-Code Alignment

- This check is more relevant at implementation time, but at requirements level:
- Are requirements clear enough that code-spec mismatch would be detectable?
- Are edge cases explicit enough to test?

## Output

For each category:
```
✓ Category: covered by FR-001, FR-005, NFR-002
⚠ Category: partially covered — [specific gap]
✗ Category: not addressed — [why it matters for this project]
- Category: not applicable
```

Summary:
```
Smart Contract Domain Coverage: X/Y relevant categories addressed
Critical gaps: [list]
```
```
