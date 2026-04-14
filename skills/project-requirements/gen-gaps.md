# Generate gaps.md

You are a subagent that collects `[GAP]` and `[CHOICE]` markers from every prior artifact and writes a single consolidated gaps file. Fresh context.

## Read

- Requirements: `{{DATA_FILE}}` — needed to pick the nearest item ID as parent
- All prior artifacts via named placeholders — whichever the profile generated. Use only named placeholders (e.g. `{{OVERVIEW_OUTPUT}}`, `{{GLOSSARY_OUTPUT}}`, `{{PARTICIPANT_MATRIX_OUTPUT}}`, `{{STATE_ACTION_MATRIX_OUTPUT}}`, `{{BOUNDARY_MAP_OUTPUT}}`, `{{DEPENDENCY_GRAPH_OUTPUT}}`, `{{NFR_COVERAGE_OUTPUT}}`, `{{THREAT_COVERAGE_OUTPUT}}`, `{{CONSISTENCY_REPORT_OUTPUT}}`, `{{AMBIGUITY_REPORT_OUTPUT}}`, plus any domain-specific ones the profile declares). If a placeholder is empty, skip the read.
- Formatting rules: `{{PROFILE_DIR}}/formats/gaps.md`

## Write

`{{OUTPUT}}` — a single consolidated `gaps.md` file.

## Task

Walk every prior artifact. Extract:
- Every inline `[GAP]: ...` marker.
- Every inline `[CHOICE]: ...` marker.

Merge into one table:

`# | Marker | Artifact | Description | Parent | Item type | Item text | Priority`

- **Marker**: `GAP` (information missing) or `CHOICE` (ambiguity, the generator picked one interpretation).
- **Artifact**: short artifact name the marker came from (e.g. `participant-matrix`, `boundary-map`, `threat-coverage`).
- **Description**: the text after `[GAP]:` / `[CHOICE]:` — verbatim.
- **Parent**: nearest existing item ID from `{{DATA_FILE}}` (FR-NN, NFR-NN, C-NN, R-NN). Pick the item the gap most directly relates to. If no natural parent, use `—`.
- **Item type**: one of `FR`, `NFR`, `C`, `R`, or `?`. Use `?` ONLY when the gap genuinely cannot be typed; otherwise infer from the marker context (boundary/threat → C/R, behavior gap → FR, quantification gap → NFR).
- **Item text**: short proposed item text in WHAT-not-HOW form (will be the suggested item if user accepts the gap).
- **Priority**: `Must` / `Should` / `Could`. Default `Must` for safety-critical (boundary, threat, consistency); `Should` for completeness items.

This table is consumed by `reviewer.md`, which converts each row into a fully-structured proposed item (with acceptance criteria where needed). Do NOT add acceptance criteria here — leave that to the reviewer. Do NOT add mitigation for R items — R items are threat descriptions only.

## Rules

- **Do not invent gaps.** Only surface what is already marked in artifacts.
- **Deduplicate** identical markers (same description, same parent) — keep one entry.
- **Preserve ordering** roughly by artifact generation order so reviewers can trace the origin.
- If no `[GAP]` / `[CHOICE]` anywhere, still write the file with the header and the line "No gaps — all artifacts are clean." (table omitted or kept empty). The file always exists; emptiness is expressed by content, not by the return shape.

## Return

Return exactly this, two lines:

```
written: {{OUTPUT}}
gaps: N
```

Where `N` is the number of rows in the table (0 if file contains the "No gaps" line). Do NOT embed the count inside the `written:` line — the orchestrator parses `written:` strictly against accepted shapes (`written: {{OUTPUT}}` / `written: {{OUTPUT}} (none)` / `fatal: <reason>`).

Use `fatal: <reason>` as a single line only if the subagent cannot run at all.
