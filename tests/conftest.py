import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
# This package, not Pillow, as `PIL`; build/ holds the fonts tests/fonts.json makes
sys.path[:0] = [str(ROOT), str(ROOT / "build")]
