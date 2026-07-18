from pathlib import Path
import hashlib
import shutil
import subprocess

try:
    from PIL import Image
except ImportError:
    Image = None

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "09-generated"
OUT.mkdir(exist_ok=True)

ASSET_ROOT = ROOT / "03-brand-assets"
MANIFEST_DIR = ROOT / "08-records" / "manifests"
MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
BRAND_ASSET_MANIFEST = MANIFEST_DIR / "brand-assets-manifest.md"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_dimensions(path: Path) -> str:
    if Image is None:
        return "Unavailable (install Pillow to detect dimensions)"
    try:
        with Image.open(path) as image:
            width, height = image.size
        return f"{width} × {height} px"
    except Exception:
        return "Not applicable"


def generate_brand_asset_manifest() -> None:
    allowed = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".pdf", ".ai", ".eps", ".psd", ".tif", ".tiff"}
    assets = sorted(
        path for path in ASSET_ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in allowed
    )

    lines = [
        "# Brand Asset Manifest",
        "",
        "This manifest identifies the exact technical files associated with the OCD Brand Assets.",
        "It is automatically regenerated each time `scripts/build.py` runs.",
        "",
    ]

    for asset in assets:
        relative = asset.relative_to(ROOT).as_posix()
        lines.extend([
            f"## `{relative}`",
            "",
            f"**File:** `{relative}`  ",
            f"**Format:** {asset.suffix.lstrip('.').upper()}  ",
            f"**Dimensions:** {image_dimensions(asset)}  ",
            f"**File Size:** {asset.stat().st_size:,} bytes  ",
            f"**SHA-256:** `{sha256_file(asset)}`  ",
            "",
        ])

    BRAND_ASSET_MANIFEST.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


generate_brand_asset_manifest()

parts = [
    ROOT / "02-ownership/01-founder-brand-ownership-declaration.md",
    ROOT / "02-ownership/02-brand-foundation-agreement.md",
    ROOT / "02-ownership/03-brand-owner-written-consent.md",
    ROOT / "03-brand-assets/EXHIBIT-A-brand-assets.md",
    ROOT / "03-brand-assets/EXHIBIT-B-logo-icon-specimens.md",
    ROOT / "03-brand-assets/EXHIBIT-C-packaging-trade-dress.md",
    ROOT / "03-brand-assets/EXHIBIT-D-domain-social-assets.md",
    ROOT / "03-brand-assets/EXHIBIT-E-prior-rights-disclosures.md",
    BRAND_ASSET_MANIFEST,
    ROOT / "04-licensing/01-quality-control-and-brand-use-schedule.md",
    ROOT / "04-licensing/03-operator-and-license-schedule.md",
    ROOT / "05-flora-summit/01-exclusive-sweepstakes-partnership-agreement.md",
    ROOT / "06-closing/04-final-business-structure-decisions.md",
    ROOT / "06-closing/01-signature-packet-cover.md",
    ROOT / "06-closing/03-closing-certificate.md",
]

basename = "OCD-Brand-Foundation-and-Flora-Summit-Partnership-Package"
md = OUT / f"{basename}.md"
docx = OUT / f"{basename}.docx"
pdf = OUT / f"{basename}.pdf"
manifest_file = OUT / "SHA256SUMS.txt"

missing = [str(path.relative_to(ROOT)) for path in parts if not path.exists()]
if missing:
    raise FileNotFoundError("Missing package files:\n" + "\n".join(f"- {path}" for path in missing))

combined = "\n\n---\n\n".join(path.read_text(encoding="utf-8").strip() for path in parts)
md.write_text(combined + "\n", encoding="utf-8")

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
        print(f"PDF build failed: {exc}")
else:
    print("Pandoc not installed; Markdown package created only.")

manifest_entries = []
for path in [md, docx, pdf, BRAND_ASSET_MANIFEST]:
    if path.exists():
        manifest_entries.append(f"{sha256_file(path)}  {path.relative_to(ROOT).as_posix()}")

manifest_file.write_text("\n".join(manifest_entries) + "\n", encoding="utf-8")
print(f"Built package in {OUT}")
