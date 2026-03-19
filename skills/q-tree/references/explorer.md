# Explorer — EXPLORE Phase Behavior

Read this file when entering EXPLORE (lazy load — not at INIT).

Exploration is a focused narrowing session on a single question (or a cluster of related questions). The goal is to converge to an answer through constraint accumulation and variant elimination — not by presenting menus of options.

## Entry

User pushes back on a question and accepts the offer to explore.

## Exploration trail in the tree

During exploration, the exploring node accumulates children that represent the exploration state — not sub-questions. Exploration-specific markers:
- `✗` — rejected variant (with short reason)
- `!` — constraint discovered during exploration
- `→` — active variant still being considered

```
- ? Oracle design
  - ! off-chain simulation unverifiable in EVM
  - ! oracle error observable → exploitable
  - ✗ Cash-flow → kills fair share pricing in multi-user vault
  - ✗ Report-based → stale pricing creates arbitrage
  - ✗ Simulation-based → unverifiable on-chain
  - → Chainlink + TWAP + emergency [d:oracle-design]
```

When exploration completes, the winning variant becomes `✓`. Rejected (`✗`) and constraints (`!`) stay as permanent record. The node itself becomes `✓` with the winning answer.

```
- ✓ Oracle design → Chainlink + TWAP + emergency [d:oracle-design]
  - ! off-chain simulation unverifiable in EVM
  - ! oracle error observable → exploitable
  - ✗ Cash-flow → kills fair share pricing in multi-user vault
  - ✗ Report-based → stale pricing creates arbitrage
  - ✗ Simulation-based → unverifiable on-chain
```

## Recording after every user message

After each user message during exploration, show what you're about to record and write it to the tree file immediately. This ensures nothing is lost if the session breaks.

```
Recording: ✗ Report-based (stale pricing → arbitrage). Confirm? [Y/fix]
```

If the user confirms (Y or just continues the conversation) → write to tree. If the user corrects → fix and write. Always write to the tree file before responding with the next exploration step.

For constraints:
```
Recording: ! on-chain verification of off-chain simulation impossible in EVM. Confirm? [Y/fix]
```

For reframing:
```
Recording: updating question "How to calculate NAV?" → "How to make oracle error non-exploitable?" Confirm? [Y/fix]
```

## Behavior

Shift from "propose and confirm" to "narrow the space":
- **Don't present menus.** Don't say "here are 5 options, pick one." Instead, ask what properties the user cares about, what constraints exist, what's unacceptable.
- **Track constraints.** When the user says "I don't want X" or "it must support Y" — record as `!` child node. Show how it eliminates variants.
- **Track rejected variants.** When a variant is discarded, record as `✗` child node with the reason. Never re-propose a rejected variant.
- **Keep answers short.** Max 5-7 sentences per response during exploration. If the user wants deeper explanation, they'll ask. Don't lecture.
- **Show exploration status** periodically (every 2-3 exchanges):
  ```
  [Exploring: "Oracle design"]
  Constraints: 3 (non-manipulable, survive oracle death, FV-friendly)
  Rejected: 4 (cash-flow, report-based, TWAP-only, keeper-reported NAV)
  Active: 1 (Chainlink + TWAP cross-check + emergency)
  Ready to confirm, or keep narrowing?
  ```

## Constraint promotion

If a constraint discovered during exploration applies to the whole project (not just this question), promote it to the global Constraints section in the tree header AND record as `!` child of the current node. Tell the user: `"Promoting constraint to global: [constraint]. This may affect other decisions."`

## Reframing

The user may redefine the question itself ("the problem isn't error, it's whether error is exploitable"). This is valuable — update the question text in the tree and continue exploration with the new framing. If two questions turn out to be tightly coupled (e.g., "share pricing" and "cost allocation"), reframe one to cover both aspects — don't try to explore multiple nodes simultaneously.

## Logging

After each exploration exchange (not just at the end), delegate logging to a background subagent with `references/session-logger.md`. This ensures the exploration trail is preserved even if the session breaks mid-exploration.

## Exit conditions

- User confirms an answer → winning variant becomes ✓, write fuller explanation to Details → proceed to CHECK → then EXPAND
- User says "postpone" / "let's move on" → keep as → or ?, exploration trail already in tree → proceed to CHECK → then EXPAND
- User has been going in circles (3+ rounds without new constraints or eliminated variants) → agent suggests: `"We've been exploring for N rounds. Want to confirm what we have, postpone, or reframe the question?"`
