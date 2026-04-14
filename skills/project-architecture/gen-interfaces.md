# Generate interfaces/*

You are a subagent generating architecture interface files. Fresh context.

## Domain

{{DOMAIN}}

Use the language, interface style, and file extension specified in the domain block above (e.g. Solidity `.sol` `interface` / Python `.py` with `Protocol` or `ABC` / TypeScript `.ts` `interface`).

## Read

- Tree: `{{DATA_FILE}}`
- Details: `{{DETAILS_DIR}}/AD-*.md`
- Components: `{{COMPONENTS_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/interfaces.md`

## Write

`{{OUTPUT}}` — a glob pattern. Write one file per component into the directory portion of the pattern; filenames follow the formatting rules for this language. The concrete path comes from the profile's `writes:` field via the orchestrator — do not assume a specific directory prefix.

**Zero-item case:** if no component exposes an interface worth generating, write a sentinel file `<glob-dir>/.none` in the directory portion of `{{OUTPUT}}`, containing a one-line explanation, and return `written: {{OUTPUT}} (none)`.

## Task

Generate interfaces. These are the **bridge from architecture to implementation** — specs import them as the single source of truth for signatures.

For each component from components.md:
- Group functions by audience as the format rules specify (e.g. user-facing, admin, internal between components, views/getters).
- One-line docstring/comment above each function describing its purpose.
- Signatures only — no bodies.
- Parameters and return types use **concrete language types**. This is the one artifact where implementation types are appropriate.

## Critical checks (must pass)

1. **Parameter sufficiency.** For every function: "Can the component execute ALL described behavior using ONLY these parameters + its own state?" If not → `[GAP]`.
2. **Return value sufficiency.** If a later step in call-diagrams will consume a result, the function MUST return it. Void/None where a return is needed → `[GAP]`.
3. **Responsibility check.** A parameter belongs to the component that performs the action. If a param forces the caller to know internals of another component → `[GAP]`.
4. **Necessity filter for views/getters.** Only include query functions that are used by other components, needed for spec verification, or required by a standard.
5. **Callback patterns.** Hooks, plugins, flash-loan receivers, event handlers → generate interfaces for the callback side too.

## Rules

- Signatures only. Minimal surface.
- No deployment/setup boilerplate unless format rules say otherwise.
- `[GAP]` as a language-appropriate comment above the function, or at file header if the whole interface cannot be derived.

## Return

`written: {{OUTPUT}}` (list of written files; inline `[GAP]` markers go inside interface files as language-appropriate comments). Use `fatal: <reason>` only if the subagent cannot run at all.
