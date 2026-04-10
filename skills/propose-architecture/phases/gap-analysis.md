# Phase 4: Gap Analysis

Method: Completeness criteria sweep + tradeoff analysis.

```
You are an architecture proposer doing gap analysis.

Read requirements from: {{REQUIREMENTS_FILE}}
Read current architecture tree from: {{INPUT_FILE}}
Read completeness criteria from: validate-architecture/rules/completeness-criteria.md
Propose up to {{COUNT}} NEW decisions not already present.

## Method

1. **Requirements traceability:**
   - For each FR/NFR in requirements → does an AD exist? Uncovered → propose AD.
   - For each R in requirements → is it resolved? Either propose AD that mitigates it, or propose marking it "accepted" with reasoning. Every R must be addressed.

2. **Completeness criteria sweep:**
   - Walk all 12 criteria from completeness-criteria.md
   - For each gap found → propose AD to close it

3. **Error handling decisions:**
   - For each external call in architecture → what if it fails?
   - For each state → what if unexpected input?
   - Missing error handling → propose AD

4. **Tradeoff identification:**
   - Which ADs have tensions between them?
   - "Low gas" vs "comprehensive validation" — which wins?
   - Unresolved tradeoffs → propose AD that makes the choice explicit

5. **Persona sweep:**
   - Attacker: "what architectural weakness remains?"
   - Auditor: "what would I flag as unclear?"
   - Operator: "what do I need to manage this in production?"

This is the catch-all phase. If it finds nothing → architecture is likely complete.
```
