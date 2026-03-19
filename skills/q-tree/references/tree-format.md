# Tree File Format

## Structure principle

**Decomposition:** parent-child = child is a sub-question needed to fully answer the parent.

- **Parent** = composite question that can't be answered without resolving sub-questions
- **Child** = part of the parent's answer
- **Parent auto-closes** when all children are ✓ (see "Update tree file" in SKILL.md)
- **Consequence questions** = new children that appear when an answer reveals new sub-questions (handled by question-generator)

```
- ? Shares minting                              ← composite, OPEN (has unresolved children)
  - ✓ Standard → ERC-4626
  - ✓ NAV calculation → idleBalance + collateral - debt
  - ? First depositor protection — virtual shares / min deposit
  - → Mint timing → after leverage (delta NAV)  ← consequence of NAV answer

↓ all children resolved → parent auto-closes:

- ✓ Shares minting                              ← auto-closed
  - ✓ Standard → ERC-4626
  - ✓ NAV calculation → idleBalance + collateral - debt
  - ✓ First depositor protection → virtual shares
  - ✓ Mint timing → after leverage (delta NAV)
```

**One level at a time.** Decompose one level deep per round. Deeper levels appear after the current level is answered.

## File template

```markdown
# Q-Tree: [Project Name]

> Goal: [user's goal as stated]
>
> Resolved: N | Suggested: N | Open: N

Markers: ✓ confirmed | → suggested | ? open | ~ auto

## Tree

- ~ Chain → Arbitrum (from goal)
- ~ Base asset → USDC (from goal)
- ? Contract architecture
  - ✓ Decomposition → Vault + Strategy (Yearn pattern)
  - → Share model → ERC-4626 (composable, audited) [d:shares]
  - ? Value flows
    - ✓ Entry → user deposits USDC, mint shares
    - ? Fee model — performance / management / both [d:fees]
    - ~ Fee recipient → treasury multisig (from access control)

## Details

### [d:shares] Share model
- ERC-4626 (recommended) — composable, audited implementations
- Custom (possible) — more flexibility but higher audit cost

### [d:fees] Fee model
- Performance only (10%) — simple, aligned with users
- Management (2% AUM) — predictable but hurts small depositors
Agent note: MVP scope → performance only simplest
```

## Markers

| Marker | Meaning | User action needed |
|--------|---------|-------------------|
| `✓` | Confirmed — user accepted or answered directly | No |
| `→` | Suggested — agent proposes, awaiting confirmation | Confirm or override |
| `?` | Open — agent can't decide, needs user input | Answer required |
| `~` | Auto — derived from prior answers, shown for transparency | Override if wrong |
| `!` | Constraint — discovered during exploration, limits solution space | Override if wrong |
| `✗` | Rejected — variant eliminated during exploration (with reason) | No |

`!` and `✗` only appear inside exploration trails — children of nodes being discussed during pushback. If a question becomes irrelevant, delete it from the tree and note the reason in the parent's Details section.

## Conventions

- Every node is a markdown list item: `- marker question → answer [d:tag]`
- Tree depth = nested list indent (2 spaces + `- ` per level)
- `[d:tag]` links to a Details section for complex questions
- Composite nodes (with children) auto-close to `✓` when all **question** children (`?`, `→`, `~`) are resolved. Exploration markers (`✗`, `!`) are not questions and are excluded from auto-close
- Leaf nodes (no children) are resolved directly by the user
- Counters in header updated after every batch

## Details section: level of abstraction

Details explain **why** (trade-offs, options, reasoning), not **how** (implementation).

Good:
```
### [d:strategy-sep] Strategy separation
- Separate contract (Yearn pattern) — strategy replaceable without user migration
- Embedded in vault — simpler but locked to one strategy
- Strategy only manages position; vault owns accounting and user-facing logic
```

Bad (too detailed — function signatures, parameters, storage):
```
### [d:strategy-functions] Strategy functions
| Function | Caller | What it does |
| deploy(uint256 amount) | Vault | Pull from vault, build position |
| rebalance() | Keeper | Adjust LTV to target |
```

Rule: if it looks like an interface definition or API spec, it's too detailed for q-tree. That belongs in ADR or implementation planning.

**Details = only confirmed information.** Details expand on what the user confirmed or what directly follows from the answer. If writing a Detail reveals sub-decisions that weren't discussed (struct fields, ID generation, mapping structure), those must become new questions in the next batch — not silently written into Details.

**Exploration trail.** Constraints (`!`) and rejected variants (`✗`) live in the tree as child nodes of the discussed question. The Details section provides the fuller "why" — written when the user confirms an answer.

```markdown
### [d:oracle-design] Oracle design
Chainlink primary + TWAP cross-check + emergency state machine.
Only approach satisfying all constraints — non-manipulable (Chainlink is off-chain),
survives Chainlink death (emergency mode with orderly wind-down), FV-friendly (FREI-PI invariants as safety net).
See tree for rejected variants and constraints.
```

Keep Details concise for explored nodes — the tree already shows what was rejected and why. Details explain the positive case: why the chosen approach works.

Example: user confirms "✓ Data model → three mappings: subscriptions, merchants, stores".
- OK in Detail: *why* three mappings (separation of concerns, gas), *why* events instead of on-chain history
- NOT OK in Detail: `Subscription(id, subscriber, storeId, amount, interval, nextChargeAt, endAt, active)` — these are sub-decisions the user hasn't seen. They should be child questions.
