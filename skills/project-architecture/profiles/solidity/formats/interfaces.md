# Interface Formatting Rules

Rules for `interfaces/*.sol` artifacts.

## Access modifiers

Place access modifiers as a trailing comment **after the function signature**, not inside `@dev` or `@param`:

```solidity
// Good
function pause() external; // onlyOwner

// Bad — inside @dev
/// @dev Bounded: newFeeBps <= 3000 (30%). // onlyOwner
function setPerformanceFee(uint256 newFeeBps) external;

// Bad — inside @param
/// @param caller Address to update. // onlyOwner
function setTrustedCaller(address caller, bool trusted) external;
```

Multiple modifiers: `function rebalance() external; // onlyKeeper, nonReentrant`

## Section headers

Group functions with comment block separators:

```solidity
// ---------------------------------------------------------------
//  Admin actions (onlyOwner)
// ---------------------------------------------------------------
```

When the section header names the modifier (e.g. `Admin actions (onlyOwner)`), individual functions still carry the trailing `// onlyOwner` for grep-ability.

## NatSpec

- `/// @notice` — one-line description of what the function does (required for every function).
- `/// @dev` — implementation notes, constraints, behavioral details. No access modifiers here.
- `/// @param` — parameter description only. No access modifiers here.
- `/// @return` — return value description.
