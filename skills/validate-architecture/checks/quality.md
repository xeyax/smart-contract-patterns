# Decision Quality Check (Tier 1)

Individual decision quality. Runs on each decision independently.

```
You are an architecture decision quality checker.

Read the architecture tree from: {{INPUT_FILE}}
Read the decision quality rules from: rules/decision-quality.md
Read detail files from the details/ directory referenced in the tree.

For EACH decision node (AD-NNN), read its detail file and check ALL 10 rules from decision-quality.md.

## Output

Include the decision text so the issue is understandable without context:

```
1. ⚠ AD-003: "Fee only on net positive gains"
   Check: quality.alternatives
   → Only 1 alternative listed. Add ≥2 alternatives with rejection reasons.

2. ⚠ AD-007: "Use Chainlink oracle"
   Check: quality.consequences
   → No negative consequences listed. What if Chainlink feed is stale? What's the cost?
```

When suggesting a fix, provide a **complete suggestion** for the missing section.

Severity: ✗ ERROR / ⚠ WARNING / ℹ INFO.

Summary:
```
Quality: X/Y decisions pass all checks
Issues: N errors, M warnings, K info
```
```
