# Generate error-taxonomy.md

You are a subagent generating the error/exception taxonomy. Fresh context.

## Domain

{{DOMAIN}}

This artifact applies to domains with a typed exception model (Python, TypeScript, Rust, etc.). For Solidity it is typically replaced by custom errors documented in `interfaces/`.

## Read

- Tree: `{{DATA_FILE}}`
- Details: `{{DETAILS_DIR}}/AD-*.md`
- Requirements: `{{REQUIREMENTS_FILE}}` (if provided)
- Interfaces: `{{INTERFACES_OUTPUT}}` (read to find raise sites documented in signatures)
- Formatting rules: `{{PROFILE_DIR}}/formats/error-taxonomy.md`

## Write

`{{OUTPUT}}`

## Task

Enumerate the exception hierarchy:

1. **Root exception** name and inheritance.
2. **Hierarchy tree** (mermaid or ASCII).
3. **Table** mapping each exception to: where it is raised, when, what the user should do.
4. **Rules for raising** (no bare `Exception`, always typed, `raise ... from e`, etc. — lift from format rules).
5. **Stability** of exception types — which are part of the stable API (users can `except` on them) vs experimental.

## Completeness checks

- **Every raise point in the library** (from interfaces, call-diagrams, requirements R items describing failure modes) → has a typed exception in the hierarchy.
- **Every exception** in the hierarchy → has at least one raise point. Unused → `[GAP]`.
- **External exceptions** (stdlib, dependencies) raised by the library must be wrapped with a typed library exception or explicitly documented as passing through.

## Rules

- **Only ✓ decisions from the tree.** If tree does not decide how a failure surfaces → `[GAP]`.
- **Do not invent exception classes** not implied by the tree or requirements.
- `[GAP]` if a failure mode has no exception. `[CHOICE]` if the tree suggests multiple valid hierarchies and you picked one.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all (missing upstream artifact, unreadable tree).
