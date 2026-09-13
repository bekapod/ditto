import helpers
import rom_adapter


LCDC = 0xFF40
WINDOW_TILE_MAP_9800 = 0x9800
WINDOW_TILE_MAP_9C00 = 0x9C00
TEXT_TILE_BASE = 1


def test_title_menu_labels_are_written_to_the_window_map(gb):
    pyboy = gb.pyboy

    pyboy.tick(1, render=False)
    window_map = (
        WINDOW_TILE_MAP_9C00
        if pyboy.memory[LCDC] & 0x40
        else WINDOW_TILE_MAP_9800
    )
    assert pyboy.memory[window_map + 1] == TEXT_TILE_BASE + 28  # S
    assert pyboy.memory[window_map + 32 + 1] == TEXT_TILE_BASE + 28  # S


def test_sound_test_uses_selected_menu_item(gb):
    pyboy = gb.pyboy
    calls = []
    rom_adapter.hook(pyboy, "audio_play_test_sfx", lambda _: calls.append(True))

    pyboy.button_press("left")
    pyboy.tick(1, render=False)
    pyboy.button_release("left")
    pyboy.tick(1, render=False)
    pyboy.button_press("a")
    pyboy.tick(1, render=False)
    pyboy.button_release("a")
    pyboy.tick(1, render=False)

    rom_adapter.unhook(pyboy, "audio_play_test_sfx")
    assert calls == [True]
    helpers.wait_for_callback(pyboy, "title_update")


def test_start_confirms_the_default_menu_item(gb):
    pyboy = gb.pyboy

    pyboy.button("start")
    helpers.wait_for_callback(pyboy, "play_update")
