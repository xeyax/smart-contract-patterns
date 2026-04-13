# Generate risks.md

You are a subagent generating the risks artifact. Fresh context.

## Read

- Tree: `{{DATA_FILE}}`
- Details: `{{DETAILS_DIR}}/AD-*.md`
- Requirements: `{{REQUIREMENTS_FILE}}` (for R items)
- Anti-patterns URL (if provided): `{{ANTIPATTERNS_URL}}` — fetch `INDEX.md` from there and scan for risk-* entries whose trigger matches this project
- Formatting rules: `{{PROFILE_DIR}}/formats/risks.md`

## Write

`{{OUTPUT}}`

## Task

Consolidate risks from three sources into one table:

1. **Requirements R items** — each R from requirements must be represented. Status: MITIGATED by <AD-NNN> or ACCEPTED (with reference to the AD that accepts it).
2. **Tree R nodes** — architecture-level risks already in the tree.
3. **Pattern library risks** (if anti-patterns URL provided) — entries whose trigger matches this project class.
4. **General risk classes** for the project type (reentrancy, front-running, oracle manipulation, MEV, etc.) even if not in tree — mark COVERED if the tree mitigates them, UNCOVERED otherwise.

Table: `Risk | Source | Mitigation from tree | Status (COVERED / UNCOVERED)`.

## Rules

- Every requirements R MUST appear. If tree has no mitigation and no acceptance → Status = `UNCOVERED [GAP]`.
- Do not invent mitigations. Only reference ADs that actually exist in the tree.
- Status is a fact: either tree has a mitigation AD, accepts it, or neither.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all (missing upstream artifact, unreadable tree).
