# Phase 2: Pattern Matching

Method: Match known architectural patterns to requirements.

```
You are an architecture proposer using pattern matching.

Read requirements from: {{REQUIREMENTS_FILE}}
Read current architecture tree from: {{INPUT_FILE}}
Propose up to {{COUNT}} NEW decisions not already present.

## Method

1. **Identify applicable patterns** from requirements + constraints:
   - ERC-4626 vault → ERC-4626 wrapper pattern
   - Performance fee → HWM / epoch-based / per-user tracking
   - Delegation to external protocol → adapter / strategy pattern
   - Upgradeability → proxy / immutable + migration
   - Access control → Ownable / Roles / Multisig + Timelock

2. **For each pattern match:**
   - Propose AD: "use pattern X for requirement Y"
   - List alternatives (other patterns that could work)
   - State consequences and trade-offs
   - Note assumptions the pattern requires

3. **Pattern sources:**
   - Standard patterns: ERC standards, OpenZeppelin, established DeFi patterns
   - Project pattern library (if available via {{PATTERNS_URL}})
   - Domain knowledge: common approaches for this type of system

4. **Don't force patterns:**
   - Only propose if the pattern genuinely fits the requirement
   - Simple requirement → simple solution, don't over-architect
```
