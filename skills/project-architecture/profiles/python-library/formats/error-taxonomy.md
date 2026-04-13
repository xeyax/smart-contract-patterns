# error-taxonomy.md Formatting Rules

Exception hierarchy for the library. What can be raised, when, and what the user should catch.

## Structure

```markdown
# Error Taxonomy

## Root exception

All library exceptions inherit from `MyPkgError`. Users can `except MyPkgError:` to catch anything from the library.

```python
class MyPkgError(Exception):
    """Base for all mypkg errors."""
```

## Hierarchy

```
MyPkgError
├── ConfigError                # invalid configuration
│   ├── MissingConfigKeyError
│   └── InvalidConfigValueError
├── ParseError                 # malformed input
│   └── UnsupportedSyntaxError
├── ResourceError              # filesystem, network, subprocess failures
│   ├── ResourceNotFoundError  → IOError
│   └── ResourceTimeoutError   → TimeoutError
└── UsageError                 # caller misused the API
    └── SessionClosedError
```

## Table

| Exception | Raised by | Raised when | User should do |
|-----------|-----------|-------------|----------------|
| `ConfigError` | `load_config()` | Config file is malformed | Fix config, retry |
| `ParseError` | `Session.parse()` | Input is not valid syntax | Inspect `.position` attr, surface to user |
| `ResourceTimeoutError` | `Session.load()` | Resource fetch > timeout | Retry or fail fast |
| `SessionClosedError` | any method on closed `Session` | Caller used closed session | Programming error — do not catch |

## Rules for raising

- **No bare `Exception`.** Always raise a typed subclass of `MyPkgError`.
- **No catching `Exception` inside the library** except at clearly-marked boundary points, and then re-raise as a typed library exception with `raise ... from e`.
- **Preserve cause chain.** Always `raise X from e` when wrapping an external exception.
- **Do not raise `BaseException` subclasses** (`KeyboardInterrupt`, `SystemExit`) — let them propagate.

## Stability

| Exception | Stability |
|-----------|-----------|
| Root + main categories (`ConfigError`, `ParseError`) | stable — used in `except` clauses |
| Leaf subclasses | experimental — may be refined |
```

## Rules

- **Every raise point in the library maps to a typed exception.** `[GAP]` if tree mentions a failure mode with no exception defined.
- **Every typed exception maps to at least one raise point.** Unused exceptions are a gap.
- **External exceptions** (`FileNotFoundError`, `requests.HTTPError`) must be wrapped into a library exception at the boundary — never let them leak.
- **Inherit from stdlib exceptions where meaningful** (e.g. `ResourceNotFoundError(MyPkgError, FileNotFoundError)`) so users have two valid `except` paths.
- `[GAP]` if tree does not decide how a failure mode surfaces.
