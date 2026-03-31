# Issues Format

How validator returns issues and how the orchestrator presents them to the user.

## From Validator (text)

Validator returns a numbered list:

```
Validation issues (N found):

1. ✗ FR-003: "high-water mark" is HOW, not WHAT
   Check: quality.abstraction
   → Rewrite as: "Fee charged only on net new gains"

2. ⚠ Missing: no requirements for emergency state
   Check: completeness.state_coverage
   → Add requirements for emergency shutdown behavior

3. ℹ Grouping: related items far apart
   Check: completeness.grouping
   → Consider reordering

Coverage: actors 3/3, states 2/3, NFR categories 5/6
```

Severity icons: ✗ = ERROR (blocks DoD), ⚠ = WARNING (should fix), ℹ = INFO (consider).

## Orchestrator Presents to User

```
[Validation] 3 issues:

1. ✗ FR-003: "high-water mark" is HOW, not WHAT
   → "Fee charged only on net new gains"
   Fix? [Y/skip/edit]

2. ⚠ Missing: emergency state behavior
   → Add requirements for emergency shutdown
   Add? [Y/skip]

3. ℹ Grouping: related items far apart
   → Reorder? [Y/skip]
```

Each issue is actionable:
- ERROR/WARNING with fix → "Fix? [Y/skip/edit]"
- Missing item suggestion → "Add? [Y/skip]"
- INFO → "Apply? [Y/skip]"

User response → orchestrator writes changes to data file.
