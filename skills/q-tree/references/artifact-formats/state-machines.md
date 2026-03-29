# State Machines Formatting Rules

Rules for `state-machines.md` artifact. Also see `mermaid.md` for general mermaid rules.

## Structure

One section per entity:

```markdown
## Subscription

States: `Active`, `Paused`, `Cancelled`, `Expired`

(mermaid stateDiagram-v2)

| From | To | Trigger | Guard |
|------|----|---------|-------|
| * | Active | subscribe() | valid token, amount >= minAmount |
| Active | Paused | pause() | onlySubscriber |
| Active | Cancelled | cancel() | onlySubscriber or onlyMerchant |

Invariants:
- Only Active subscriptions can be charged
- Cancelled/Expired are terminal — no transitions out
```

## Rules

- Only include entities where state transitions are a design decision. Skip CRUD entities.
- Mermaid `stateDiagram-v2` showing states and transitions.
- Transition table: From, To, Trigger (function), Guard (who/condition).
- State invariants: what must be true in each state.
