"""
export_txt.py
-------------
Convert iTELL JSON volumes and/or source PDFs into plain .txt files
ready to be run through TAACO, TAALES, TAASSC, and ARTE on Windows.

Output naming convention
------------------------
  Generated volumes:  <volume_id>_<mode>.txt
  Source PDFs:        <stem>_source.txt

Usage
-----
  # Export all generated JSON volumes to txt/
  python export_txt.py jsons --input-dir path/to/jsons --output-dir txt/generated

  # Export source PDFs to txt/
  python export_txt.py pdfs --input-dir path/to/pdfs --output-dir txt/source

  # Export one file at a time
  python export_txt.py jsons --input-dir jsons/ --output-dir out/ --volume chapter1_faithful.json
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# JSON → txt
# ---------------------------------------------------------------------------

def _json_to_txt(json_path: Path, output_dir: Path, volume_id_override: str | None = None) -> Path:
    """
    Extract all chunk text from one iTELL JSON volume and write a single .txt.
    The output filename encodes volume_id and mode, e.g. chapter3_faithful.txt
    """
    # Reuse existing extractor — stays consistent with the feature pipeline
    sys.path.insert(0, str(Path(__file__).parent))
    from extractor.text_extractor import extract_records

    records = extract_records(json_path)
    if not records:
        raise ValueError(f"No text records found in {json_path.name}")

    volume_id = volume_id_override or records[0]["volume_id"]
    mode = records[0]["mode"]

    # One paragraph per page (TAACO works best with paragraph-separated input)
    pages: dict[int, list[str]] = {}
    for r in records:
        pages.setdefault(r["page_order"], []).append(r["chunk_text"])

    paragraphs = [" ".join(chunks) for _, chunks in sorted(pages.items())]
    body = "\n\n".join(p for p in paragraphs if p.strip())

    out_name = f"{volume_id}_{mode}.txt"
    out_path = output_dir / out_name
    out_path.write_text(body, encoding="utf-8")
    return out_path


def export_jsons(input_dir: Path, output_dir: Path, volume: str | None = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    if volume:
        paths = [input_dir / volume]
    else:
        paths = sorted(input_dir.glob("*.json"))

    if not paths:
        logger.error("No JSON files found in %s", input_dir)
        sys.exit(1)

    ok = fail = 0
    for p in paths:
        try:
            out = _json_to_txt(p, output_dir)
            logger.info("Wrote %s", out.name)
            ok += 1
        except Exception as exc:
            logger.warning("Skipping %s: %s", p.name, exc)
            fail += 1

    logger.info("Done — %d exported, %d skipped. Files in: %s", ok, fail, output_dir)


# ---------------------------------------------------------------------------
# Tournament folder → txt
# Walks results/mode_tournament/<textbook>/<itell_mode>.json
# and writes <textbook>_<mode>.txt for each
# ---------------------------------------------------------------------------

def export_tournament(tournament_dir: Path, output_dir: Path) -> None:
    """
    Walk a mode_tournament results directory and export every JSON to .txt.

    Expected structure:
      tournament_dir/
        001/
          itell_condensed.json
          itell_faithful.json
          itell_simplified.json
        002/
          ...

    Output:
      output_dir/
        001_condensed.txt
        001_faithful.txt
        001_simplified.txt
        002_condensed.txt
        ...
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    textbook_dirs = sorted(p for p in tournament_dir.iterdir() if p.is_dir())
    if not textbook_dirs:
        logger.error("No subdirectories found in %s", tournament_dir)
        sys.exit(1)

    ok = fail = 0
    for textbook_dir in textbook_dirs:
        textbook_id = textbook_dir.name
        json_files = sorted(textbook_dir.glob("itell_*.json"))
        if not json_files:
            logger.warning("No itell_*.json files in %s, skipping", textbook_dir.name)
            continue

        for json_path in json_files:
            try:
                out = _json_to_txt(json_path, output_dir, volume_id_override=textbook_id)
                logger.info("Wrote %s", out.name)
                ok += 1
            except Exception as exc:
                logger.warning("Skipping %s/%s: %s", textbook_id, json_path.name, exc)
                fail += 1

    logger.info("Done — %d exported, %d skipped. Files in: %s", ok, fail, output_dir)


# ---------------------------------------------------------------------------
# PDF → txt
# ---------------------------------------------------------------------------

def _pdf_to_txt(pdf_path: Path, output_dir: Path) -> Path:
    """
    Extract text from a PDF keeping only textual content (no tables, images).
    Requires pdfplumber (pip install pdfplumber).
    """
    try:
        import pdfplumber
    except ImportError:
        logger.error("pdfplumber is required for PDF conversion. Run: pip install pdfplumber")
        sys.exit(1)

    pages_text: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if text:
                # Collapse hyphenated line breaks common in PDFs
                text = re.sub(r"-\n(\w)", r"\1", text)
                text = re.sub(r"\n+", "\n", text).strip()
                pages_text.append(text)

    if not pages_text:
        raise ValueError(f"No extractable text in {pdf_path.name}")

    body = "\n\n".join(pages_text)
    out_name = f"{pdf_path.stem}_source.txt"
    out_path = output_dir / out_name
    out_path.write_text(body, encoding="utf-8")
    return out_path


def export_pdfs(input_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = sorted(input_dir.glob("*.pdf"))

    if not paths:
        logger.error("No PDF files found in %s", input_dir)
        sys.exit(1)

    ok = fail = 0
    for p in paths:
        try:
            out = _pdf_to_txt(p, output_dir)
            logger.info("Wrote %s", out.name)
            ok += 1
        except Exception as exc:
            logger.warning("Skipping %s: %s", p.name, exc)
            fail += 1

    logger.info("Done — %d exported, %d skipped. Files in: %s", ok, fail, output_dir)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="export_txt",
        description="Export iTELL JSON volumes and/or source PDFs to .txt for linguistic analysis tools.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- jsons subcommand
    j = sub.add_parser("jsons", help="Convert iTELL JSON volumes to .txt")
    j.add_argument("--input-dir", type=Path, required=True,
                   help="Directory containing iTELL JSON files.")
    j.add_argument("--output-dir", type=Path, default=Path("txt/generated"),
                   help="Output directory for .txt files (default: txt/generated).")
    j.add_argument("--volume", default=None,
                   help="Process a single file instead of the whole directory.")

    # -- pdfs subcommand
    p = sub.add_parser("pdfs", help="Convert source PDFs to .txt")
    p.add_argument("--input-dir", type=Path, required=True,
                   help="Directory containing source PDF files.")
    p.add_argument("--output-dir", type=Path, default=Path("txt/source"),
                   help="Output directory for .txt files (default: txt/source).")

    # -- tournament subcommand
    t = sub.add_parser("tournament", help="Export all mode JSONs from a mode_tournament results folder.")
    t.add_argument("--tournament-dir", type=Path,
                   default=Path("/Users/tobasum/Desktop/itell-volume-generation/results/mode_tournament"),
                   help="Root of the mode_tournament results directory.")
    t.add_argument("--output-dir", type=Path, default=Path("txt/generated"),
                   help="Output directory for .txt files (default: txt/generated).")

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "jsons":
        export_jsons(args.input_dir, args.output_dir, args.volume)
    elif args.command == "pdfs":
        export_pdfs(args.input_dir, args.output_dir)
    elif args.command == "tournament":
        export_tournament(args.tournament_dir, args.output_dir)


if __name__ == "__main__":
    main()
