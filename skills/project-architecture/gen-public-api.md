# Generate public-api.md

You are a subagent generating the public API catalog. Fresh context.

## Domain

{{DOMAIN}}

This artifact applies to domains where a **library surface** exists (Python lib, npm package, Rust crate, etc.). For smart contracts it is typically skipped — external ABI is covered by `interfaces/`.

## Read

- Tree: `{{DATA_FILE}}`
- Details: `{{DETAILS_DIR}}/AD-*.md`
- Requirements: `{{REQUIREMENTS_FILE}}` (if provided)
- Overview: `{{OVERVIEW_OUTPUT}}` (for consistency)
- Formatting rules: `{{PROFILE_DIR}}/formats/public-api.md`

## Write

`{{OUTPUT}}`

## Task

Enumerate every symbol the library exports, with stability level and since-version.

Per the format rules: group by module; for each symbol provide kind (class / function / constant / type alias / exception), stability (`stable` / `experimental` / `internal`), and since version.

Include a short **Stability contract** paragraph: what the library guarantees across minor versions, deprecation policy.

Include an **Importability rules** section: what is accessible from the package root vs submodule-only.

## Rules

- **Only ✓ decisions from the tree.** If the tree did not decide what to export → `[GAP]`.
- **Do not list private helpers.** Underscore-prefixed symbols and submodules are not public.
- **Do not include function signatures.** Those live in `interfaces/*`.
- `[GAP]` if a symbol's stability level is not decided. `[CHOICE]` if tree lets multiple export sets be valid.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all (missing upstream artifact, unreadable tree).
