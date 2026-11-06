# micropython-pil: PIL's drawing API for MicroPython (README.md)
MPY_DIR ?=
FONTS_DIR ?=
PYTHON ?= python3
BUILD := build

help:
	@echo "make fonts FONTS_DIR=<dir with OpenSans-Regular.ttf and OpenSans-SemiBold.ttf>   the fonts the tests draw"
	@echo "make unix MPY_DIR=<micropython checkout>   MicroPython's unix port with _gfx, for the tests"
	@echo "make test [MICROPYTHON=build/unix/micropython]   pytest, and the C module against PIL/_gfx_sim.py"
	@echo "make check-fonts FONTS_DIR=...   the bitmap fonts' metrics against Pillow's"

fonts:
	@test -n "$(FONTS_DIR)" || { echo "set FONTS_DIR"; exit 1; }
	$(PYTHON) tools/make_fonts.py $(BUILD)/pil_fonts tests/fonts.json $(FONTS_DIR)

unix:
	@test -n "$(MPY_DIR)" || { echo "set MPY_DIR to a micropython checkout"; exit 1; }
	$(MAKE) -C $(MPY_DIR)/ports/unix -j8 BUILD=$(abspath $(BUILD)/unix) PROG=micropython USER_C_MODULES=$(abspath cmod)

test:
	MICROPYTHON=$(MICROPYTHON) $(PYTHON) -m pytest -q tests

check-fonts:
	$(PYTHON) tests/check_fonts.py $(BUILD)/pil_fonts $(FONTS_DIR)

.PHONY: help fonts unix test check-fonts
