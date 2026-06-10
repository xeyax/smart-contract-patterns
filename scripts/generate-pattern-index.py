#!/usr/bin/env python3
"""Generate patterns/INDEX.md from pattern file metadata.

Reads all .md files in patterns/*/, extracts metadata and key sections,
produces a lightweight index for agent consumption. Also refreshes the
generated category table in README.md (between the GENERATED:CATEGORIES
markers).

Usage: python3 scripts/generate-pattern-index.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
PATTERNS_DIR = ROOT / "patterns"
OUTPUT = PATTERNS_DIR / "INDEX.md"
README = ROOT / "README.md"

CATEGORY_DESCRIPTIONS = {
    "access-control": "Roles, authority handoff, scoped permissions, rate-limited privileges.",
    "automation": "Keeper/bot execution, triggers, cranks, permissionless maintenance.",
    "cross-chain": "Bridges, cross-chain messaging, rollup exits, custody, finality.",
    "governance": "Voting, timelocks, parameter changes, emergency powers.",
    "lending": "Collateral, interest-rate models, liquidations, bad-debt handling.",
    "liquidity": "AMMs, concentrated liquidity, pool fees, LP accounting.",
    "math": "Fixed-point arithmetic, rounding, numerical safety.",
    "monitoring": "On-chain risk monitors, circuit breakers, invariant checks.",
    "oracles": "Price feeds, TWAP, staleness, manipulation resistance.",
    "perps": "Perpetual futures: funding, margin, position settlement.",
    "rewards": "Staking rewards, emissions, distribution accounting.",
    "routing": "Swap routing, order settlement, aggregation.",
    "token-integration": "Safely consuming external or non-standard tokens.",
    "tokens": "Token implementations and transfer mechanics.",
    "upgrades": "Proxies, migrations, versioning.",
    "vaults": "Share accounting, deposits/withdrawals, NAV, vault fees.",
    "zero-knowledge": "ZK proof verification and integration.",
}

# Sections every file of a given type must have (validate-patterns.py
# enforces these; the generator only warns).
REQUIRED_SECTIONS = {
    "pattern": ["Metadata", "Use When", "Avoid When", "How It Works", "Related Patterns"],
    "risk": ["Metadata"],
    "req": ["Metadata"],
}


def extract_section(text: str, heading: str) -> list[str]:
    """Extract bullet points from a ## section."""
    pattern = rf"^## {re.escape(heading)}\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if not match:
        return []
    lines = []
    for line in match.group(1).strip().splitlines():
        line = line.strip()
        if line.startswith("- "):
            lines.append(line[2:].strip())
    return lines


def has_section(text: str, heading: str) -> bool:
    return re.search(rf"^#{{2,3}} {re.escape(heading)}\s*$", text, re.MULTILINE) is not None


def extract_description(text: str) -> str:
    """Extract the > one-liner description."""
    for line in text.splitlines():
        if line.startswith("> "):
            return line[2:].strip()
    return ""


def extract_metadata(text: str) -> dict:
    """Extract the | Property | Value | rows from the Metadata section."""
    meta = {}
    match = re.search(r"^## Metadata\s*\n(.*?)(?=\n## |\Z)", text, re.MULTILINE | re.DOTALL)
    if not match:
        return meta
    for row in re.finditer(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", match.group(1), re.MULTILINE):
        key = row.group(1).strip().lower()
        if key in ("property", "----------", "--------"):
            continue
        meta[key] = row.group(2).strip()
    return meta


def extract_req_ids(text: str) -> str:
    """Extract requirement IDs and summaries from req-* files.

    Supports formats:
      ## R1: Freshness          (heading)
      **R1: Freshness**         (bold)
      | R1: Freshness | ... |   (table)
    """
    ids = []
    # Format: ## R1: Name
    for match in re.finditer(r"^##\s+(R\d+):\s+(.+)$", text, re.MULTILINE):
        ids.append(f"{match.group(1)}: {match.group(2).strip()}")
    if not ids:
        # Format: **R1: Name**
        for match in re.finditer(r"\*\*?(R\d+)[:\s]+([^*\n]+)", text):
            ids.append(f"{match.group(1)}: {match.group(2).strip().rstrip('*')}")
    if not ids:
        # Format: | R1: Name | ... |
        for match in re.finditer(r"\|\s*(R\d+)[\s:]+([^|]+)\|", text):
            ids.append(f"{match.group(1)}: {match.group(2).strip()}")
    return ", ".join(ids)


def classify(filename: str) -> str:
    if filename.startswith("pattern-"):
        return "pattern"
    if filename.startswith("risk-"):
        return "risk"
    if filename.startswith("req-"):
        return "req"
    return "other"


def condense(items: list[str], max_len: int = 120) -> str:
    """Join bullet points into a short semicolon-separated string."""
    result = "; ".join(items)
    if len(result) > max_len:
        cut = result[:max_len]
        if ";" in cut:
            result = cut.rsplit(";", 1)[0]
        else:
            # no clause boundary — cut at a word boundary instead of mid-word
            result = cut.rsplit(" ", 1)[0] + " …"
    return result


def process_file(filepath: Path) -> dict:
    text = filepath.read_text()
    name = filepath.name
    ftype = classify(name)
    desc = extract_description(text)
    meta = extract_metadata(text)

    info = {"name": name, "type": ftype, "desc": desc, "meta": meta}

    if ftype == "pattern":
        use_when = extract_section(text, "Use When")
        info["use_when"] = condense(use_when)
    elif ftype == "risk":
        # For risks, extract "Applies When" or use description
        applies = extract_section(text, "Applies When")
        if not applies:
            applies = extract_section(text, "Context")
        info["triggered"] = condense(applies) if applies else desc
    elif ftype == "req":
        info["req_ids"] = extract_req_ids(text)

    for heading in REQUIRED_SECTIONS.get(ftype, []):
        if heading == "Related Patterns" and has_section(text, "Related Anti-Patterns"):
            continue
        if not has_section(text, heading):
            rel = filepath.relative_to(ROOT)
            print(f"  warning: {rel} missing required section '## {heading}'")
    if not desc:
        print(f"  warning: {filepath.relative_to(ROOT)} missing '> ' one-line description")

    return info


def display_name(info: dict) -> str:
    """File name, annotated with platform when it is not EVM."""
    platform = info["meta"].get("platform", "").lower()
    if platform and platform != "evm":
        return f"{info['name']} ({platform})"
    return info["name"]


def update_readme(category_counts: dict):
    """Refresh the generated category table in README.md, if markers exist."""
    if not README.exists():
        return
    text = README.read_text()
    begin = "<!-- BEGIN GENERATED:CATEGORIES -->"
    end = "<!-- END GENERATED:CATEGORIES -->"
    if begin not in text or end not in text:
        return

    rows = [
        "| Category | Docs | Scope |",
        "|----------|------|-------|",
    ]
    for cat, counts in sorted(category_counts.items()):
        desc = CATEGORY_DESCRIPTIONS.get(cat, "")
        total = sum(counts.values())
        detail = ", ".join(
            f"{n} {label}" for label, n in counts.items() if n
        )
        rows.append(f"| [{cat}](patterns/{cat}/) | {total} ({detail}) | {desc} |")

    table = "\n".join(rows)
    new_text = re.sub(
        rf"{re.escape(begin)}.*?{re.escape(end)}",
        f"{begin}\n{table}\n{end}",
        text,
        flags=re.DOTALL,
    )
    if new_text != text:
        README.write_text(new_text)
        print(f"Updated {README}")


def generate_index():
    categories = sorted(
        [d for d in PATTERNS_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.name,
    )

    lines = [
        "# Pattern Library Index\n",
        "> Auto-generated from pattern metadata. Regenerate: `python3 scripts/generate-pattern-index.py`\n",
    ]

    category_counts = {}

    for cat_dir in categories:
        files = sorted(cat_dir.glob("*.md"))
        if not files:
            continue

        entries = [process_file(f) for f in files]
        patterns = [e for e in entries if e["type"] == "pattern"]
        risks = [e for e in entries if e["type"] == "risk"]
        reqs = [e for e in entries if e["type"] == "req"]

        category_counts[cat_dir.name] = {
            "patterns": len(patterns),
            "risks": len(risks),
            "reqs": len(reqs),
        }

        lines.append(f"## {cat_dir.name}\n")

        if patterns:
            lines.append("### Patterns\n")
            lines.append("| File | Description | Use When |")
            lines.append("|------|-------------|----------|")
            for p in patterns:
                lines.append(f"| {display_name(p)} | {p['desc']} | {p.get('use_when', '')} |")
            lines.append("")

        if risks:
            lines.append("### Risks\n")
            lines.append("| File | Triggered When |")
            lines.append("|------|---------------|")
            for r in risks:
                lines.append(f"| {display_name(r)} | {r.get('triggered', '')} |")
            lines.append("")

        if reqs:
            lines.append("### Requirements\n")
            lines.append("| File | Applies To |")
            lines.append("|------|-----------|")
            for r in reqs:
                applies = r.get("req_ids") or r["desc"]
                lines.append(f"| {display_name(r)} | {applies} |")
            lines.append("")

    OUTPUT.write_text("\n".join(lines))
    print(f"Generated {OUTPUT} ({len(lines)} lines)")

    update_readme(category_counts)


if __name__ == "__main__":
    generate_index()
