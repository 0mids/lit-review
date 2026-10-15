#!/bin/sh
# Rebuild figures' data macros, bibliography and PDF.
set -e
cd "$(dirname "$0")"
python3 scripts/make_bib.py
pdflatex -interaction=nonstopmode main.tex >/dev/null || true
bibtex main >/dev/null || true
pdflatex -interaction=nonstopmode main.tex >/dev/null || true
pdflatex -interaction=nonstopmode main.tex >/dev/null || true
grep -E "^! |undefined|Overfull" main.log | sort | uniq -c | head -40 || true
pdfinfo main.pdf | grep Pages
