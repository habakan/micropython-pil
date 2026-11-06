/* Where _gfx.show() sends the band: a window, then its rows as big-endian RGB565, one call a row */
#ifndef GFX_DISPLAY_H
#define GFX_DISPLAY_H
#include <stddef.h>
#include <stdint.h>

void gfx_display_init(void);
void gfx_display_window(int x0, int y0, int x1, int y1); /* x1 and y1 exclusive */
void gfx_display_write(const uint8_t *data, size_t n);

#endif
