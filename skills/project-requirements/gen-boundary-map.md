# Generate boundary-map.md

You are a subagent generating the system boundary map. Fresh context.

## Domain

{{DOMAIN}}

## Read

- Requirements: `{{DATA_FILE}}`
- Overview: `{{OVERVIEW_OUTPUT}}`
- Glossary: `{{GLOSSARY_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/boundary-map.md`

## Write

`{{OUTPUT}}`

## Task

Map every external dependency, **classified by kind** — runtime interaction vs environment/dependency constraint. The two have different completeness rules.

### A. Runtime external interactions

The system actually calls, reads from, or hands data to these at runtime. Per row:

| Dependency | Kind | Declared by C | Used by FRs | Failure mode (R/FR) | Status |
|------------|------|---------------|-------------|----------------------|--------|

Examples (abstract — see profile format for domain-specific ones): external service, sibling component, callback receiver, database, message broker, file system, subprocess.

Required for runtime interactions:
- **Declared by C** — Constraint naming the dependency and its required behavior. Empty → `[GAP]: runtime dependency X has no Constraint`.
- **Used by FRs** — FR-IDs that interact with it. Empty → `[GAP]: dependency declared but no FR uses it (boundary leak — declared but unused)`.
- **Failure mode** — R or FR describing what happens on failure. Empty → `[GAP]: no failure mode for runtime dependency X`.

### B. Environment / build-time / packaging constraints

The system depends on these for building or running but does NOT interact with them at runtime through API calls. Per row:

| Constraint | Kind | Declared by C/NFR | Notes |
|------------|------|--------------------|-------|

Examples (abstract — see profile format for domain-specific ones): supported runtime version, allowed dependencies, supported platforms, target deployment environment, build toolchain version.

Required for environment constraints:
- **Declared by C/NFR** — explicit C or NFR. Empty → `[GAP]: environment dependency mentioned but no C/NFR declares it`.
- Failure mode and FR usage are NOT required — these are static facts about the deployment context, not runtime interactions.

### Sources to scan

1. Dependencies listed in `{{OVERVIEW_OUTPUT}}` — classify each as A or B.
2. References in Purpose to other systems.
3. Constraints (C) items.
4. FRs that mention "calls X", "reads from Y", "depends on Z" → kind A.
5. Constraints about versions, packages, OS, chain, toolchain → kind B.

## Rules

- One row per distinct dependency, in the appropriate section (A or B).
- Kind A (runtime): all three columns (C, FR usage, failure mode) required.
- Kind B (environment): only declaration required.
- A dependency that appears in FRs but not in Purpose/C → flag `[GAP]: boundary leak`.
- For every FR that requires behavior FROM an external system (not OF the system under design) → `[GAP]: FR-NN describes external behavior, should be C` in a "Boundary violations" section below the tables.
- If a dependency is ambiguous (could be runtime or environment) → put in section A and add `[CHOICE]: classified as runtime, alternative is environment`.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all.
