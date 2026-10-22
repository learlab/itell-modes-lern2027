"""
run_taaco.py
------------
Run TAACO programmatically on a directory of .txt files using the
TAACOnoGUI Python API (https://github.com/LCR-ADS-Lab/TAACO).

No Wine or Windows machine needed — TAACO's Python 3 version runs on Mac.

Setup (one time)
----------------
  git clone https://github.com/LCR-ADS-Lab/TAACO.git
  pip install spacy
  python -m spacy download en_core_web_sm

Usage
-----
  python run_taaco.py \\
      --taaco-dir path/to/TAACO \\
      --input-dir txt/ \\
      --output output/taaco_results.csv
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# All indices enabled — mirrors running TAACO with every checkbox ticked.
# Set any to False to skip that index family.
TAACO_OPTIONS = {
    "sourceKeyOverlap": False,
    "sourceLSA":        False,
    "sourceLDA":        False,
    "sourceWord2vec":   False,
    "wordsAll":         True,
    "wordsContent":     True,
    "wordsFunction":    True,
    "wordsNoun":        True,
    "wordsPronoun":     True,
    "wordsArgument":    True,
    "wordsVerb":        True,
    "wordsAdjective":   True,
    "wordsAdverb":      True,
    "overlapSentence":  True,
    "overlapParagraph": True,
    "overlapAdjacent":  True,
    "overlapAdjacent2": True,
    "otherTTR":         True,
    "otherConnectives": True,
    "otherGivenness":   True,
    "overlapLSA":       True,
    "overlapLDA":       True,
    "overlapWord2vec":  True,
    "overlapSynonym":   True,
    "overlapNgrams":    True,
    "outputTagged":     False,
    "outputDiagnostic": False,
}


def run(taaco_dir: Path, input_dir: Path, output: Path) -> None:
    # Add TAACO repo to path so TAACOnoGUI can be imported
    sys.path.insert(0, str(taaco_dir))
    try:
        from TAACOnoGUI import runTAACO
    except ImportError:
        logger.error(
            "Could not import TAACOnoGUI from %s\n"
            "Make sure you cloned https://github.com/LCR-ADS-Lab/TAACO "
            "and passed its directory with --taaco-dir",
            taaco_dir,
        )
        sys.exit(1)

    txt_files = list(input_dir.glob("*.txt"))
    if not txt_files:
        logger.error("No .txt files found in %s", input_dir)
        sys.exit(1)

    logger.info("Running TAACO on %d files in %s", len(txt_files), input_dir)
    output.parent.mkdir(parents=True, exist_ok=True)

    # runTAACO expects a trailing slash on the input directory
    runTAACO(
        str(input_dir).rstrip("/") + "/",
        str(output),
        TAACO_OPTIONS,
        gui=False,
        source_text=False,
    )

    logger.info("TAACO output written to %s", output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_taaco",
        description="Run TAACO on a directory of .txt files (no Windows needed).",
    )
    parser.add_argument(
        "--taaco-dir", type=Path, required=True,
        help="Path to the cloned TAACO repository (contains TAACOnoGUI.py).",
    )
    parser.add_argument(
        "--input-dir", type=Path, required=True,
        help="Directory of .txt files to analyse.",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("output/taaco_results.csv"),
        help="Output CSV path (default: output/taaco_results.csv).",
    )
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    run(args.taaco_dir, args.input_dir, args.output)


if __name__ == "__main__":
    main()
