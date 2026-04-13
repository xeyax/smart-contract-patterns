# Generate gaps.md

You are a subagent that collects `[GAP]` and `[CHOICE]` markers from every prior artifact and from specs, and writes a single consolidated gaps file. Fresh context.

## Read

- Tree: `{{DATA_FILE}}` — needed to pick the nearest `AD-NNN` parent for each gap
- Details: `{{DETAILS_DIR}}/AD-*.md` — needed to phrase a useful `?` question when the inline marker is terse
- All prior artifacts via named placeholders — whichever the profile generated. Use only named placeholders (e.g. `{{OVERVIEW_OUTPUT}}`, `{{COMPONENTS_OUTPUT}}`, `{{INTERFACES_OUTPUT}}`, `{{CALL_DIAGRAMS_OUTPUT}}`, `{{DATA_FLOWS_OUTPUT}}`, `{{ACCESS_CONTROL_OUTPUT}}`, `{{STATE_MACHINES_OUTPUT}}`, `{{INVARIANTS_OUTPUT}}`, `{{RISKS_OUTPUT}}`, `{{PLAN_OUTPUT}}`, `{{PUBLIC_API_OUTPUT}}`, `{{ERROR_TAXONOMY_OUTPUT}}`, `{{SPECS_OUTPUT}}`, plus any domain-specific ones the profile declares). If a placeholder is empty, skip the read.
- Formatting rules: `{{PROFILE_DIR}}/formats/gaps.md`

## Write

`{{OUTPUT}}` — a single consolidated `gaps.md` file.

## Task

Walk every prior artifact and every spec file. Extract:
- Every inline `[GAP]: ...` marker.
- Every inline `[CHOICE]: ...` marker.
- Every `[GAP]` entry in a spec's traceability matrix.

Merge into one table:

`# | Type | Artifact | Description | Parent (AD-NNN) | Suggested tree question`

- **Type**: `GAP` (information missing) or `CHOICE` (ambiguity, the generator picked one interpretation).
- **Artifact**: short artifact name the marker came from (e.g. `components`, `interfaces`, `specs/test_session`).
- **Description**: the text after `[GAP]:` / `[CHOICE]:` — verbatim.
- **Parent**: nearest existing `AD-NNN` where the gap belongs. `—` if no natural parent.
- **Suggested tree question**: a `?`-style question that, if answered, would resolve the gap. Derived from the description.

## Rules

- **Do not invent gaps.** Only surface what is already marked in artifacts or specs.
- **Deduplicate** identical markers (same description, same parent) — keep one entry.
- **Preserve ordering** roughly by artifact generation order (overview → components → ... → specs) so reviewers can trace the origin easily.
- If no `[GAP]` / `[CHOICE]` anywhere, still write the file with an empty table and the line `No gaps — all decisions are covered by existing artifacts.` Return `written: {{OUTPUT}} (empty)`.

## Return

`written: {{OUTPUT}}` with count (`M gaps`) or `written: {{OUTPUT}} (empty)`.
