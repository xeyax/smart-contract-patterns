# specs/*.py Formatting Rules (pytest)

One abstract test class per component under `artifacts/specs/`. The developer subclasses and supplies concrete fixtures; the base class asserts the contract.

## File naming

`test_<component>.py` — e.g. `test_session.py`, `test_parser.py`.

## Per-file structure

```python
"""Specification tests for <Component>.

These tests encode the architectural contract. Subclass and implement
the abstract fixtures to run them against a concrete implementation.

Traceability: map every checkable claim to a test or mark [GAP].
"""

import pytest
from abc import abstractmethod
from mypkg.interfaces.session import Session  # interface, not impl


# ============================================================
# Traceability matrix
# ============================================================
# Claim (source) → Test
# INV-1 (invariants.md: Session.closed=True → all methods raise) → test_closed_session_raises
# POST-deposit (call-diagrams.md: after parse, result.tokens > 0)  → test_parse_returns_tokens
# AC-1 (access-control.md): public methods on closed session raise  → test_closed_session_raises
# AD-005 (tree): deterministic output for same input               → test_deterministic
# [GAP]: AD-012 equivalence between parse and parse_stream — no decision in tree


class BaseSessionSpec:
    """Contract tests for any implementation of `Session`.

    Concrete subclass must provide `make_session()` and any required inputs.
    """

    # ---- Abstract fixtures ----

    @pytest.fixture
    @abstractmethod
    def make_session(self):
        """Factory that returns a fresh Session instance."""

    @pytest.fixture
    def session(self, make_session):
        s = make_session()
        yield s
        s.close()

    # ---- Section 1: Invariants ----

    def test_closed_session_rejects_parse(self, make_session):
        s = make_session()
        s.close()
        with pytest.raises(SessionClosedError):
            s.parse("x")

    # ---- Section 2: Guards / access / validation ----

    def test_parse_rejects_none(self, session):
        with pytest.raises(TypeError):
            session.parse(None)

    # ---- Section 3: Postconditions ----

    def test_parse_produces_nonempty_result(self, session, valid_input):
        result = session.parse(valid_input)
        assert result.tokens  # POST from call-diagrams

    # ---- Section 4: State machine / lifecycle ----

    def test_close_is_idempotent(self, make_session):
        s = make_session()
        s.close()
        s.close()  # must not raise

    # ---- Section 5: Behavioral properties ----

    def test_deterministic(self, make_session, valid_input):
        a = make_session().parse(valid_input)
        b = make_session().parse(valid_input)
        assert a == b
```

## Five sections

1. **Invariants** — from `invariants.md`. One test per invariant (e.g. closed-session rejects operations, immutable fields do not change).
2. **Guards / access / validation** — from `error-taxonomy.md` and interface docstrings. Every raise point → `pytest.raises(X)` test.
3. **Postconditions** — from `call-diagrams.md`. Every `POST:` → assertion with exact expected value.
4. **State machine / lifecycle** — from `state-machines.md` if present. Valid transitions → tests; invalid → `pytest.raises`.
5. **Behavioral properties** — system-wide correctness: idempotency, determinism, round-trip, entry-point equivalence, conservation.

## Rules

- **Inherit from a base class** named `Base<Component>Spec`. Developer subclasses with concrete fixtures.
- **`@pytest.fixture @abstractmethod`** for any dependency that varies between implementations (factory for the component, config loaders, mock resources).
- **Import interfaces, not implementations** — `from mypkg.interfaces.X import ...`, never `from mypkg.impl.X import ...`.
- **Traceability matrix at the top** — comment block mapping every tracked claim to a test function or `[GAP]`.
- **No test body depends on implementation details** — only on the interface contract.
- **Parametrize** where the same test covers multiple inputs (`@pytest.mark.parametrize`).
- **No shared mutable state** between tests — each gets a fresh component.

## Completeness checklist (run against tree)

Walk every `✓` AD node with a Details section:

1. **Formula check** — exact value in Details → `assert result == expected_value` (not `>`/`<`).
2. **Guard check** — every raise point → `pytest.raises(X)`.
3. **Recovery check** — every ✓ AD about behavior after adverse condition → end-to-end scenario test.
4. **Equivalence check** — multiple entry points doing the same thing → assert outputs equal + rich path does not trigger simple path's side-effects unintentionally.
5. **Determinism check** — if tree says "deterministic", a test that runs twice and compares outputs.

For each miss → add a test or record `[GAP]` in the traceability matrix.
