"""Ingest the BAPS Master Glossary PDF into ``src/w1_data/master_glossary.json``.

The PDF is a three-column table (Words · Meaning · Book Name). We extract the **canonical
spelling** of every term (the critical output — it feeds the fuzzy canonical-spelling stage and
the in-vocabulary guard) plus a best-effort definition.

Usage:
    python scripts/ingest_glossary_pdf.py [PATH_TO_PDF]

Requires ``pdftotext`` (poppler: ``brew install poppler``). The PDF is a clean digital export,
so ``pdftotext -layout`` preserves the column structure well enough to parse deterministically.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

_DEFAULT_PDF = Path(
    "/Users/jaypatel/Desktop/Repositories/Mandir/NEW INFORMATION MASTER THE MOST "
    "IMPORTANT DOCUMENTS/Master Glossary - New - 06-11-25.pdf"
)
_OUT = Path(__file__).resolve().parents[1] / "src" / "w1_data" / "master_glossary.json"

# Known source-book labels that occupy the right-hand column; stripped from definitions.
_BOOKS = ("Vachanamrut", "Swamini Vato", "Swamini Vaato", "Bhagwad Gita", "Satsang Diksha")

_COLUMN_GAP = re.compile(r"\s{2,}")  # 2+ spaces separates table columns
_DATE = re.compile(r"\d{1,2}/\d{1,2}/\d{2,4}")


def _pdftotext(pdf: Path) -> str:
    out = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=True, capture_output=True, text=True,
    )
    return out.stdout


def _is_noise(line: str) -> bool:
    """Page headers ('Glossary  <date>'), the column header, and footers (page numbers)."""
    s = line.strip()
    if not s:
        return True
    if s.isdigit():
        return True
    if s.startswith("Glossary") and _DATE.search(s):
        return True
    left = _COLUMN_GAP.split(s, 1)[0]
    return left in {"Words", "Glossary"}


def _looks_like_term(left: str) -> bool:
    """A real term is a short label (1-3 words), not a wrapped sentence fragment."""
    if not left or len(left) > 35:
        return False
    if left[-1] in ".,:;–-":
        return False
    return len(left.split()) <= 3


def _strip_book(text: str) -> str:
    for book in _BOOKS:
        text = re.sub(rf"\s{{2,}}{re.escape(book)}\s*$", " ", text)
        text = text.replace(book, " ")
    return _COLUMN_GAP.sub(" ", text).strip()


def parse(raw: str) -> list[dict]:
    """Parse pdftotext '-layout' output into ordered, de-duplicated glossary entries."""
    entries: list[dict] = []
    current: dict | None = None

    for line in raw.splitlines():
        if _is_noise(line):
            continue
        starts_entry = bool(line) and not line[0].isspace() and _COLUMN_GAP.search(line)
        left = _COLUMN_GAP.split(line.strip(), 1)[0] if starts_entry else ""

        if starts_entry and _looks_like_term(left):
            if current:
                entries.append(current)
            parts = _COLUMN_GAP.split(line.strip(), 1)
            current = {"canonical": parts[0].strip(), "meaning": parts[1] if len(parts) > 1 else ""}
        elif current is not None:  # continuation line (indented or unindented wrap)
            current["meaning"] += " " + line.strip()

    if current:
        entries.append(current)

    seen: set[str] = set()
    out: list[dict] = []
    for e in entries:
        canonical = e["canonical"].strip()
        if len(canonical) < 2 or canonical.lower() in seen:
            continue
        seen.add(canonical.lower())
        out.append({
            "canonical": canonical,
            "definition": _strip_book(e["meaning"]),
            "source": "Master Glossary (BAPS)",
        })
    return out


def main(argv: list[str]) -> int:
    pdf = Path(argv[1]) if len(argv) > 1 else _DEFAULT_PDF
    if not pdf.exists():
        print(f"PDF not found: {pdf}", file=sys.stderr)
        return 1
    entries = parse(_pdftotext(pdf))
    _OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} terms -> {_OUT.relative_to(Path.cwd())}")
    print("Sample:", ", ".join(e["canonical"] for e in entries[:8]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
