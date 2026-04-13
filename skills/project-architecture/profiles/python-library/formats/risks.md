# risks.md Formatting Rules (Python library)

Library-specific risk taxonomy. Consolidates R items from requirements + tree + general library-class risks.

## Structure

```markdown
# Risks

## Table

| Risk | Source | Mitigation | Status |
|------|--------|------------|--------|
| Unintended breaking change on stable symbol | requirements R-01 | AD-005: stability contract + DeprecationWarning + type checks in CI | COVERED |
| Pickle deserialization exposes code execution | general (lib class) | AD-012: do not pickle arbitrary objects; use explicit schema | COVERED |
| Subprocess command injection via user input | general | — | UNCOVERED [GAP] |
| Resource leak: unclosed file handle on error path | general | AD-018: context-manager contract on Session | COVERED |
| Thread-unsafe global cache | tree R-02 | accepted — documented as single-threaded only | ACCEPTED |
```

## Library-class risks to always consider

Scan whether the tree addresses each, even if requirements do not mention it:

| # | Risk class | Applies when |
|---|-----------|--------------|
| 1 | Breaking public API | Always |
| 2 | Thread safety | Library has mutable global/singleton state |
| 3 | Async/sync confusion | Mixed mode (skip if pure sync) |
| 4 | Resource leak (files, sockets, subprocesses) | Library opens external resources |
| 5 | Pickle / marshal / eval | Library serializes or deserializes untrusted data |
| 6 | Dependency drift | Library has external pip dependencies |
| 7 | Monkey-patching risk | Library mutates third-party module state |
| 8 | Name shadow / import cycle | Non-trivial package structure |
| 9 | Logging leakage (secrets) | Library logs user-provided data |
| 10 | `eval` / `exec` / dynamic code | Library interprets user code |
| 11 | Signal / atexit handler side-effects | Library registers handlers |
| 12 | Locale / encoding bugs | Library handles text I/O |
| 13 | Subprocess injection | Library spawns processes with user input |
| 14 | `__slots__` / metaclass surprises | Library's public classes |

## Columns

- **Risk** — one-sentence description of the threat.
- **Source** — `requirements R-NN` / `tree R-NN` / `general` / `ecosystem`.
- **Mitigation** — AD-NNN that addresses it, or `—`.
- **Status** — one of:
  - `COVERED` — an AD mitigates it.
  - `ACCEPTED` — tree consciously accepts the risk, typically with documentation.
  - `UNCOVERED [GAP]` — neither mitigated nor accepted. Needs a tree decision.

## Rules

- **Every requirements R item appears.** If no mitigation and no acceptance → `UNCOVERED [GAP]`.
- **Do not invent mitigations.** Only reference ADs that exist in the tree.
- **Do not over-catalogue.** Skip library-class risks that clearly do not apply (async risks for a pure-sync lib).
