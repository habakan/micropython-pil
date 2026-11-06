import os
import pathlib
import subprocess
import sys

import pytest

from PIL import Image, ImageDisplay, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_colours():
    assert Image.rgba("#ff8000") == (255, 128, 0, 255)
    assert Image.rgba("#f80") == (255, 136, 0, 255)
    assert Image.rgba("white") == (255, 255, 255, 255)
    assert Image.rgba(0x0000FF) == (255, 0, 0, 255)  # PIL's ints are 0xBBGGRR


def test_an_opaque_paint_drops_what_it_hides():
    im = Image.new("RGB", (240, 240))
    d = ImageDraw.Draw(im)
    for i in range(50):
        d.rectangle((10, 10, 50, 50), fill=(i, 0, 0))
    assert len(im.ops) <= 3  # the background and the last square, not fifty squares


def test_whole_image_paint_replaces_everything():
    im = Image.new("RGB", (240, 240))
    for _ in range(20):
        im.paste(Image.new("RGB", (240, 240), "red"), (0, 0))
    assert len(im.ops) == 1


def test_crop_and_paste_keep_ops_not_pixels():
    im = Image.new("RGB", (240, 240), "blue")
    part = im.crop((0, 0, 100, 100))
    assert part.size == (100, 100) and all(op[0] != "pix" for op in part.ops)


def test_qr_draws_without_a_buffer():
    code = ImageDisplay.qr("hello", 120, 120)
    assert code.ops[0][0] == "qr" and code.size == (120, 120)


def test_scene_matches_micropython():
    mp = os.environ.get("MICROPYTHON")
    if not mp:
        pytest.skip("set MICROPYTHON to a unix build with cmod/gfx (make unix)")
    env = dict(os.environ, PYTHONPATH="%s:%s" % (ROOT, ROOT / "build"), MICROPYPATH="%s:%s" % (ROOT, ROOT / "build"))
    py = subprocess.run([sys.executable, str(ROOT / "tests/scene.py")], env=env, capture_output=True, text=True, check=True)
    mpy = subprocess.run([mp, str(ROOT / "tests/scene.py")], env=env, capture_output=True, text=True, check=True)
    assert py.stdout == mpy.stdout and py.stdout.startswith("text")
