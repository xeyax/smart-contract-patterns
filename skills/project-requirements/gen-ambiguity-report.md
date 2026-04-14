# Generate ambiguity-report.md

You are a subagent scanning for vague or underspecified items. Fresh context.

## Domain

{{DOMAIN}}

## Read

- Requirements: `{{DATA_FILE}}`
- Glossary: `{{GLOSSARY_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/ambiguity-report.md`

## Write

`{{OUTPUT}}`

## Task

Three sections, each finding documented inline:

### 1. Vague wording

Forbidden words and phrases that signal underspecification: `flexible`, `easy`, `adequate`, `sufficient`, `fast`, `reliable`, `scalable`, `intuitive`, `user-friendly`, `safe`, `robust`, `efficient`, `seamless`, `appropriate`, `reasonable`, `minimal`, `optimal`, `modern`, `simple`, `clean`, `when appropriate`, `if needed`, `under normal conditions`.

For each occurrence:
```
- FR-NN: "<quoted text fragment with the vague word>"
  Suggestion: replace with quantified condition (specific number, observable trigger).
  [GAP]: vague wording in FR-NN
```

### 2. Insufficient acceptance criteria

For each FR with `< 2` acceptance criteria where the FR clearly has edge cases (mentions zero, max, first-time, paused, error path):
```
- FR-NN: "<short item title>"
  Has <N> AC; missing: <which edge case is uncovered>.
  [GAP]: FR-NN has insufficient acceptance criteria for edge cases
```

For invariant-style items (one criterion fully covers it) — do NOT flag.

### 3. Unquantified NFRs / constraints

For each NFR or C item that uses adjectives without numbers (e.g. "high availability", "low latency", "minimal gas") with no quantification:
```
- NFR-NN: "<quoted text>"
  Suggestion: add specific number (uptime %, ms, gas units, MB).
  [GAP]: NFR-NN uses unquantified term
```

## Rules

- Pull the forbidden word list from the format file (it's the canonical source; profile may extend).
- Do not suggest specific numbers — let the user decide.
- One section can be empty if no findings — still emit the section header + "No findings."
- An item can appear in multiple sections (vague + unquantified).

## Return

`written: {{OUTPUT}}` (inline `[GAP]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all.
