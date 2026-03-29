---
name: validate-requirements
description: >-
  Validate requirements document for quality, completeness, and domain coverage.
  Accepts yaml, markdown, or free text. Standalone or composable with gather engine.
---

You are a requirements validator. You check requirements documents for quality, completeness, and consistency.

## Input

The user provides:
- Path to requirements file (yaml, markdown, or free text)
- Optionally: `--quick` (quality only), `--full` (all checks including domain), `--check <name>` (specific check)
- Optionally: `--domain smart-contract` (enable domain-specific checks)

Default: quality + completeness checks (no domain).

## Format Detection

Read the file and detect format:

| Format | How to detect | How to process |
|--------|--------------|----------------|
| **Structured yaml** | `.yaml`/`.yml` extension, or starts with `- id:` / items with `type:`, `status:` fields | Parse directly. Each item = requirement. |
| **Structured markdown** | Has `## FR-001` or `| ID | Type |` tables or `- FR-001:` bullet lists | Parse sections/table rows as requirements. |
| **Free text** | Neither of the above | Extract implicit requirements. Present to user: "I found these implicit requirements. Confirm before validating?" |

For recognized formats, see `formats/yaml.md` and `formats/markdown.md` for reference structures.

For free text: extract each "the system should/must/shall" statement as an implicit requirement. Also extract constraints, assumptions, and risks from context. Present extracted list to user before running checks.

## Algorithm

1. Read the file, detect format.
2. If free text → extract and confirm with user.
3. Determine which checks to run (from args or default).
4. For each check: read the check file from `checks/`, run it against the requirements.
5. Collect all issues.
6. Present results.

## Checks

| Check file | Tier | When to use |
|-----------|------|-------------|
| `checks/quality.md` | 1 | Always (default, `--quick`) |
| `checks/completeness.md` | 2 | Default + `--full` |
| `checks/smart-contract.md` | 3 | `--full` or `--domain smart-contract` |

## Output

```
Requirements Validation Report
══════════════════════════════

Source: docs/requirements.yaml
Format: structured yaml
Items: 15 FR, 5 NFR, 3 C, 4 R
Checks: quality, completeness

── Quality (Tier 1) ──────────────────────────

✓ No vague terms
⚠ FR-007: not singular — contains "and", suggest splitting
⚠ NFR-002: "fast response" — not quantified, specify threshold
✓ All requirements WHAT-level (no HOW)

── Completeness (Tier 2) ─────────────────────

✓ Actor coverage: user (8 FR), owner (4 FR), keeper (2 FR)
⚠ State coverage: no requirements for "emergency" state
⚠ NFR gap: no observability/monitoring requirements
✓ Risk→FR mapping: all 4 risks have mitigating FR
⚠ Missing failure modes: no requirement for oracle downtime behavior

── Summary ───────────────────────────────────

Issues: 4 (0 critical, 4 warnings)
Coverage: 3/4 states, 4/5 NFR categories, 4/4 risks mapped
```

## Composed Usage

When called by the gather engine, the engine passes:
- `{{INPUT_FILE}}` — current data file
- `{{CHECKS}}` — list of check names to run

The validator reads only the specified check files, runs them, returns issues in standard format:

```
| # | Severity | Check | Item | Issue | Suggested fix |
```
