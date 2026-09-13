#include <gb/gb.h>
#include <gbdk/platform.h>

#include "audio.h"
#include "pallet.h"

extern const hUGESong_t placeholder;
extern const uint8_t font_tiles[];

static const uint8_t empty_background[32 * 32] = {0};

#define FADE_FRAMES_PER_STEP 4
#define DITTO_SAVE_VERSION 1U

typedef struct {
    uint8_t version;
    uint16_t score;
} save_t;

static uint16_t run_seed;
static blink_state_t title_prompt;
static uint16_t score;
static save_t save_data;
static uint8_t run_seed_captured;
static uint8_t title_cursor = SPR_NONE;
static uint8_t play_block = SPR_NONE;

static void title_init(void);
static void title_update(void);
static void play_wait_update(void);
static void play_init(void);
static void play_update(void);
static void pause_init(void);
static void pause_update(void);
static void pause_exit(void);

static const state_t title_state = {
    title_init, title_update, 0, 0, 0
};
static const state_t play_wait_state = {
    0, play_wait_update, 0, 0, 0
};
static const state_t play_state = {
    play_init, play_update, 0, 0, 0
};
static const state_t pause_state = {
    pause_init, pause_update, 0, pause_exit, 1
};

static void title_init(void) {
    run_seed_captured = 0;
    DISPLAY_OFF;
    set_bkg_tiles(0, 0, 32, 32, empty_background);
    DISPLAY_ON;

    spr_reset();
    title_cursor = spr_alloc(1U);
    if (title_cursor != SPR_NONE) {
        spr_tile(title_cursor, TEXT_TILE_BASE + 39U);
        spr_prop(title_cursor, 0U);
        spr_move(title_cursor, 64U, 80U);
    }

    save_data.version = DITTO_SAVE_VERSION;
    if (!save_load(&save_data, sizeof(save_data)))
        save_data.version = DITTO_SAVE_VERSION;
    blink_init(&title_prompt);
    text_print(8, 8, "PUSH START");
}

static void title_update(void) {
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
        state_replace(&play_wait_state);
    }
}

static void play_wait_update(void) {
    if (!fade_active)
        state_replace(&play_state);
}

static void play_init(void) {
    uint8_t slot;
    static const uint8_t x[] = {64U, 72U, 64U, 72U};
    static const uint8_t y[] = {112U, 112U, 120U, 120U};

    spr_reset();
    play_block = spr_alloc(4U);
    if (play_block != SPR_NONE) {
        for (slot = 0; slot < 4U; slot++) {
            spr_tile((uint8_t)(play_block + slot), TEXT_TILE_BASE + 39U);
            spr_prop((uint8_t)(play_block + slot), 0U);
            spr_move((uint8_t)(play_block + slot), x[slot], y[slot]);
        }
    }

    score = save_data.score;
    DISPLAY_OFF;
    set_bkg_tiles(0, 0, 32, 32, empty_background);
    text_print(8, 8, "SCORE");
    text_digits(14, 8, score, 5);
    DISPLAY_ON;
    fade_in(FADE_FRAMES_PER_STEP);
}

static void pause_init(void) {
    text_print(8, 10, "PAUSED");
}

static void pause_update(void) {
    if (input_pressed & J_START)
        state_pop();
}

static void pause_exit(void) {
    text_print(8, 10, "      ");
}

static void play_flash(void) {
    flash(4);
}

static void play_shake(void) {
    shake(6, 2);
}

static void play_update(void) {
    if (fade_active)
        return;
    if (input_pressed & J_B) {
        state_replace(&title_state);
        return;
    }
    if (input_pressed & J_START) {
        state_push(&pause_state);
        return;
    }

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
    SHOW_SPRITES;
    DISPLAY_ON;

    sfx_init();
    add_VBL(pallet_vblank_tick);
    add_VBL(hUGE_dosound);
    music_play(&placeholder);
    state_push(&title_state);

    while (1) {
        input_update();
        state_tick();
        spr_hide_unused();
        seq_tick();
        vsync();
        bg_flush();
    }
}
