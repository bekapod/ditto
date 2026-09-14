/* Example: save — loading on boot and writing during play.
 *
 * Build with `make example-save` (ROM: build/ditto-save.gb).
 * Demonstrates save_load()/save_write() with an explicit schema version:
 * the title loads the saved score, play increments it and writes it back
 * every frame so it survives a power cycle.
 */
#include <gb/gb.h>
#include <gbdk/platform.h>

#include "pallet.h"

extern const uint8_t font_tiles[];

static const uint8_t empty_background[32 * 32] = {0};

#define DITTO_SAVE_VERSION 1U

typedef struct {
    uint16_t score;
} save_t;

static save_t save_data;
static uint16_t score;
static uint8_t load_saved_score = 1U;

static void title_init(void);
static void title_update(void);
static void play_init(void);
static void play_update(void);

static const state_t title_state = {title_init, title_update, 0, 0, 0};
static const state_t play_state = {play_init, play_update, 0, 0, 0};

static void title_init(void) {
    DISPLAY_OFF;
    while (bg_pending())
        bg_flush();
    set_bkg_tiles(0, 0, 32, 32, empty_background);
    DISPLAY_ON;

    load_saved_score =
        save_load(DITTO_SAVE_VERSION, &save_data, sizeof(save_data)) == SAVE_OK;
    text_print(4U, 8U, "PRESS START");
}

static void title_update(void) {
    if (input_pressed(J_START))
        (void)state_replace_faded(&play_state, 4U);
}

static void play_init(void) {
    DISPLAY_OFF;
    while (bg_pending())
        bg_flush();
    set_bkg_tiles(0, 0, 32, 32, empty_background);
    DISPLAY_ON;

    score = load_saved_score ? save_data.score : 0U;
    load_saved_score = 0U;
    text_print(8U, 8U, "SCORE");
    text_digits(8U, 10U, score, 5U);
}

static void play_update(void) {
    if (input_pressed(J_B)) {
        (void)state_replace_faded(&title_state, 4U);
        return;
    }
    score++;
    text_digits(8U, 10U, score, 5U);
    save_data.score = score;
    (void)save_write(DITTO_SAVE_VERSION, &save_data, sizeof(save_data));
}

static const pallet_game_t ditto_game = {&title_state, 0, 0};

void main(void) {
    BGP_REG = 0xE4;
    OBP0_REG = 0xE4;
    OBP1_REG = 0x1B;

    text_init(font_tiles);
    set_bkg_tiles(0, 0, 32, 32, empty_background);
    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;

    pallet_run(&ditto_game);
}
