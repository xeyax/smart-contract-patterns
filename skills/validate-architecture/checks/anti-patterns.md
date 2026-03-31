# Anti-Pattern Check (Tier 3)

Detect known bad architectural patterns.

```
You are an architecture anti-pattern detector.

Read the architecture tree from: {{INPUT_FILE}}
Read detail files from the details/ directory.
Fetch the anti-patterns catalog from: {{ANTIPATTERNS_URL}}

If the URL is not available, use your knowledge of common smart contract anti-patterns.

For each anti-pattern in the catalog:
1. Is this pattern present in the architecture? Check decisions, component structure, and detail files.
2. If found → flag with description of where it appears and how to fix.
3. If not found but the architecture is at risk (e.g., no explicit protection against it) → flag as INFO.

## Output

```
1. ⚠ Unrestricted Admin: AD-012 allows owner to change fee rate with no timelock or bounds
   → Add timelock requirement or hard-coded bounds. See ANTIPATTERNS.md: Access Control > Unrestricted Admin.

2. ⚠ Oracle Monoculture: AD-007 specifies single Chainlink feed, no fallback
   → Add fallback mechanism or circuit breaker.

3. ℹ Donation Attack Surface: no explicit protection found. AD-002 (share pricing) may be vulnerable.
   → Consider virtual shares offset or minimum first deposit.
```

Severity:
- ✗ ERROR: anti-pattern clearly present and dangerous
- ⚠ WARNING: anti-pattern present or architecture at risk
- ℹ INFO: no explicit protection, worth reviewing
```
