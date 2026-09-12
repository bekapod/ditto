#include <gb/gb.h>
#include <gbdk/platform.h>

#include "audio.h"
#include "fade.h"
#include "input.h"
#include "main.h"
#include "music.h"
#include "sfx.h"

extern const hUGESong_t placeholder;

#define FADE_FRAMES_PER_STEP 4

uint8_t state = STATE_TITLE_INIT;

void title_init(void) {
    state = STATE_TITLE;
}

void title_update(void) {
    if (input_pressed & J_A)
        audio_play_test_sfx();
    if (input_pressed & J_START) {
        fade_out(FADE_FRAMES_PER_STEP);
        state = STATE_PLAY_INIT;
    }
}

void play_init(void) {
    if (fade_active)
        return;

    fade_in(FADE_FRAMES_PER_STEP);
    state = STATE_PLAY_FADE_IN;
}

void play_fade_in(void) {
    if (!fade_active)
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
    add_VBL(fade_tick);
    add_VBL(hUGE_dosound);
    music_play(&placeholder);

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
        case STATE_PLAY_FADE_IN:
            play_fade_in();
            break;
        case STATE_PLAY:
            play_update();
            break;
        }
    }
}
