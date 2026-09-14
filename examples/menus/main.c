/* Example: menus — a title menu with items, selection, and a cursor.
 *
 * Build with `make example-menus` (ROM: build/ditto-menus.gb).
 * Demonstrates menu_item_t descriptors, menu_event_t handling, and the
 * menu cursor sprite. B returns from play to the title.
 */
#include <gb/gb.h>
#include <gbdk/platform.h>

#include "audio.h"
#include "pallet.h"

extern const uint8_t font_tiles[];

static const uint8_t empty_background[32 * 32] = {0};

static const menu_item_t title_items[] = {
    {"START", 0},
    {"SOUND TEST", 0},
};

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

    menu_close();
    spr_reset();
    menu_open(title_items, 2U, 8U, 8U);
}

static void title_update(void) {
    menu_event_t event = menu_tick();

    if (event.action == MENU_CANCEL) {
        menu_open(title_items, 2U, 8U, 8U);
        return;
    }
    if (event.action != MENU_CONFIRM && !input_pressed(J_START))
        return;
    if (menu_selected() == 0U)
        (void)state_replace_faded(&play_state, 4U);
    else
        audio_play_test_sfx();
}

static void play_init(void) {
    /* The title menu owns the window and cursor; close both before play
     * renders its own background. */
    menu_close();
    DISPLAY_OFF;
    while (bg_pending())
        bg_flush();
    set_bkg_tiles(0, 0, 32, 32, empty_background);
    DISPLAY_ON;
    text_print(6U, 8U, "IT WORKS!");
}

static void play_update(void) {
    if (input_pressed(J_B))
        (void)state_replace_faded(&title_state, 4U);
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
