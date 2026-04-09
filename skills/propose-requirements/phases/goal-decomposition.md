# Phase 1: Goal Decomposition

Method: KAOS — decompose goals into sub-goals, leaf goals become requirements. Obstacles become risks.

```
You are a requirements proposer using goal decomposition.

Read the current items from: {{INPUT_FILE}}
Propose up to {{COUNT}} NEW items not already present.

## Method

1. **Extract goals** from the Purpose section (already filled by gather at INIT). Decompose into sub-goals (AND/OR):
   - AND: all sub-goals needed to achieve parent
   - OR: alternative ways to achieve parent (pick one or note as open question)

   Decompose until leaf goals are specific enough to be a single requirement.

2. **Classify leaves:**
   - System responsibility → FR ("System shall...")
   - Environment assumption → C (constraint: "Base vault supports ERC-4626")
   - Stakeholder expectation → NFR ("System shall be ERC-4626 compliant")

3. **Obstacle analysis** — for each goal:
   - "What could prevent achieving this goal?"
   - Each obstacle → R (risk) item
   - Each obstacle → R item with mitigation + acceptance criteria. Only create separate FR if it adds new capability beyond the mitigation.

4. **Core constraints** — if not yet present, propose:
   - Chain, standards, external dependencies as C items
```
