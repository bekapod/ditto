#include <gb/gb.h>
#include <gbdk/platform.h>

#include "audio.h"
#include "bg.h"
#include "blink.h"
#include "fade.h"
#include "flash.h"
#include "input.h"
#include "main.h"
#include "music.h"
#include "rng.h"
#include "save.h"
#include "seq.h"
#include "shake.h"
#include "sfx.h"
#include "text.h"
#include "vblank.h"

extern const hUGESong_t placeholder;
extern const uint8_t font_tiles[];

static const uint8_t empty_background[32 * 32] = {0};

#define FADE_FRAMES_PER_STEP 4

uint8_t state = STATE_TITLE_INIT;
uint16_t run_seed;
static blink_state_t title_prompt;
static uint16_t score;
static save_t save_data;
static uint8_t run_seed_captured;

void title_init(void) {
    save_data.version = DITTO_SAVE_VERSION;
    if (!save_load(&save_data, sizeof(save_data)))
        save_data.version = DITTO_SAVE_VERSION;
    blink_init(&title_prompt);
    text_print(8, 8, "PUSH START");
    state = STATE_TITLE;
}

void title_update(void) {
    blink_tick(&title_prompt);
    if (title_prompt.dirty) {
        text_print(8, 8, title_prompt.visible ? "PUSH START" : "          ");
        title_prompt.dirty = 0;
    }

    if (input_pressed & J_A)
        audio_play_test_sfx();
    if ((input_pressed & J_START) && !run_seed_captured) {
        run_seed = sys_time;
        rng_init(&rng_global, run_seed);
        run_seed_captured = 1;
        fade_out(FADE_FRAMES_PER_STEP);
        state = STATE_PLAY_INIT;
    }
}

void play_init(void) {
    if (fade_active)
        return;

    score = save_data.score;
    DISPLAY_OFF;
    set_bkg_tiles(0, 0, 32, 32, empty_background);
    text_print(8, 8, "SCORE");
    text_digits(14, 8, score, 5);
    DISPLAY_ON;
    fade_in(FADE_FRAMES_PER_STEP);
    state = STATE_PLAY_FADE_IN;
}

void play_fade_in(void) {
    if (!fade_active)
        state = STATE_PLAY;
}

static void play_flash(void) {
    flash(4);
}

static void play_shake(void) {
    shake(6, 2);
}

void play_update(void) {
    if (seq_busy())
        return;

    score++;
    text_digits(14, 8, score, 5);
    save_data.score = score;
    save_write(&save_data, sizeof(save_data));
    if (input_pressed & J_A) {
        seq_push(play_flash, 4);
        seq_push(play_shake, 6);
        seq_push(0, 10);
        seq_push(audio_play_test_sfx, 0);
    }
}

void main(void) {
    BGP_REG = 0xE4;
    OBP0_REG = 0xE4;
    OBP1_REG = 0x1B;

    text_init(font_tiles);
    set_bkg_tiles(0, 0, 32, 32, empty_background);
    SHOW_BKG;
    DISPLAY_ON;

    sfx_init();
    add_VBL(pallet_vblank_tick);
    add_VBL(hUGE_dosound);
    music_play(&placeholder);

    while (1) {
        vsync();
        bg_flush();
        input_update();
        seq_tick();
        text_vblank();

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
