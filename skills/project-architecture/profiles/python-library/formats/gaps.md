# Gaps Formatting Rules

Rules for `gaps.md` artifact.

## Structure

```markdown
# Gaps

| # | Type | Artifact | Description | Parent | Suggested tree question |
|---|------|----------|-------------|--------|-------------------------|
| 1 | GAP | invariants | No thread-safety invariant for `Session.cache` | AD-007 | ? Is `Session.cache` thread-safe, or single-threaded only? |
| 2 | CHOICE | error-taxonomy | `ConfigError` hierarchy split inferred from tree | AD-012 | ? Should `MissingConfigKeyError` subclass `ConfigError` or be flat? |
| 3 | GAP | public-api | Stability of `experimental_streaming` not decided | AD-015 | ? Is `experimental_streaming` stable or experimental for 1.0? |
```

## Rules

- Type: `GAP` (information missing) or `CHOICE` (ambiguity, summarizer picked one interpretation).
- Parent: `AD-NNN` of the nearest existing node where the question belongs. `—` if no natural parent.
- Only created if there are `[GAP]` or `[CHOICE]` entries in other artifacts.
