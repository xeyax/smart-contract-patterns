# Issues Format

Standard output format for all validators. Used by validate-requirements, validate-architecture, and any future validator.

Two representations of the same data:
- **YAML** — for engine/machine consumption (parseable, actionable)
- **Markdown** — for human consumption (readable report)

## YAML Format (machine)

```yaml
source: "docs/requirements.md"
format_detected: "structured markdown"   # structured yaml | structured markdown | free text
checks_run: [quality, completeness]
item_count:
  FR: 18
  NFR: 7
  C: 7
  R: 10

issues:
  - id: Q3-001
    severity: ERROR              # ERROR | WARNING | INFO
    check: quality.abstraction   # tier.check_name
    item: FR-003                 # affected item ID, or null for set-level issues
    issue: "Contains mechanism name 'high-water mark' — describes HOW, not WHAT"
    suggestion: "Rewrite as: 'Fee charged only on net new gains, not on recovery after losses'"
    fixable: true                # can engine auto-apply the suggestion?

  - id: C1-001
    severity: ERROR
    check: completeness.purpose
    item: null                   # set-level issue, no specific item
    issue: "No item defines what the system fundamentally is"
    suggestion: "Add item: 'System is a meta-vault wrapper that holds base vault shares and issues own shares'"
    fixable: false
    suggested_item:              # pre-filled item for proposer (optional)
      type: FR
      group: Purpose
      text: "System is a meta-vault wrapper that holds base vault shares and issues own shares to users"
      priority: Must

  - id: C5-001
    severity: WARNING
    check: completeness.state_coverage
    item: null
    issue: "No items define behavior in 'emergency' state"
    suggestion: "Add requirements for emergency shutdown behavior"
    fixable: false

  - id: C7-001
    severity: WARNING
    check: completeness.risk_mapping
    item: R-010
    issue: "Risk has no mitigating FR or explicit 'accepted' decision"
    suggestion: "Add mitigation reference or mark as 'accepted' with rationale"
    fixable: false

  - id: Q6-001
    severity: INFO
    check: completeness.grouping
    item: null
    issue: "FR-015, FR-016 (ERC-4626 views) separated from FR-001, FR-002 (core flows)"
    suggestion: "Consider grouping by user flow for reduced cognitive load"
    fixable: false

summary:
  total: 5
  errors: 2
  warnings: 2
  info: 1
  coverage:
    actors: "3/3"
    states: "2/3"
    nfr_categories: "5/6"
    risks_mapped: "9/10"
    items_with_acceptance_criteria: "16/18"
```

### Field Reference

#### Issue fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Stable reference: `{check_short}-{seq}` (e.g. Q3-001, C5-002) |
| `severity` | enum | yes | ERROR (blocks DoD), WARNING (should fix), INFO (consider) |
| `check` | string | yes | Which check found this: `tier.check_name` |
| `item` | string | no | Affected item ID (FR-003, R-010). Null for set-level issues. |
| `issue` | string | yes | Human-readable problem description |
| `suggestion` | string | yes | Concrete fix or action |
| `fixable` | bool | no | Can engine auto-apply? Default false. |
| `suggested_item` | object | no | Pre-filled item for proposer to present to user. Only for "missing item" issues. |

#### Summary fields

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Total issues |
| `errors` | int | Count by severity |
| `warnings` | int | |
| `info` | int | |
| `coverage` | map | Dimension → "covered/total" string. Dimensions vary by validator. |

## Markdown Format (human)

Same data, rendered for readability.

```markdown
# Validation Report

**Source:** docs/requirements.md
**Format:** structured markdown
**Items:** 18 FR, 7 NFR, 7 C, 10 R
**Checks:** quality, completeness

## Errors (2)

### ✗ No top-level purpose requirement
**Check:** completeness.purpose
No item defines what the system fundamentally is.
**Suggestion:** Add: "System is a meta-vault wrapper that holds base vault shares and issues own shares to users"

### ✗ FR-003 describes HOW, not WHAT
**Check:** quality.abstraction | **Item:** FR-003
"Performance fee with high-water mark" — names a specific mechanism.
**Suggestion:** "Fee charged only on net new gains, not on recovery after losses"

## Warnings (2)

### ⚠ Missing state coverage: emergency
**Check:** completeness.state_coverage
No items define behavior in emergency state.
**Suggestion:** Add requirements for emergency shutdown behavior.

### ⚠ R-010 has no mitigating FR
**Check:** completeness.risk_mapping | **Item:** R-010
Fee receiver revert blocks operations — no mitigation specified.
**Suggestion:** Add mitigation reference or explicit "accepted" with rationale.

## Info (1)

### ℹ Grouping could be improved
**Check:** completeness.grouping
FR-015, FR-016 separated from related core flow items.
**Suggestion:** Group by user flow for reduced cognitive load.

## Coverage Summary

| Dimension | Coverage | Details |
|-----------|----------|---------|
| Actors | 3/3 ✓ | user, owner, keeper |
| States | 2/3 ⚠ | normal ✓, paused ✓, emergency ✗ |
| NFR categories | 5/6 ⚠ | observability ✗ |
| Risks mapped | 9/10 ⚠ | R-010 unmapped |
| Acceptance criteria | 16/18 ⚠ | FR-010, FR-017 missing |
```

### Rendering Rules

- Sections grouped by severity: Errors first, then Warnings, then Info
- Each issue: icon (✗/⚠/ℹ) + title, then check reference, description, suggestion
- Item reference shown when issue is about a specific item
- Coverage summary as table at the end
- Severity icons: ✗ = ERROR, ⚠ = WARNING, ℹ = INFO

## Interactive Format (engine → user)

When engine presents issues during gathering (after_batch or before_done):

```
[Validation] 3 issues:

1. ✗ FR-003: "high-water mark" is HOW, not WHAT
   → "Fee charged only on net new gains"
   Fix? [Y/skip/edit]

2. ⚠ Missing: emergency state behavior
   → Add requirements for emergency shutdown
   Add? [Y/skip]

3. ℹ Grouping: FR-015, FR-016 far from core flows
   → Reorder? [Y/skip]
```

Rules:
- Show only new issues (not previously shown)
- ERRORs first, INFOs last
- Each issue actionable: fix/add/skip/edit
- Fixable issues show concrete suggestion inline
- User response → engine applies fix or skips

## Applicability

This format works for any validator:

| Validator | check prefix | coverage dimensions |
|-----------|-------------|-------------------|
| validate-requirements | `quality.*`, `completeness.*`, `smart-contract.*` | actors, states, nfr_categories, risks_mapped |
| validate-architecture | `consistency.*`, `tree-structure.*`, `redundancy.*` | coverage_areas, decisions_with_details, risks_covered |
| validate-specs | `decision-coverage.*`, `traceability.*` | qtree_nodes_covered, artifact_lines_covered |
