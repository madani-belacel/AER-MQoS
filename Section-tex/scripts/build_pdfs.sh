#!/usr/bin/env bash
# Regenerate main-ieee.pdf (IEEE two-column)
# from Section-tex/. Usage: ./scripts/build_pdfs.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
build_one() {
  local doc="$1"
  TEXINPUTS="./templates/ieee/:$TEXINPUTS" BSTINPUTS="./templates/ieee/:$BSTINPUTS" pdflatex -interaction=nonstopmode "$doc.tex"
  if [[ -f "bib/references.bib" ]]; then
    bibtex "$doc" || { echo "ERROR: bibtex failed for $doc"; exit 1; }
  fi
  pdflatex -interaction=nonstopmode "$doc.tex"
  pdflatex -interaction=nonstopmode "$doc.tex"
}
build_one main-ieee
echo "Wrote: $ROOT/main-ieee.pdf"
