"""One screen of every drawing PIL here makes, rendered band by band; prints a digest of each band as
_gfx.save gives it. Run by CPython (PIL/_gfx_sim.py) and by MicroPython (cmod/gfx), which must agree."""
import sys

from PIL import Image, ImageDisplay, ImageDraw

try:
    from PIL import ImageFont
    font = ImageFont.truetype("OpenSans-Regular.ttf", 20)
    small = ImageFont.truetype("OpenSans-SemiBold.ttf", 17)
except (ImportError, OSError):  # no fonts made: tests/fonts.json and make fonts
    font = small = None

im = Image.new("RGB", (240, 240), "#202020")
d = ImageDraw.Draw(im)
d.rectangle((4, 4, 235, 40), fill="orange", outline="white", width=2)
d.rounded_rectangle((10, 50, 120, 100), radius=12, fill=(30, 90, 200), outline=(255, 255, 255), width=3)
d.ellipse((130, 50, 230, 110), fill="green", outline="yellow", width=4)
d.line([(0, 239), (120, 120), (239, 239)], fill="red", width=3)
d.polygon([(20, 200), (60, 140), (100, 200)], fill=(200, 0, 200), outline="white")
d.arc((140, 130, 220, 210), 30, 300, fill="white", width=5)
if font:
    d.text((120, 22), "Pico 2: PIL", fill="black", font=font, anchor="mm")
    d.text((12, 108), "abc xyz 0123", fill="white", font=small)
code = ImageDisplay.qr("micropython-pil", 90, 90, border=2, style=ImageDisplay.DOTS)
im.paste(code, (140, 140))
part = im.crop((10, 50, 120, 100)).resize((55, 25))
im.paste(part, (175, 5))
shade = Image.new("RGBA", (240, 60), (0, 0, 0, 128))
im.paste(shade, (0, 180))


def digest(b):
    h = 0
    for v in b:
        h = (h * 131 + v) & 0xFFFFFFFF
    return h


out = []
ImageDisplay.render(im.snapshot(), 0, 0, im.size,
                    lambda x0, y0, x1, y1: out.append(digest(Image._gfx.save(x0, y0, x1, y1))))
print("text" if font else "notext", " ".join("%08x" % h for h in out))
sys.exit(0)
