/* Example: audio — placeholder music at boot plus a scripted SFX.
 *
 * Build with `make example-audio` (ROM: build/ditto-audio.gb).
 * Demonstrates the pallet_game_t music field and a sequence that plays
 * the test SFX after a flash and a shake: press A in play.
 */
#include <gb/gb.h>
#include <gbdk/platform.h>

#include "audio.h"
#include "pallet.h"

extern const hUGESong_t placeholder;
extern const uint8_t font_tiles[];

static const uint8_t empty_background[32 * 32] = {0};

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
    text_print(2U, 8U, "PRESS A FOR SFX");
}

static void play_flash(void) {
    flash(4);
}

static void play_shake(void) {
    camera_shake(6, 2);
}

static void play_update(void) {
    if (input_pressed(J_B)) {
        (void)state_replace_faded(&title_state, 4U);
        return;
    }
    if (seq_busy() || !input_pressed(J_A))
        return;
    seq_push(play_flash, 4);
    seq_push(play_shake, 6);
    seq_push(0, 10);
    seq_push(audio_play_test_sfx, 0);
}

static const pallet_game_t ditto_game = {&title_state, &placeholder, 0};

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
