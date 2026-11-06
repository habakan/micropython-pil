# micropython-pil

A subset of Pillow's drawing API (`Image`, `ImageDraw`, `ImageFont`) for MicroPython on microcontrollers
with a few hundred KB of RAM, made to run [SeedSigner](https://github.com/SeedSigner/seedsigner)'s screens on
a Raspberry Pi Pico 2 (RP2350, 520 KB of RAM, no PSRAM). It is not a SeedSigner project.

**The subset is what SeedSigner's screens use**, no more. Code written for Pillow on CPython runs with
`from PIL import ...` unchanged as long as it stays inside the list below. Anything that needs pixels is out
of scope by design (see "What does not, and why"); please don't expect it to grow towards full Pillow.

## How it fits in a small RAM

**An image holds drawing operations, not pixels.** `ImageDraw` calls append operations to the image;
`paste`, `crop` and `resize` copy or scale them. Nothing allocates a pixel buffer on the heap, the screen
included. An opaque paint drops the operations it hides, so a screen redrawn many times does not pile up.

**The screen is drawn a band of rows at a time.** `ImageDisplay.show(image)` replays the operations into
the C module's band (240 x 40 pixels, one byte each, outside the heap) and sends each band to the display
before drawing the next. The palette is a 6x6x6 colour cube and 40 greys.

**Fonts and images are bytes in flash.** MicroPython cannot render TrueType. `tools/make_fonts.py` renders
the characters a program uses, at the sizes it uses, into Python modules of bytes; `tools/make_images.py`
does the same for PNG images. Frozen into the firmware, they cost flash and no heap.

The rule for anything added: **no pixel buffer on the heap.** Work on pixels belongs in the C module, on the
band.

## What works

| Module | Supported |
|---|---|
| `Image` | `new`, `open` (images made by `make_images.py`), `paste` (images or a colour), `crop`, `copy`, `resize` (scales the drawing), `convert`, `alpha_composite`, `size`, `width`, `height`; RGB, RGBA (a translucent fill shades what it is pasted over), L and 1 |
| `ImageDraw` | `rectangle`, `rounded_rectangle`, `ellipse`, `line`, `polygon`, `arc`, `text`, `textbbox`, `textlength` |
| `ImageFont` | `truetype` (the bitmaps `make_fonts.py` made; the nearest size made if the size asked for was not), `getbbox`, `getlength`, `getmetrics`, PIL's basic layout (no kerning) |
| `ImageColor` | `getrgb` |
| `ImageDisplay` (not in Pillow) | `show`, `render`, `qr` (QR codes drawn by the C module), `camera` (the board's camera frame) |

`getbbox` and `getlength` give what Pillow gives for the same font file: `make check-fonts` compares them.

## What does not, and why

These need pixels, so they are stubs or absent:

- `rotate` (only by multiples of 360), `filter` and `ImageOps` return the image unchanged; `putalpha` does
  nothing.
- `getpixel`, `putpixel`, `point`, `tobytes`, `frombytes`, `save`: a 240 x 240 RGB image would be 172 KB,
  more than such a device's heap. A pixel-by-pixel loop of operations would run out of memory too.
- `Image.open` of PNG or JPEG files at run time: convert them with `make_images.py` instead.
- `ImageFont.truetype` with characters or sizes that were not made: make them with `make_fonts.py`.
- Complex text layout (libraqm), kerning, and scripts that need shaping.

## Layout

| Path | What |
|---|---|
| `PIL/` | the Python package; `PIL/_gfx_sim.py` is the C module in Python, so it runs and tests on CPython |
| `cmod/gfx/` | the C module `_gfx`: the band, the palette, glyphs, shapes, QR codes (`gfx.c`) and a display backend (`display.h`) |
| `tools/` | `make_fonts.py`, `make_images.py` (run on CPython with Pillow) |
| `tests/` | pytest, and a scene drawn by both CPython and MicroPython that must come out byte for byte the same |

## Building it into firmware

Add `cmod` to `USER_C_MODULES`. For CMake ports set `GFX_DISPLAY`:

- `st7789_rp2` (the default): a 240 x 240 ST7789 on an RP2040/RP2350's SPI. Set `GFX_BOARD_DIR` to a
  directory with your `board_pins.h` (`PIN_LCD_RES`, `PIN_LCD_DC`, `PIN_LCD_SCK`, `PIN_LCD_MOSI`, and
  `LCD_FLIP` for a panel mounted upside down).
- `none`: no display. Make ports (unix) use this.

Another display needs a `display_<name>.c` with the three functions in `display.h`. The canvas size and band
height are `GFX_WIDTH`, `GFX_HEIGHT` and `GFX_BAND` (240, 240, 40). A camera driver may define
`const uint8_t *camera_frame(void)`, returning its last greyscale frame (`GFX_CAMERA_W` x `GFX_CAMERA_H`,
320 x 240), for `ImageDisplay.camera`.

Freeze `PIL/` and the packages the tools wrote. Their names are `ImageFont.FONTS` (`pil_fonts`) and
`Image.IMAGES` (`pil_images`); change those to use others.

## Tests

```sh
make fonts FONTS_DIR=<dir with OpenSans-Regular.ttf and OpenSans-SemiBold.ttf>
make unix MPY_DIR=<micropython checkout>
make test MICROPYTHON=build/unix/micropython
make check-fonts FONTS_DIR=<same dir>
```

The tests need Pillow, `qrcodegen` and pytest on CPython.
