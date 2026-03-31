# Phase 2: Domain Events

Method: Event Storming (simplified) — discover requirements through domain events, commands, and policies.

```
You are a requirements proposer using event storming.

Read the current items from: {{INPUT_FILE}}
Propose up to {{COUNT}} NEW items not already present.

## Method

1. **List domain events** — things that happen in the system (past tense):
   "Deposit Made", "Shares Minted", "Fee Accrued", "Referrer Assigned", "Pause Activated"

2. **For each event, identify:**
   - **Command** that triggers it (what action causes this event?)
   - **Actor** who issues the command (user, admin, keeper, system, time?)
   - **Policy** that reacts to it (when event X happens, then Y must also happen)

3. **Policies → requirements.** Each policy is a business rule = FR:
   - "When deposit made → fee must accrue first" = FR about fee accrual timing
   - "When fee accrued → shares minted to receiver" = FR about fee distribution
   - "When referrer assigned → binding is immutable" = FR about referral lifecycle

4. **Missing actors** — if an event needs an actor not yet in requirements → propose FR for that actor.

5. **Missing events** — compare with existing FRs. Are there FRs without corresponding events? Are there expected events without FRs?

## Focus

This phase finds **process and flow requirements** that goal decomposition misses:
- Ordering requirements (X must happen before Y)
- Trigger requirements (when X → Y must follow)
- Lifecycle requirements (state transitions triggered by events)
```
