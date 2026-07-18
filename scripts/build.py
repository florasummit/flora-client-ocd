from pathlib import Path
import hashlib
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "09-generated"
OUT.mkdir(exist_ok=True)

parts = [
    ROOT / "02-ownership/01-founder-brand-ownership-declaration.md",
    ROOT / "02-ownership/02-brand-foundation-agreement.md",
    ROOT / "02-ownership/03-brand-owner-written-consent.md",
    ROOT / "03-brand-assets/EXHIBIT-A-brand-assets.md",
    ROOT / "03-brand-assets/EXHIBIT-B-logo-icon-specimens.md",
    ROOT / "03-brand-assets/EXHIBIT-C-domain-social-assets.md",
    ROOT / "03-brand-assets/EXHIBIT-D-prior-rights-disclosures.md",
    ROOT / "04-licensing/01-quality-control-and-brand-use-schedule.md",
    ROOT / "04-licensing/03-operator-and-license-schedule.md",
    ROOT / "05-flora-summit/01-exclusive-sweepstakes-partnership-agreement.md",
    ROOT / "06-closing/01-signature-packet-cover.md",
    ROOT / "06-closing/03-closing-certificate.md",
]

basename = "OCD-Brand-Foundation-and-Flora-Summit-Partnership-Package"
md = OUT / f"{basename}.md"
docx = OUT / f"{basename}.docx"
pdf = OUT / f"{basename}.pdf"

missing = [str(path.relative_to(ROOT)) for path in parts if not path.exists()]
if missing:
    raise FileNotFoundError(
        "Missing package files:\n" + "\n".join(f"- {path}" for path in missing)
    )

# Join documents with normal spacing only.
# This removes the visible "\newpage" text from both DOCX and PDF output.
combined = "\n\n---\n\n".join(
    path.read_text(encoding="utf-8").strip()
    for path in parts
)

md.write_text(combined + "\n", encoding="utf-8")

pandoc = shutil.which("pandoc")

if pandoc:
    subprocess.run(
        [
            pandoc,
            str(md),
            "--from=gfm",
            "--to=docx",
            "--standalone",
            "-o",
            str(docx),
        ],
        check=True,
    )

    try:
        subprocess.run(
            [
                pandoc,
                str(md),
                "--from=gfm",
                "--standalone",
                "--pdf-engine=xelatex",
                "-V",
                "geometry:margin=0.7in",
                "-V",
                "fontsize=10pt",
                "-o",
                str(pdf),
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"PDF build failed: {exc}")
else:
    print("Pandoc not installed; Markdown package created.")

manifest = []

for path in sorted(OUT.glob(f"{basename}.*")):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest.append(f"{digest}  {path.name}")

(OUT / "SHA256SUMS.txt").write_text(
    "\n".join(manifest) + "\n",
    encoding="utf-8",
)

print(f"Built package in {OUT}")
