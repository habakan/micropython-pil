"""
PNG images as the framebuffer's palette indices, one module of bytes each, for PIL.Image.open on MicroPython.
Alpha is dropped. OUT_DIR is the package PIL.Image.IMAGES names; an image is found by its path below IMG_DIR.

    python3 tools/make_images.py OUT_DIR IMG_DIR
"""
import importlib.util
import pathlib
import sys

from PIL import Image  # Pillow, which reads the PNG

# The palette as gfx.c has it, from the package's CPython stand-in (not importable as PIL beside Pillow)
_spec = importlib.util.spec_from_file_location("_gfx_sim", pathlib.Path(__file__).resolve().parents[1] / "PIL/_gfx_sim.py")
_sim = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sim)

out, src = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
(out / "__init__.py").write_text("")
for p in sorted(src.rglob("*.png")):
    img = Image.open(p).convert("RGB")
    px = img.tobytes()
    idx = bytes(_sim.colour(px[i], px[i + 1], px[i + 2]) for i in range(0, len(px), 3))
    name = "i_" + "_".join(p.relative_to(src).with_suffix("").parts).replace("-", "_")
    (out / (name + ".py")).write_text("W = %d\nH = %d\nPIXELS = %r\n" % (img.width, img.height, idx))
    print(name, img.size)
