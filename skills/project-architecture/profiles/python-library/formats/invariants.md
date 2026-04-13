# Invariants Formatting Rules (Python library)

Rules for `invariants.md` artifact.

## Format

```markdown
## Session

- I1: **Closed-session rejects operations** -- after `close()`, any method on the session raises `SessionClosedError`.
- I2: **Config immutability** -- `session.config` does not change for the lifetime of the session.

## Parser

- I3: **Deterministic output** -- `parse(x) == parse(x)` for the same input across runs.
- I4: **No side-effects** -- `parse` does not touch the filesystem or network.
```

## Numbering

Sequential across all components in the file (not per-component). If `Session` has I1–I5, `Parser` starts at I6.

## Content

- Each invariant = one line, plain English.
- Group by component with `##` headers.
- Only list invariants the library must actively enforce.
- **Exclude platform guarantees**: Python's GIL-level atomicity of simple ops, integer arithmetic correctness, `__del__` finalization timing — these are language-level, not library-level.
- **Exclude preconditions** — invariants are post-any-call truths, not input validations (those live in `error-taxonomy.md`).
- Thread-safety statements belong here if the library claims them: "I{N}: `Cache.get` is safe to call concurrently from multiple threads."
- `[GAP]` at the end of a line if the invariant is implied but not explicitly decided; `[CHOICE]` if you picked one interpretation among several valid ones.
