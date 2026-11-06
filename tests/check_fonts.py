"""
The bitmap fonts' getbbox and getlength against Pillow's, on CPython: random ASCII strings in every font and
size made, in every anchor. Exits 1 on any difference.

    python3 tests/check_fonts.py FONTS_PACKAGE_DIR FONTS_DIR [FONTS_DIR ...]
"""
import importlib.util
import pathlib
import random
import sys

root = pathlib.Path(__file__).resolve().parents[1]
pkg = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(pkg.parent))
# Ours is loaded by path: on CPython, `PIL` is Pillow
spec = importlib.util.spec_from_file_location("ours_imagefont", root / "PIL/ImageFont.py")
ours = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ours)
ours.FONTS = pkg.name
from PIL import ImageFont  # noqa: E402

paths = {p.stem: str(p) for d in sys.argv[2:] for p in pathlib.Path(d).iterdir()}
made = __import__(pkg.name).SIZES
rnd = random.Random(1)
bad, n = [], 0
for mod_name, sizes in sorted(made.items()):
    name = next(k for k in paths if k.replace("-", "_") == mod_name)
    for size in sizes:
        a, b = ours.truetype(paths[name], size), ImageFont.truetype(paths[name], size)
        for _ in range(300):
            t = "".join(chr(rnd.randint(32, 126)) for _ in range(rnd.randint(1, 20)))
            anchor = rnd.choice(["ls", "la", "lt", "ms", "mt", "mm", "rm", "rs", None])
            n += 1
            if a.getbbox(t, anchor=anchor) != b.getbbox(t, anchor=anchor) or a.getlength(t) != b.getlength(t):
                bad.append((name, size, t, anchor, a.getbbox(t, anchor=anchor), b.getbbox(t, anchor=anchor)))
print("%d of %d agree" % (n - len(bad), n))
for x in bad[:15]:
    print(x)
sys.exit(1 if bad else 0)
