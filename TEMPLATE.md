# Pattern Name

> One-line description of what this pattern does.

<!--
Section requirements (enforced by scripts/validate-patterns.py):

  REQUIRED for pattern-* files:
    Metadata, Use When, Avoid When, How It Works, Related Patterns,
    and at least one evidence section (Source Evidence / Real-World
    Examples / References).

  RECOMMENDED:
    Trade-offs (agents select patterns by comparing costs — add it
    whenever the pattern has real alternatives), Key Points.

  OPTIONAL:
    Implementation (add when abstracted code clarifies the mechanism),
    References.

  risk-* and req-* files: Metadata + one evidence section required;
  see existing files in the same category for section conventions.
-->

## Metadata

| Property | Value |
|----------|-------|
| Category | category-name |
| Platform | evm |
| Tags | tag1, tag2, tag3 |
| Complexity | Low / Medium / High |
| Gas Efficiency | Low / Medium / High |
| Audit Risk | Low / Medium / High |

<!--
Category must match the directory name.
Platform: evm (default), solana, clarity, move, sui — or a comma list
  for cross-platform patterns. Non-EVM platforms are surfaced in INDEX.md.
Tags: 3-6 tags, lowercase, singular nouns (vault not vaults), reuse
  existing tags where possible (grep '| Tags |' patterns/*/*.md).
-->

## Use When

- Condition 1 when this pattern is appropriate
- Condition 2
- Condition 3

## Avoid When

- Condition 1 when this pattern is NOT appropriate
- Condition 2
- Condition 3

## Trade-offs

**Pros:**
- Advantage 1
- Advantage 2

**Cons:**
- Disadvantage 1
- Disadvantage 2

## How It Works

Explain the core concept and mechanics of this pattern. Inline minimal
code or formulas where they carry the idea. Document significant
variants as `### <Name> Variant` subsections.

## Implementation

<!-- Optional. Focus on the pattern itself. Abstract away unrelated
     details (transfers, oracle calls, etc.) with descriptive function
     names -->

```solidity
contract PatternExample {
    // Key state variables

    // Core pattern logic here
    // Use abstract functions for implementation details:
    //   _doSomething()  instead of  token.transfer(...)
}
```

## Key Points

- Implementation constraints, boundary conditions, and what to test
- Each point should be actionable: a check, a bound, or a test case

## Source Evidence

<!-- Cite as GitHub permalinks pinned to a commit SHA, never local
     clone paths: [`src/File.sol:123`](https://github.com/org/repo/blob/<sha>/src/File.sol#L123) -->

- Protocol X does Y in [`src/File.sol:123-145`](https://github.com/org/repo/blob/abc123/src/File.sol#L123-L145).

## Real-World Examples

- [Protocol Name](https://github.com/org/repo) - brief note

## Related Patterns

- [Related Pattern 1](../category/pattern-name.md) - how it relates
- [Related Pattern 2](../category/pattern-name.md) - how it relates

## References

- [Article/Doc Title](https://url) - description
- [EIP-XXXX](https://eips.ethereum.org/EIPS/eip-xxxx) - if applicable
