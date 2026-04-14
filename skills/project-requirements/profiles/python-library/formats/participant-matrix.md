# participant-matrix.md formatting rules — Python library

## Participant categories (rows)

For a library:
- **User code** — application code that imports and calls the library.
- **Library extension authors** — authors of user-provided extensions that the library invokes (the extension contract is named in requirements; the specific mechanism — Protocol, ABC, callback signature, plugin entry point — is an architecture decision).
- **External resources** — filesystem, subprocesses, network, environment, system signals.

(For libraries with optional CLI: add **CLI users** as a fourth category.)

## Structure

```markdown
# Participant × Action Matrix (Python library)

| Participant \ Action | Open session | Process input | Provide extension behavior | Load configuration |
|----------------------|--------------|---------------|----------------------------|--------------------|
| User code            | FR-001       | FR-002        | —                          | FR-008             |
| Extension authors    | —            | —             | FR-006 (extension capability) | —              |
| External resources   | —            | —             | —                          | FR-008 (config from file) |

## Coverage notes

- User code: open session + process input + load config covered.
- Extension authors: extension capability covered via FR-006.
- External resources: config file reads covered.
  [GAP]: subprocess / network use mentioned in Purpose but no FR specifies behavior

```

## Rules

- "User code" = anyone importing the library; do not split by use case.
- "Extension authors" appear when the library has any documented extension point that user-provided code can implement (the mechanism is decided by architecture).
- "External resources" = anything outside Python-process boundary; FRs that touch them go in this row.
