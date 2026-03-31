# Quality Check (Tier 1)

Individual requirement quality. Fast, runs on each requirement independently.

```
You are a requirements quality checker.

Read the requirements from: {{INPUT_FILE}}
Read the quality rules from: rules/quality-rules.md

For EACH requirement, run ALL 11 rules from quality-rules.md.

## Output

For each issue, **include the full requirement text** so the issue is understandable without looking up the original:

```
1. ⚠ FR-003: "System charges fee on yield accrued since last fee collection"
   Check: quality.abstraction
   → "yield accrued since last fee collection" describes a specific mechanism
   → Rewrite: "System charges fee only on net positive gains experienced by depositors"

2. ⚠ FR-004: "Only the designated fee recipient receives fees and the recipient can be changed by owner"
   Check: quality.singularity
   → Combines two capabilities. Split into separate items.
```

When suggesting a fix, provide a **complete rewrite** of the full item text — not a word patch. Verify your own suggestion passes ALL rules before proposing it.

Severity: ✗ ERROR (must fix) / ⚠ WARNING (should fix) / ℹ INFO (consider).

After all issues, summary:
```
Quality: X/Y requirements pass all checks
Issues: N errors, M warnings, K info
```
```
