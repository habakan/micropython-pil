# _gfx for CMake ports (rp2, esp32): set GFX_DISPLAY (st7789_rp2 by default, or none) and, for st7789_rp2,
# GFX_BOARD_DIR to the directory holding the board's board_pins.h
add_library(usermod_gfx INTERFACE)
if(NOT DEFINED GFX_DISPLAY)
    set(GFX_DISPLAY st7789_rp2)
endif()
target_sources(usermod_gfx INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/gfx.c ${CMAKE_CURRENT_LIST_DIR}/qrcodegen.c ${CMAKE_CURRENT_LIST_DIR}/display_${GFX_DISPLAY}.c)
target_include_directories(usermod_gfx INTERFACE ${CMAKE_CURRENT_LIST_DIR} ${GFX_BOARD_DIR})
if(GFX_DISPLAY STREQUAL "st7789_rp2")
    target_link_libraries(usermod_gfx INTERFACE hardware_spi hardware_gpio)
endif()
target_link_libraries(usermod INTERFACE usermod_gfx)
