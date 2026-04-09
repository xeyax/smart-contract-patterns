# Completeness Check (Tier 2)

Set-level completeness. Runs before done.

```
Read the requirements from: {{INPUT_FILE}}
Read and apply ALL 12 criteria from: rules/completeness-criteria.md

For each issue, include full requirement text or describe the gap:

1. ✗ No Purpose section found
   → Add ## Purpose with one-paragraph system description

2. ⚠ State coverage: no items define behavior in "emergency" state
   → Add requirements for emergency state behavior

Severity: ✗ ERROR / ⚠ WARNING / ℹ INFO
(see Severity Guide in completeness-criteria.md)

Coverage summary:
Participants: X/Y covered
States: X/Y covered
NFR categories: X/Y covered
Risks: X/Y mitigated or accepted
Failure modes: X/Y covered
```
