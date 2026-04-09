# Quality Check (Tier 1)

Per-item quality. Fast, runs after every batch.

```
Read the requirements from: {{INPUT_FILE}}
Read and apply ALL rules from: rules/quality-rules.md

For each issue, include full requirement text:

1. ⚠ FR-003: "System charges fee on yield accrued since last fee collection"
   Rule: 1 (WHAT not HOW)
   → Rewrite: "System charges fee only on net positive gains experienced by depositors"

Severity: ✗ ERROR / ⚠ WARNING / ℹ INFO

Summary: Quality: X/Y pass | Issues: N errors, M warnings, K info
```
