import os

import pytest

import helpers

if os.environ.get("ROM_NAME", "ditto") != "ditto-scroll":
    pytest.skip("sprite tests run against the ditto-scroll example", allow_module_level=True)

TEXT_TILE_BASE = 1
TEXT_SPRITE_TILE_BASE = 0xC0
OAM = 0xFE00


def sprite(pyboy, slot):
    address = OAM + slot * 4
    return tuple(pyboy.memory[address + offset] for offset in range(4))


def boot_to_play(pyboy):
    pyboy.button("start")
    helpers.wait_for_callback(pyboy, "play_update")
    # The play state starts with a fade-in; edge input is ignored until
    # it completes, so wait it out before pressing anything.
    helpers.wait_for_fade(pyboy)
    pyboy.tick(20, render=False)


def test_state_sprite_cleanup(gb):
    pyboy = gb.pyboy
    boot_to_play(pyboy)

    # The score HUD allocates ten sprites; nothing else is on screen.
    for slot in range(10):
        y, x, tile, prop = sprite(pyboy, slot)
        assert (y, x, prop) == (16, 88 + slot * 8, 0)
        assert TEXT_SPRITE_TILE_BASE <= tile < 0xFE
    assert all(sprite(pyboy, slot)[0] == 0 for slot in range(10, 40))

    pyboy.button("b")
    helpers.wait_for_state(pyboy, "title_state")
    pyboy.tick(2, render=False)
    # Returning to the title frees the HUD sprites and resets the scrolling
    # camera as well as the sprite pool.
    assert pyboy.memory[0xFF43] == 0
    assert all(sprite(pyboy, slot)[0] == 0 for slot in range(40))
