# Phase 4: Security Threats

Method: Misuse cases + STRIDE + smart contract checklist — discover security requirements and risks.

```
You are a requirements proposer focusing on security threats.

Read the current items from: {{INPUT_FILE}}
Propose up to {{COUNT}} NEW items not already present.

## Method

Three complementary techniques. Run all, collect unique items.

### 1. Misuse Case Analysis

For each existing FR:
1. **Invert:** "How could an attacker exploit this?"
2. **Propose countermeasure:** new FR or note on existing FR
3. **Iterate:** "Can the attacker defeat the countermeasure?"

Example:
- FR: "Users can deposit assets" → Attacker: "deposit dust to grief storage" → R: dust griefing → FR: minimum deposit

### 2. STRIDE per Data Flow

For each data flow implied by FRs (token transfers, state changes, external calls):

| Threat | Question | Example |
|--------|----------|---------|
| **Spoofing** | Can someone impersonate a legitimate actor? | Third party sets referrer for victim |
| **Tampering** | Can data be modified unexpectedly? | Oracle price manipulated mid-tx |
| **Repudiation** | Can actions be denied? | Fee distribution without event trail |
| **Info Disclosure** | Can sensitive data leak? | (Usually low risk for public chains) |
| **Denial of Service** | Can the system be blocked? | Fee receiver reverts, blocking all deposits |
| **Elevation** | Can someone gain unauthorized access? | Bypassing onlyOwner via delegatecall |

### 3. Smart Contract Checklist

Read `validate-requirements/rules/smart-contract-threats.md` for the full list of 15 threat categories. Walk each category against existing items. For each uncovered relevant category → propose R + mitigation FR.
```
