#!/usr/bin/env python3
"""Validate pattern/risk/req files for CI.

Errors (exit 1):
  - missing required sections per file type
  - missing '> ' one-line description
  - ephemeral local-path citations (/private/tmp/...)
  - broken relative links
  - Metadata Category not matching the directory name

Warnings (reported, never fail):
  - patterns missing Trade-offs

Usage: python3 scripts/validate-patterns.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PATTERNS_DIR = ROOT / "patterns"

REQUIRED_SECTIONS = {
    "pattern": ["Metadata", "Use When", "Avoid When", "How It Works", "Related Patterns"],
    "risk": ["Metadata"],
    "req": ["Metadata"],
}

# At least one of these must ground the file in real sources.
EVIDENCE_SECTIONS = ["Source Evidence", "Real-World Examples", "Real-World Incidents", "References"]

LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

errors = []
warnings = []


def classify(filename: str) -> str:
    for prefix in ("pattern", "risk", "req"):
        if filename.startswith(prefix + "-"):
            return prefix
    return "other"


def has_section(text: str, heading: str) -> bool:
    return re.search(rf"^#{{2,3}} {re.escape(heading)}\s*$", text, re.MULTILINE) is not None


def check_file(f: Path):
    rel = f.relative_to(ROOT)
    text = f.read_text()
    ftype = classify(f.name)

    for heading in REQUIRED_SECTIONS.get(ftype, []):
        if heading == "Related Patterns":
            if not (has_section(text, "Related Patterns") or has_section(text, "Related Anti-Patterns")):
                errors.append(f"{rel}: missing '## Related Patterns' (or '## Related Anti-Patterns')")
        elif not has_section(text, heading):
            errors.append(f"{rel}: missing required section '## {heading}'")

    if not any(line.startswith("> ") for line in text.splitlines()):
        errors.append(f"{rel}: missing '> ' one-line description")

    # req-* files may be normative definitions with no external evidence
    if ftype in ("pattern", "risk") and not any(has_section(text, h) for h in EVIDENCE_SECTIONS):
        errors.append(f"{rel}: no evidence section ({' / '.join(EVIDENCE_SECTIONS)})")

    if ftype == "pattern" and not has_section(text, "Trade-offs"):
        warnings.append(f"{rel}: no Trade-offs section")

    if "/private/tmp/" in text or "/tmp/defillama-source" in text:
        errors.append(f"{rel}: ephemeral local-path citation (use a GitHub permalink)")

    meta_cat = re.search(r"^\|\s*Category\s*\|\s*([^|]+?)\s*\|", text, re.MULTILINE)
    if meta_cat and meta_cat.group(1) != f.parent.name:
        errors.append(f"{rel}: Metadata Category '{meta_cat.group(1)}' != directory '{f.parent.name}'")

    # strip fenced code blocks and inline code so Solidity `arr[i](x)` is not parsed as a link
    prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    prose = re.sub(r"`[^`\n]*`", "", prose)
    for m in LINK.finditer(prose):
        target = m.group(1).split("#")[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (f.parent / target).exists():
            errors.append(f"{rel}: broken relative link '{m.group(1)}'")


def main():
    files = sorted(p for p in PATTERNS_DIR.rglob("*.md") if p.name != "INDEX.md")
    for f in files:
        check_file(f)

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    print(f"\n{len(files)} files checked, {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
