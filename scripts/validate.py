from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCAN = [
    ROOT / "client.yml",
    ROOT / "02-ownership",
    ROOT / "03-brand-assets",
    ROOT / "04-licensing",
    ROOT / "05-flora-summit",
    ROOT / "06-closing",
]

patterns = [
    r"\bREQUIRED\b",
    r"\[EFFECTIVE DATE\]",
    r"\[AUTHORIZED OPERATOR LEGAL NAME\]",
    r"REQUIRED_EXACT_PROCESSOR_OR_DISTRIBUTOR_LLC_NAME",
]

hits = []
for target in SCAN:
    paths = [target] if target.is_file() else list(target.rglob("*.md"))
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            if any(re.search(p, line) for p in patterns):
                hits.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()}")

if hits:
    print("Unresolved fields found:")
    print("\n".join(hits))
    sys.exit(1)

print("Validation passed: no unresolved required fields.")
