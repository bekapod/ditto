#include <gb/gb.h>
#include <gbdk/platform.h>

#include "audio.h"
#include "debug_math.h"
#include "pallet.h"

extern const hUGESong_t placeholder;
extern const uint8_t font_tiles[];

static const uint8_t empty_background[32 * 32] = {0};
static uint8_t scroll_columns[32][18];

#define FADE_FRAMES_PER_STEP 4
#define SCROLL_SPEED_SLOW 0x0100U
#define SCROLL_SPEED_FAST 0x0180U
#define HUD_SCORE_SPRITE_COUNT 10U
#define HUD_SCORE_X 88U
#define HUD_SCORE_Y 16U
#define PAUSE_HUD_SPRITE_COUNT 6U
#define PAUSE_HUD_X 56U
#define PAUSE_HUD_Y 80U
#define DITTO_SAVE_VERSION 1U

typedef struct {
    uint16_t score;
} save_t;

static uint16_t run_seed;
static uint16_t score;
static save_t save_data;
static uint8_t run_seed_captured;
static uint8_t load_saved_score = 1U;
static uint8_t score_hud = SPR_NONE;
static uint8_t pause_hud = SPR_NONE;
static const menu_item_t title_items[] = {
    {"START", 0},
    {"SOUND TEST", 0},
};
static const char score_label[] = "SCORE";
static const char pause_label[] = "PAUSED";
static uint16_t play_scroll_speed;

static void play_scroll_column(uint8_t map_col, uint8_t world_col) {
    uint8_t row;

    for (row = 0; row < 18U; row++)
        scroll_columns[map_col][row] =
            (uint8_t)(TEXT_TILE_BASE + ((world_col + row) & 3U));
    bg_put_col(map_col, 0U, scroll_columns[map_col], 18U);
}

static void draw_pause_hud(void) {
    uint8_t index;

    if (pause_hud == SPR_NONE)
        return;
    for (index = 0; index < PAUSE_HUD_SPRITE_COUNT; index++) {
        spr_tile((uint8_t)(pause_hud + index), text_sprite_tile(pause_label[index]));
        spr_move((uint8_t)(pause_hud + index),
                 (uint8_t)(PAUSE_HUD_X + index * 8U), PAUSE_HUD_Y);
    }
}

static void draw_score_hud(void) {
    uint8_t index;
    uint16_t value = score;

    if (score_hud == SPR_NONE)
        return;
    for (index = 0; index < 5U; index++) {
        spr_tile((uint8_t)(score_hud + index), text_sprite_tile(score_label[index]));
        spr_move((uint8_t)(score_hud + index),
                 (uint8_t)(HUD_SCORE_X + index * 8U), HUD_SCORE_Y);
    }
    for (index = 5U; index; index--) {
        uint8_t slot = (uint8_t)(score_hud + index + 4U);

        spr_tile(slot, text_sprite_tile((char)('0' + value % 10U)));
        spr_move(slot, (uint8_t)(HUD_SCORE_X + (index + 4U) * 8U),
                 HUD_SCORE_Y);
        value /= 10U;
    }
}

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
    scroll_set_on_column(0);
    scroll_reset(0);
    DISPLAY_OFF;
    while (bg_pending())
        bg_flush();
    set_bkg_tiles(0, 0, 32, 32, empty_background);
    DISPLAY_ON;

    menu_close();
    spr_reset();
    menu_open(title_items, 2U, 8U, 8U);

    load_saved_score =
        save_load(DITTO_SAVE_VERSION, &save_data, sizeof(save_data)) == SAVE_OK;
}

static void title_start(void) {
    if (run_seed_captured)
        return;
    run_seed = sys_time;
    rng_init(&rng_global, run_seed);
    run_seed_captured = 1;
    menu_close();
    fade_out(FADE_FRAMES_PER_STEP);
    state_replace(&play_wait_state);
}

static void title_update(void) {
    menu_event_t event = menu_tick();

    if (event.action == MENU_CANCEL) {
        menu_open(title_items, 2U, 8U, 8U);
        return;
    }
    if (event.action != MENU_CONFIRM && !(input_pressed(J_START)))
        return;
    if (menu_selected() == 0U)
        title_start();
    else
        audio_play_test_sfx();
}

static void play_wait_update(void) {
    if (!fade_active)
        state_replace(&play_state);
}

static void play_init(void) {
    DISPLAY_OFF;
    while (bg_pending())
        bg_flush();
    set_bkg_tiles(0, 0, 32, 32, empty_background);
    scroll_set_on_column(play_scroll_column);
    play_scroll_speed = SCROLL_SPEED_SLOW;
    scroll_set_speed(play_scroll_speed);
    scroll_reset(0);
    while (bg_pending())
        bg_flush();

    spr_reset();
    pause_hud = SPR_NONE;
    score = load_saved_score ? save_data.score : 0;
    load_saved_score = 0;
    score_hud = spr_alloc(HUD_SCORE_SPRITE_COUNT);
    draw_score_hud();
    DISPLAY_ON;
    fade_in(FADE_FRAMES_PER_STEP);
}

static void pause_init(void) {
    scroll_pause();
    pause_hud = spr_alloc(PAUSE_HUD_SPRITE_COUNT);
    draw_pause_hud();
}

static void pause_update(void) {
    if (input_pressed(J_START))
        state_pop();
}

static void pause_exit(void) {
    spr_free(pause_hud, PAUSE_HUD_SPRITE_COUNT);
    pause_hud = SPR_NONE;
    scroll_resume();
}

static void play_flash(void) {
    flash(4);
}

static void play_shake(void) {
    camera_shake(6, 2);
}

static void play_update(void) {
    if (fade_active)
        return;
    if (input_pressed(J_B)) {
        state_replace(&title_state);
        return;
    }
    if (input_pressed(J_START)) {
        state_push(&pause_state);
        return;
    }

    if (input_pressed(J_SELECT)) {
        play_scroll_speed = play_scroll_speed == SCROLL_SPEED_SLOW
                                ? SCROLL_SPEED_FAST
                                : SCROLL_SPEED_SLOW;
        scroll_set_speed(play_scroll_speed);
    }
    scroll_tick();

    if (seq_busy())
        return;

    score++;
    draw_score_hud();
    save_data.score = score;
    save_write(DITTO_SAVE_VERSION, &save_data, sizeof(save_data));
    if (input_pressed(J_A)) {
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
    debug_math_cases();

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
        text_vblank();
        bg_flush();
    }
}
