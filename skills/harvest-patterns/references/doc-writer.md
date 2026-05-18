# Doc Writer Guide

Use this guide when turning accepted harvested candidates into catalog edits.

## New Pattern Docs

Create `patterns/<category>/pattern-<slug>.md` with the existing style:

1. H1 name.
2. Blockquote one-line description.
3. `## Metadata`.
4. `## Use When`.
5. `## Avoid When`.
6. `## Trade-offs`.
7. `## How It Works`.
8. `## Implementation`.
9. `## Source Evidence` for harvested docs unless evidence is already represented by public Real-World Examples.
10. `## Real-World Examples`.
11. `## Related Patterns`.
12. `## References`.

Implementation snippets must be minimal and generalized. Replace project-specific
contract names, token names, and addresses with descriptive names.

## New Risk Docs

Create `patterns/<category>/risk-<slug>.md` with:

1. H1 name.
2. Blockquote one-line risk description.
3. `## Metadata`.
4. `## Problem Description`.
5. `## Applies When` or `## Conditions That Increase Risk`.
6. `## Requirements Violated` or `## Requirements Affected`.
7. `## Attack Vectors` or `## Failure Modes`.
8. `## Mitigations`.
9. `## Source Evidence`.
10. `## Related Patterns`.
11. `## References`.

Prefer `## Applies When` for new risk docs because the index generator can extract it.

## New Requirement Docs

Create `patterns/<category>/req-<slug>.md` only for reusable guarantees that several
patterns can satisfy or violate. Use numbered `## R1: Name` sections so the index
generator can extract them.

## Updating Existing Docs

- Add the smallest section-level change that captures the new evidence.
- Add "Variation", "Edge Case", "Common Pitfall", or "Source Evidence" sections only when they materially improve future reuse.
- Update Related Patterns both ways when a new cross-link changes navigation.
- Keep claims scoped: "reduces", "bounds", "detects", or "eliminates" must be technically accurate.

## Final Verification

Run:

```bash
python3 scripts/generate-pattern-index.py
```

Then check:

- `git diff -- patterns/INDEX.md` is expected and sourced from doc metadata.
- New docs appear in `patterns/INDEX.md`.
- Relative markdown links resolve.
- No unsupported placeholder text remains in new docs.
