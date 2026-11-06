"""
Bitmap fonts for PIL on MicroPython, which cannot render TrueType. One module per font and size, of bytes only,
so frozen it costs flash and no heap.

    python3 tools/make_fonts.py OUT_DIR SPEC.json FONTS_DIR [FONTS_DIR ...]

SPEC.json is {"Font-Name:size": chars}: the characters a program draws in that font and size, the font found in
a FONTS_DIR by its file name. Printable ASCII and a newline are added to each, except for the fonts listed under
"_icons", which get only their characters. Each glyph is its ink box at the baseline, as PIL's
getbbox(ch, anchor="ls") gives it, with 4-bit alpha. OUT_DIR is the package PIL.ImageFont.FONTS names.
"""
import json
import pathlib
import struct
import sys

from PIL import Image, ImageDraw, ImageFont  # Pillow, which renders the TrueType


def glyph(font, ch):
    x0, y0, x1, y1 = font.getbbox(ch, anchor="ls")
    w, h = max(x1 - x0, 0), max(y1 - y0, 0)
    packed = bytearray()
    if w and h:
        img = Image.new("L", (w, h), 0)
        ImageDraw.Draw(img).text((-x0, -y0), ch, fill=255, font=font, anchor="ls")
        px = img.tobytes()
        for row in range(h):
            line = [(px[row * w + i] * 15 + 127) // 255 for i in range(w)] + [0]
            packed += bytes((line[i] << 4) | line[i + 1] for i in range(0, w, 2))
    return int(round(font.getlength(ch))), x0, y0, w, h, bytes(packed)


def main():
    out, spec = pathlib.Path(sys.argv[1]), json.load(open(sys.argv[2]))
    paths = [p for d in sys.argv[3:] for p in pathlib.Path(d).iterdir() if p.suffix.lower() in (".ttf", ".otf")]
    icons = set(spec.pop("_icons", []))
    out.mkdir(parents=True, exist_ok=True)
    sizes = {}
    ascii_ = {chr(c) for c in range(32, 127)}
    total = 0
    for key, chars in sorted(spec.items()):
        name, size = key.rsplit(":", 1)
        path = next((p for p in paths if p.stem == name), None)
        if path is None:
            sys.exit("no font file for %s in %s" % (name, " ".join(sys.argv[3:])))
        font = ImageFont.truetype(str(path), int(size))
        # A newline is a glyph to PIL's single-line calls, .notdef's box and advance
        want = {c for c in chars if c >= " " or c == "\n"} | (set() if name in icons else ascii_ | {"\n"})
        chars_sorted = "".join(sorted(want))
        metrics, bitmaps = bytearray(), bytearray()
        for ch in chars_sorted:
            adv, x0, y0, w, h, bits = glyph(font, ch)
            metrics += struct.pack("<HhhBBI", adv, x0, y0, w, h, len(bitmaps))
            bitmaps += bits
        ascent, descent = font.getmetrics()
        mod = "f_%s_%s" % (name.replace("-", "_"), size)
        sizes.setdefault(name.replace("-", "_"), []).append(int(size))
        (out / (mod + ".py")).write_text(
            "# %s at %s, made by micropython-pil's tools/make_fonts.py\n" % (name, size) +
            "ASCENT = %d\nDESCENT = %d\nCHARS = %r\nMETRICS = %r\nBITMAPS = %r\n" % (
                ascent, descent, chars_sorted, bytes(metrics), bytes(bitmaps)))
        total += len(metrics) + len(bitmaps)
    # What ImageFont falls back on for a size not made: the nearest that was
    (out / "__init__.py").write_text("SIZES = %r\n" % {k: sorted(v) for k, v in sorted(sizes.items())})
    print("%d KB of glyphs" % (total // 1024))


main()
