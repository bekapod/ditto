#include <gb/gb.h>
#include <gbdk/platform.h>

#include "input.h"
#include "main.h"
#include "sfx.h"

uint8_t state = STATE_TITLE_INIT;

void title_init(void) {
    state = STATE_TITLE;
}

void title_update(void) {
    if (input_pressed & J_START)
        state = STATE_PLAY_INIT;
}

void play_init(void) {
    state = STATE_PLAY;
}

void play_update(void) {
}

void main(void) {
    BGP_REG = 0xE4;
    OBP0_REG = 0xE4;
    OBP1_REG = 0x1B;

    sfx_init();
    add_VBL(sfx_tick);

    while (1) {
        vsync();
        input_update();

        switch (state) {
        case STATE_TITLE_INIT:
            title_init();
            break;
        case STATE_TITLE:
            title_update();
            break;
        case STATE_PLAY_INIT:
            play_init();
            break;
        case STATE_PLAY:
            play_update();
            break;
        }
    }
}
