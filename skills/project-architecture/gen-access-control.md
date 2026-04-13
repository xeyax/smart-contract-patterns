# Generate access-control.md

You are a subagent generating the access-control artifact. Fresh context.

## Read

- Tree: `{{DATA_FILE}}`
- Details: `{{DETAILS_DIR}}/AD-*.md`
- Contracts: `{{COMPONENTS_OUTPUT}}`
- Interfaces: `{{INTERFACES_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/access-control.md`

## Write

`{{OUTPUT}}`

## Task

Table: `Function | Contract | Who can call | Guard`.

- One row per external/public function in interfaces/*.
- "Who can call" = role name as defined in the tree (owner, keeper, permissionless, ERC-4626 standard caller, etc.).
- "Guard" = any additional constraint beyond caller identity (nonReentrant, paused check, bounds, input validation).

## Rules

- If tree confirms the function exists but does not say who calls it → `[GAP]: caller not decided for <fn>`.
- If tree mentions a role but no function is restricted to it → note as informational at end of file.
- Do not invent roles. Use only role names from the tree.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all (missing upstream artifact, unreadable tree).
