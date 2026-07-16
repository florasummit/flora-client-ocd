name: Build OCD Signing Package

on:
  workflow_dispatch:
  push:
    paths:
      - "client.yml"
      - "ownership/**"
      - "agreements/**"
      - "exhibits/**"
      - ".github/workflows/build-ocd-package.yml"

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Validate required files
        shell: bash
        run: |
          set -euo pipefail
          required=(
            "client.yml"
            "ownership/01-founder-brand-ownership-declaration.md"
            "agreements/01-brand-foundation-agreement.md"
            "agreements/02-exclusive-sweepstakes-partnership-agreement.md"
            "agreements/03-closing-certificate.md"
            "exhibits/exhibit-a-brand-assets.md"
            "exhibits/exhibit-b-logo-icon-specimens.md"
            "exhibits/exhibit-c-domain-social-assets.md"
            "exhibits/exhibit-d-operator-license-information.md"
            "exhibits/exhibit-e-prior-rights-disclosures.md"
          )

          for file in "${required[@]}"; do
            test -f "$file" || { echo "Missing required file: $file"; exit 1; }
          done

      - name: Block unresolved signature build
        shell: bash
        run: |
          set -euo pipefail
          if grep -RInE "REQUIRED_PROCESSOR_OR_DISTRIBUTOR_LLC_NAME|\[AUTHORIZED OPERATOR LEGAL NAME\]"             client.yml agreements ownership exhibits; then
            echo "Unresolved Authorized Operator legal name. Complete client.yml and source documents before final build."
            exit 1
          fi

      - name: Install Pandoc and PDF dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y pandoc texlive-xetex texlive-fonts-recommended

      - name: Assemble package
        shell: bash
        run: |
          set -euo pipefail
          mkdir -p generated

          cat             ownership/01-founder-brand-ownership-declaration.md             agreements/01-brand-foundation-agreement.md             exhibits/exhibit-a-brand-assets.md             exhibits/exhibit-b-logo-icon-specimens.md             exhibits/exhibit-c-domain-social-assets.md             exhibits/exhibit-d-operator-license-information.md             exhibits/exhibit-e-prior-rights-disclosures.md             agreements/02-exclusive-sweepstakes-partnership-agreement.md             agreements/03-closing-certificate.md             > generated/OCD-Brand-Foundation-and-Flora-Summit-Package.md

      - name: Build DOCX
        run: |
          pandoc generated/OCD-Brand-Foundation-and-Flora-Summit-Package.md             --from=gfm             --to=docx             --output=generated/OCD-Brand-Foundation-and-Flora-Summit-Package.docx

      - name: Build PDF
        run: |
          pandoc generated/OCD-Brand-Foundation-and-Flora-Summit-Package.md             --from=gfm             --pdf-engine=xelatex             --output=generated/OCD-Brand-Foundation-and-Flora-Summit-Package.pdf

      - name: Create manifest
        shell: bash
        run: |
          set -euo pipefail
          (
            cd generated
            sha256sum OCD-Brand-Foundation-and-Flora-Summit-Package.* > SHA256SUMS.txt
          )

      - name: Upload generated package
        uses: actions/upload-artifact@v4
        with:
          name: OCD-signing-package
          path: |
            generated/OCD-Brand-Foundation-and-Flora-Summit-Package.md
            generated/OCD-Brand-Foundation-and-Flora-Summit-Package.docx
            generated/OCD-Brand-Foundation-and-Flora-Summit-Package.pdf
            generated/SHA256SUMS.txt
