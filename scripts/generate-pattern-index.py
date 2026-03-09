#!/usr/bin/env python3
"""Generate patterns/INDEX.md from pattern file metadata.

Reads all .md files in patterns/*/, extracts metadata and key sections,
produces a lightweight index for agent consumption.

Usage: python3 scripts/generate-pattern-index.py
"""

import re
from pathlib import Path

PATTERNS_DIR = Path(__file__).parent.parent / "patterns"
OUTPUT = PATTERNS_DIR / "INDEX.md"


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


def extract_description(text: str) -> str:
    """Extract the > one-liner description."""
    for line in text.splitlines():
        if line.startswith("> "):
            return line[2:].strip()
    return ""


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
        result = result[:max_len].rsplit(";", 1)[0]
    return result


def process_file(filepath: Path) -> dict:
    text = filepath.read_text()
    name = filepath.name
    ftype = classify(name)
    desc = extract_description(text)

    info = {"name": name, "type": ftype, "desc": desc}

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

    return info


def generate_index():
    categories = sorted(
        [d for d in PATTERNS_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.name,
    )

    lines = [
        "# Pattern Library Index\n",
        "> Auto-generated from pattern metadata. Regenerate: `python3 scripts/generate-pattern-index.py`\n",
    ]

    for cat_dir in categories:
        files = sorted(cat_dir.glob("*.md"))
        if not files:
            continue

        entries = [process_file(f) for f in files]
        patterns = [e for e in entries if e["type"] == "pattern"]
        risks = [e for e in entries if e["type"] == "risk"]
        reqs = [e for e in entries if e["type"] == "req"]

        lines.append(f"## {cat_dir.name}\n")

        if patterns:
            lines.append("### Patterns\n")
            lines.append("| File | Description | Use When |")
            lines.append("|------|-------------|----------|")
            for p in patterns:
                lines.append(f"| {p['name']} | {p['desc']} | {p.get('use_when', '')} |")
            lines.append("")

        if risks:
            lines.append("### Risks\n")
            lines.append("| File | Triggered When |")
            lines.append("|------|---------------|")
            for r in risks:
                lines.append(f"| {r['name']} | {r.get('triggered', '')} |")
            lines.append("")

        if reqs:
            lines.append("### Requirements\n")
            lines.append("| File | Applies To |")
            lines.append("|------|-----------|")
            for r in reqs:
                applies = r.get("req_ids", r["desc"])
                lines.append(f"| {r['name']} | {applies} |")
            lines.append("")

    OUTPUT.write_text("\n".join(lines))
    print(f"Generated {OUTPUT} ({len(lines)} lines)")


if __name__ == "__main__":
    generate_index()
