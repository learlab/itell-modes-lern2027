"""
collate.py
----------
Merge CSV outputs from TAACO, TAALES, TAASSC, and ARTE into a single
master CSV, joined on filename.

Each tool produces a CSV where the first column is the input filename
(e.g. chapter1_faithful.txt). This script:
  1. Reads each tool CSV
  2. Normalises the filename column to a common key (strips .txt, lower)
  3. Joins all four on that key
  4. Splits the key into volume_id and mode columns
  5. Writes the merged CSV

Usage
-----
  python collate.py \\
      --taaco  tool_outputs/taaco_results.csv \\
      --taales tool_outputs/taales_results.csv \\
      --taassc tool_outputs/taassc_results.csv \\
      --arte   tool_outputs/arte_results.csv \\
      --output output/merged_tool_features.csv

  # Any tool can be omitted if you only have some outputs so far:
  python collate.py --taaco tool_outputs/taaco.csv --output output/merged.csv
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

# Known modes — used to split filename key into volume_id + mode
_KNOWN_MODES = {"faithful", "simplified", "condensed", "interactive", "source"}


def _normalise_key(raw: str) -> str:
    """
    Normalise a filename to a join key.
    e.g.  'chapter1_faithful.txt'  →  'chapter1_faithful'
          'CHAPTER1_FAITHFUL.TXT'  →  'chapter1_faithful'
    """
    return Path(raw).stem.lower().strip()


def _parse_key(key: str) -> tuple[str, str]:
    """
    Split a normalised key into (volume_id, mode).
    e.g. 'chapter1_faithful' → ('chapter1', 'faithful')
         'my_doc_source'     → ('my_doc', 'source')
    """
    parts = key.rsplit("_", 1)
    if len(parts) == 2 and parts[1] in _KNOWN_MODES:
        return parts[0], parts[1]
    return key, "unknown"


def _load_tool_csv(path: Path, tool_name: str) -> "pd.DataFrame":
    """
    Load one tool CSV, normalise its filename column to '_key',
    and prefix all feature columns with the tool name to avoid collisions.
    """
    try:
        import pandas as pd
    except ImportError:
        logger.error("pandas is required. Run: pip install pandas")
        sys.exit(1)

    df = pd.read_csv(path, encoding="utf-8", low_memory=False)

    # Find the filename column — TAACO/TAALES/TAASSC/ARTE all use different names
    filename_col = None
    for col in df.columns:
        if col.lower() in {"filename", "file", "file name", "text", "input"}:
            filename_col = col
            break
    if filename_col is None:
        # Fall back: assume first column is the filename
        filename_col = df.columns[0]
        logger.warning("[%s] Could not detect filename column; using first column: '%s'",
                       tool_name, filename_col)

    df["_key"] = df[filename_col].astype(str).apply(_normalise_key)

    # Drop original filename column (it becomes redundant after join)
    df = df.drop(columns=[filename_col])

    # Prefix feature columns with tool name
    rename = {c: f"{tool_name}_{c}" for c in df.columns if c != "_key"}
    df = df.rename(columns=rename)

    logger.info("[%s] Loaded %d rows, %d feature columns from %s",
                tool_name, len(df), len(df.columns) - 1, path.name)
    return df


def collate(
    taaco: Path | None,
    taales: Path | None,
    taassc: Path | None,
    arte: Path | None,
    output: Path,
) -> None:
    try:
        import pandas as pd
    except ImportError:
        logger.error("pandas is required. Run: pip install pandas")
        sys.exit(1)

    tool_files = [
        ("taaco",  taaco),
        ("taales", taales),
        ("taassc", taassc),
        ("arte",   arte),
    ]
    provided = [(name, path) for name, path in tool_files if path is not None]

    if not provided:
        logger.error("No tool CSVs provided. Use at least one of --taaco, --taales, --taassc, --arte")
        sys.exit(1)

    dfs = [_load_tool_csv(path, name) for name, path in provided]

    # Outer join so rows are not dropped if a tool didn't process a file
    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on="_key", how="outer")

    # Decode _key → volume_id + mode and put them at the front
    parsed = merged["_key"].apply(_parse_key)
    merged.insert(0, "volume_id", parsed.apply(lambda t: t[0]))
    merged.insert(1, "mode",      parsed.apply(lambda t: t[1]))
    merged = merged.drop(columns=["_key"])

    output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output, index=False)
    logger.info(
        "Merged CSV written: %d rows × %d columns → %s",
        len(merged), len(merged.columns), output,
    )

    # Quick mode coverage report
    if "mode" in merged.columns:
        coverage = merged.groupby("mode").size().rename("n_files")
        logger.info("Files per mode:\n%s", coverage.to_string())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="collate",
        description="Merge TAACO / TAALES / TAASSC / ARTE CSV outputs into one file.",
    )
    parser.add_argument("--taaco",  type=Path, default=None, help="Path to TAACO output CSV.")
    parser.add_argument("--taales", type=Path, default=None, help="Path to TAALES output CSV.")
    parser.add_argument("--taassc", type=Path, default=None, help="Path to TAASSC output CSV.")
    parser.add_argument("--arte",   type=Path, default=None, help="Path to ARTE output CSV.")
    parser.add_argument(
        "--output", type=Path, default=Path("output/merged_tool_features.csv"),
        help="Output path for the merged CSV (default: output/merged_tool_features.csv).",
    )
    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    collate(
        taaco=args.taaco,
        taales=args.taales,
        taassc=args.taassc,
        arte=args.arte,
        output=args.output,
    )


if __name__ == "__main__":
    main()
