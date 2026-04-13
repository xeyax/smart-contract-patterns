# interfaces/*.py Formatting Rules (Python library)

Python interfaces are defined as `typing.Protocol` classes (preferred for duck-typed extensibility) or `abc.ABC` (when subclass identity matters). One file per component that exposes an interface.

## File naming

- `<component_name>.py` — one file per exporting component (e.g. `session.py`, `parser.py`, `cache.py`).
- Internal contract between modules → also a `.py` file, but noted as internal in a module docstring.
- Callback/hook interfaces (for plugins, user-provided handlers) → same `.py` file as the code that invokes them, or a dedicated `hooks.py`.

## Per-file structure

```python
"""Interface: <Component name>.

Stability: <stable | experimental | internal>
"""

from typing import Protocol, Sequence

# ---- User-facing entry points ----

class Session(Protocol):
    """One library run.

    Created via `mypkg.Session(config)`; holds state for the duration.
    """

    def parse(self, source: str) -> "ParseResult":
        """Parse source text into an internal representation.

        Raises ParseError on malformed input.
        """
        ...

    def close(self) -> None:
        """Release any acquired resources. Idempotent."""
        ...


# ---- Plugin / callback interfaces ----

class Emitter(Protocol):
    """User-provided renderer for a parse result."""

    def emit(self, result: "ParseResult") -> str: ...


# ---- Internal contract (between modules) ----

class _Cache(Protocol):
    """Cache used internally by Session. Not part of public API."""
    def get(self, key: str) -> object | None: ...
    def put(self, key: str, value: object) -> None: ...
```

## Grouping

Within one file, group symbols by audience with a comment header:
- `# ---- User-facing entry points ----` (exported at package root)
- `# ---- Plugin / callback interfaces ----` (implemented by user code, called by library)
- `# ---- Internal contract ----` (between library modules; underscore-prefixed)

## Rules

- **Protocol is the default.** Use `abc.ABC` only when you need `isinstance` checks or enforced inheritance.
- **Signatures only** — function bodies must be `...` or `raise NotImplementedError`.
- **Type annotations everywhere** — this is the one artifact where concrete types matter. Use `TYPE_CHECKING` guards for forward refs to avoid runtime imports if needed.
- **One-line docstrings** above each method describing its purpose.
- **Raises:** document exceptions as part of the docstring. Exception types must exist in `error-taxonomy.md`.
- **No default implementations.** These are contracts, not base classes.
- `[GAP]` as a `# [GAP]: ...` comment above the method, or in the module docstring for whole-interface gaps.

## Imports

Minimal: `typing` / `collections.abc`. No imports of concrete implementations or external packages that are not part of the type signature.
