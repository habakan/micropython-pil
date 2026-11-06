/* A 240x240 ST7789 on an RP2040/RP2350's SPI, with CS tied low (so SPI mode 3) and an IPS panel. The board's
 * board_pins.h names PIN_LCD_RES, PIN_LCD_DC, PIN_LCD_SCK, PIN_LCD_MOSI and LCD_FLIP */
#include "display.h"
#include "board_pins.h"
#include "hardware/gpio.h"
#include "hardware/spi.h"
#include "pico/time.h"

#ifndef GFX_LCD_SPI
#define GFX_LCD_SPI spi0
#endif
/* Modest for jumper leads; the ST7789 takes up to 62.5 MHz */
#ifndef GFX_LCD_BAUD
#define GFX_LCD_BAUD (40 * 1000 * 1000)
#endif
#ifndef LCD_FLIP
#define LCD_FLIP 0
#endif

static void cmd(uint8_t c, const uint8_t *data, unsigned int n) {
    gpio_put(PIN_LCD_DC, 0);
    spi_write_blocking(GFX_LCD_SPI, &c, 1);
    gpio_put(PIN_LCD_DC, 1);
    if (n) spi_write_blocking(GFX_LCD_SPI, data, n);
}

/* With CS low, noise on SCK while the MCU resets shifts the LCD's bit count until it is reset too, which RES does */
void gfx_display_init(void) {
    static const uint8_t colmod = 0x55, madctl = LCD_FLIP ? 0xd0 : 0x00; /* MY|MX, and ML so the refresh runs the way rows are written */
    gpio_init(PIN_LCD_RES);
    gpio_set_dir(PIN_LCD_RES, GPIO_OUT);
    gpio_put(PIN_LCD_RES, 0);
    sleep_ms(10);
    gpio_put(PIN_LCD_RES, 1);
    sleep_ms(120);
    spi_init(GFX_LCD_SPI, GFX_LCD_BAUD);
    spi_set_format(GFX_LCD_SPI, 8, SPI_CPOL_1, SPI_CPHA_1, SPI_MSB_FIRST);
    gpio_set_function(PIN_LCD_SCK, GPIO_FUNC_SPI);
    gpio_set_function(PIN_LCD_MOSI, GPIO_FUNC_SPI);
    gpio_init(PIN_LCD_DC);
    gpio_set_dir(PIN_LCD_DC, GPIO_OUT);
    cmd(0x01, NULL, 0);
    sleep_ms(150);
    cmd(0x11, NULL, 0);
    sleep_ms(120);
    cmd(0x3a, &colmod, 1);
    cmd(0x36, &madctl, 1);
    cmd(0x21, NULL, 0);
    cmd(0x13, NULL, 0);
    cmd(0x29, NULL, 0);
}

void gfx_display_window(int x0, int y0, int x1, int y1) {
    /* flipped, the 240 visible rows are the last of the controller's 320 */
    int r0 = y0 + (LCD_FLIP ? 80 : 0), r1 = y1 - 1 + (LCD_FLIP ? 80 : 0);
    uint8_t caset[4] = {0, (uint8_t)x0, 0, (uint8_t)(x1 - 1)};
    uint8_t raset[4] = {(uint8_t)(r0 >> 8), (uint8_t)r0, (uint8_t)(r1 >> 8), (uint8_t)r1};
    cmd(0x2a, caset, 4);
    cmd(0x2b, raset, 4);
    cmd(0x2c, NULL, 0);
}

void gfx_display_write(const uint8_t *data, size_t n) {
    spi_write_blocking(GFX_LCD_SPI, data, n);
}
