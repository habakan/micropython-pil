# _gfx for make ports (unix): no display, for tests
GFX_MOD_DIR := $(USERMOD_DIR)
SRC_USERMOD_C += $(GFX_MOD_DIR)/gfx.c $(GFX_MOD_DIR)/qrcodegen.c $(GFX_MOD_DIR)/display_none.c
CFLAGS_USERMOD += -I$(GFX_MOD_DIR)
