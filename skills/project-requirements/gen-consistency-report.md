# Generate consistency-report.md

You are a subagent scanning for contradictions across requirements items. Fresh context.

## Domain

{{DOMAIN}}

## Read

- Requirements: `{{DATA_FILE}}`
- Glossary: `{{GLOSSARY_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/consistency-report.md`

## Write

`{{OUTPUT}}`

## Task

Scan all items for these five contradiction types:

1. **Behavioral** — two items describe the same operation differently.
   Example: "deposits available anytime" (FR-001) vs "deposits blocked when paused" (FR-008).
2. **Scope** — one item says X is in scope, another excludes it.
   Example: "supports multi-token" vs "single token per vault".
3. **Constraint vs FR** — a Constraint forbids what an FR requires.
   Example: C: "no ERC-4626 dependency" vs FR: "ERC-4626 compliant interface".
4. **AC vs own text** — acceptance criteria contradicts the requirement they belong to.
   Example: FR text "users can deposit anytime" with AC "deposit when paused → reverts".
5. **Priority conflict** — two `Must` items that cannot both be satisfied simultaneously.

For each finding:

```
## Contradiction <N>: <type>

- **Item A**: FR-NN — "<quoted text or AC>"
- **Item B**: FR-MM — "<quoted text or AC>"
- **Conflict**: <one-sentence explanation>
- **Suggested resolution**: <one-line hint — qualify text, split scope, drop one, etc.>

[GAP]: contradiction between FR-NN and FR-MM (<type>)
```

If no contradictions found, write a one-line file: "No contradictions found across requirements." Return `written: {{OUTPUT}}` normally — file always written, content may be just the summary.

## Rules

- Quote the conflicting text verbatim from both items.
- Do NOT propose a chosen resolution — only suggest. Resolution is a tree decision (gather PROPOSE will surface it).
- If a contradiction also matches a different completeness rule (e.g. internal completeness), prefer the contradiction framing here.
- Empty file is OK — but always write a header + summary line.

## Return

`written: {{OUTPUT}}` (inline `[GAP]` markers, one per contradiction, go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all.
