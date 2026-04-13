# Risks Formatting Rules

Rules for `risks.md` artifact.

## Structure

```markdown
# Risk Mitigation Map

| Risk | Source | Mitigation from q-tree | Status |
|------|--------|----------------------|--------|
| Oracle staleness | pattern library: risk-oracle-staleness | ✓ Staleness check with heartbeat (d:oracle-fallback) | COVERED |
| Reentrancy | general: token callbacks | ✓ ReentrancyGuard + CEI pattern (d:reentrancy) | COVERED |
| First depositor attack | general: vault share inflation | [GAP] | UNCOVERED |
```

## Rules

- Source = `pattern library: filename` or `general: brief reason`.
- Mitigation = reference to specific ✓ node in q-tree with `d:tag`.
- Status: `COVERED` or `UNCOVERED` (with `[GAP]`).
- Don't list risks that clearly don't apply to this project.
