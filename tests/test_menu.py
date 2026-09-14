import os

import pytest

import helpers
import rom_adapter

if os.environ.get("ROM_NAME", "ditto") != "ditto-menus":
    pytest.skip("menu tests run against the ditto-menus example", allow_module_level=True)

LCDC = 0xFF40
WINDOW_TILE_MAP_9800 = 0x9800
WINDOW_TILE_MAP_9C00 = 0x9C00
TEXT_TILE_BASE = 1
TEXT_SPRITE_TILE_BASE = 0xC0
MENU_CURSOR_TILE = 0xFE
OAM = 0xFE00
VRAM = 0x8000


def sprite(pyboy, slot):
    address = OAM + slot * 4
    return tuple(pyboy.memory[address + offset] for offset in range(4))


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


def test_menu_cursor_is_the_only_sprite_on_the_title(gb):
    pyboy = gb.pyboy

    y, x, tile, prop = sprite(pyboy, 0)
    assert (y, x, tile) == (80, 72, MENU_CURSOR_TILE)
    assert prop == 0
    assert any(pyboy.memory[VRAM + MENU_CURSOR_TILE * 16 : VRAM + (MENU_CURSOR_TILE + 1) * 16])
    assert all(sprite(pyboy, slot)[0] == 0 for slot in range(1, 40))


def test_menu_cursor_moves_with_input_repeat(gb):
    pyboy = gb.pyboy

    pyboy.button_press("left")
    pyboy.tick(2, render=False)
    assert sprite(pyboy, 0)[:2] == (88, 72)
    for _ in range(13):
        pyboy.tick(1, render=False)
        assert sprite(pyboy, 0)[:2] == (88, 72)
    pyboy.tick(1, render=False)
    assert sprite(pyboy, 0)[:2] == (80, 72)
    for _ in range(5):
        pyboy.tick(1, render=False)
        assert sprite(pyboy, 0)[:2] == (80, 72)
    pyboy.tick(1, render=False)
    assert sprite(pyboy, 0)[:2] == (88, 72)
    pyboy.button_release("left")
    pyboy.tick(1, render=False)


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
    pyboy.tick(2, render=False)

    # The play state replaces the title menu instead of leaving its window
    # and cursor over the play background.
    assert not (pyboy.memory[LCDC] & 0x20)
    assert sprite(pyboy, 0)[:2] == (0, 0)
