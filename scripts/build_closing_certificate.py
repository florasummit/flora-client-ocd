"""
Builds the OCD Closing Certificate as its own standalone document.

This is deliberately separate from scripts/build.py. The Closing Certificate
certifies that the FULL transaction — including the Flora Summit MCA / Order
Form / Fee Schedule package (Signing Event 3, generated from flora-legal-os,
not from this repo) — is complete. It was pulled out of the main build
because signing it before the MCA package exists would mean checking boxes
that aren't true yet.

Run this once everything on the closing checklist (06-closing/02-closing-checklist.md)
is actually done. At that point:
  1. Fill in the remaining blanks in 06-closing/03-closing-certificate.md
     (Closing Date, the checkbox list, Open Items — update or clear the
     Open Items now that they're resolved).
  2. Run this script: python scripts/build_closing_certificate.py
  3. Send/print the resulting file from 09-generated/.

Usage:
    python scripts/build_closing_certificate.py
"""

from pathlib import Path
import hashlib
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "09-generated"
OUT.mkdir(exist_ok=True)

SOURCE = ROOT / "06-closing" / "03-closing-certificate.md"
basename = "OCD-Closing-Certificate"

if not SOURCE.exists():
    raise FileNotFoundError(f"Missing source file: {SOURCE}")

md = OUT / f"{basename}.md"
docx = OUT / f"{basename}.docx"
pdf = OUT / f"{basename}.pdf"
manifest_file = OUT / f"{basename}-SHA256.txt"

md.write_text(SOURCE.read_text(encoding="utf-8").strip() + "\n", encoding="utf-8")

pandoc = shutil.which("pandoc")
if pandoc:
    common_args = [
        pandoc,
        str(md),
        "--from=markdown",
        "--standalone",
        "--resource-path",
        str(ROOT),
    ]

    subprocess.run(common_args + ["--to=docx", "-o", str(docx)], cwd=ROOT, check=True)

    try:
        subprocess.run(
            common_args + [
                "--pdf-engine=xelatex",
                "-V", "geometry:margin=0.7in",
                "-V", "fontsize=10pt",
                "-o", str(pdf),
            ],
            cwd=ROOT,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"PDF build failed via xelatex ({exc}). "
              f"Try: soffice --headless --convert-to pdf --outdir {OUT} {docx}")
else:
    print("Pandoc not installed; Markdown output created only.")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


entries = []
for path in [md, docx, pdf]:
    if path.exists():
        entries.append(f"{sha256_file(path)}  {path.relative_to(ROOT).as_posix()}")

manifest_file.write_text("\n".join(entries) + "\n", encoding="utf-8")
print(f"Built Closing Certificate in {OUT}")
