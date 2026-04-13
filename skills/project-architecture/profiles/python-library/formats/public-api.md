# public-api.md Formatting Rules

The boundary between the library and its users. Every symbol listed here is part of the public contract — changes to these are breaking changes.

## Structure

```markdown
# Public API

## Stability levels

- **Stable** — breaking change requires a major version bump. Users can rely on it.
- **Experimental** — may change in minor versions. Users opt in knowingly.
- **Internal** — not part of the API, even if technically importable. Starts with `_`.

## Exports

### `mypkg` (top-level)

| Symbol | Kind | Stability | Since | Notes |
|--------|------|-----------|-------|-------|
| `Session` | class | stable | 0.1 | Entry point |
| `load_config` | function | stable | 0.1 | |
| `DEFAULT_TIMEOUT` | constant | stable | 0.1 | seconds |
| `experimental_feature` | function | experimental | 0.3 | subject to change |

### `mypkg.submod`

| Symbol | Kind | Stability | Since | Notes |
|--------|------|-----------|-------|-------|

## Stability contract

One paragraph stating what is guaranteed across minor versions (e.g. "stable symbols preserve signature and semantics; deprecations get one minor-version grace period with DeprecationWarning").

## Importability rules

- Stable symbols are importable from the package root (`from mypkg import X`).
- Submodule-only symbols noted explicitly.
- Internal symbols live under `mypkg._internal` or modules starting with `_`.
```

## Rules

- **One row per symbol.** Classes, functions, constants, type aliases.
- **Stability is explicit.** Do not leave it to readers to guess.
- **No private helpers.** Only surfaces intentionally public.
- `[GAP]` if the tree does not decide the stability of a symbol.
- `[CHOICE]` if tree leaves multiple plausible export lists and you picked one.
- Do not include function signatures here — they live in `interfaces/*.py`. `public-api.md` is the catalog; `interfaces/` is the surface.
