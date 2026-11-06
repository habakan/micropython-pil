"""Not in Pillow: sending an image to the display a band at a time, and the drawings only _gfx makes (QR codes,
the camera's frame), which cost no pixel buffer either."""
from PIL import Image, ImageDraw

_gfx = Image._gfx


def render(ops, x, y, size, each, region=None):
    """Draws `ops` at (x, y) over a size[0] x size[1] box on the screen, or only `region` of it (inclusive),
    band by band, calling each(x0, y0, x1, y1) with what each band holds."""
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(_gfx.WIDTH, x + size[0]), min(_gfx.HEIGHT, y + size[1])
    if region:
        x0, y0 = max(x0, x + region[0]), max(y0, y + region[1])
        x1, y1 = min(x1, x + region[2] + 1), min(y1, y + region[3] + 1)
    for by in range(y0, y1, _gfx.BAND):
        by1 = min(y1, by + _gfx.band(by))
        _gfx.fill(x0, by, x1, by1, 0)
        ImageDraw.replay(ops, x, y, (x0, by, x1, by1))
        each(x0, by, x1, by1)


def show(image, x=0, y=0, region=None):
    """Sends `image` to the display at (x, y): all of it, or only `region` (inclusive)."""
    render(image.snapshot(), x, y, image.size, _gfx.show, region)


SQUARES, DOTS, GAPPED = 1, 2, 3


def qr(data, width, height, border=3, style=SQUARES, fg=(0, 0, 0), bg=(255, 255, 255)):
    """A QR code of `data` (str or bytes) at level L in the smallest version, stretched over width x height."""
    out = Image.Image("RGBA", (width, height), None)
    out.ops.append(("qr", _gfx.qr_encode(data), border, 0, 0, width, height,
                    Image.c332(Image.rgba(fg)), Image.c332(Image.rgba(bg)), style))
    return out


def camera(side=None):
    """The middle square of the camera's last frame, in greys, as the board's camera_frame() gives it."""
    side = side or _gfx.HEIGHT
    out = Image.Image("RGB", (side, side), None)
    out.ops.append(("cam", None, side, side))
    return out
