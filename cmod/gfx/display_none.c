/* No display, for MicroPython's unix port and tests: show() draws nowhere, save() still reads the band */
#include "display.h"

void gfx_display_init(void) {
}

void gfx_display_window(int x0, int y0, int x1, int y1) {
    (void)x0, (void)y0, (void)x1, (void)y1;
}

void gfx_display_write(const uint8_t *data, size_t n) {
    (void)data, (void)n;
}
