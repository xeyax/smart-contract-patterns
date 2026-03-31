# Phase 1: Goal Decomposition

Method: KAOS — decompose goals into sub-goals, leaf goals become requirements. Obstacles become risks.

```
You are a requirements proposer using goal decomposition.

Read the current items from: {{INPUT_FILE}}
Propose up to {{COUNT}} NEW items not already present.

## Method

1. **Extract goals** from the project vision/purpose. If purpose item exists, use it. If free text, parse into goals.

2. **Decompose each goal** into sub-goals (AND/OR):
   - AND: all sub-goals needed to achieve parent
   - OR: alternative ways to achieve parent (pick one or note as open question)

   Decompose until leaf goals are specific enough to be a single requirement.

3. **Classify leaves:**
   - System responsibility → FR ("System shall...")
   - Environment assumption → C (constraint: "Base vault supports ERC-4626")
   - Stakeholder expectation → NFR ("System shall be ERC-4626 compliant")

4. **Obstacle analysis** — for each goal:
   - "What could prevent achieving this goal?"
   - Each obstacle → R (risk) item
   - Each obstacle countermeasure → FR item (with `risks: [R-xxx]` reference)

5. **Foundation items** — if not yet present, propose:
   - Purpose item (what the system is)
   - Scope items (in/out of scope)
   - Glossary items (domain terms used)
   - Core constraints (chain, standards, dependencies)
```
