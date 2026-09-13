import helpers
import rom_adapter

SCX_REG = 0xFF43
VRAM_BG = 0x9800
OAM = 0xFE00
TEXT_TILE_BASE = 1
TEXT_SPRITE_TILE_BASE = 0xC0
HUD_SCORE_SLOT = 0
HUD_SCORE_TILES = [0xDC, 0xCC, 0xD8, 0xDB, 0xCE]
PAUSE_HUD_SLOT = 10
PAUSE_HUD_TILES = [0xD9, 0xCA, 0xDE, 0xDC, 0xCE, 0xCD]


def boot_to_play(pyboy):
    pyboy.button("start")
    helpers.wait_for_callback(pyboy, "play_update")
    pyboy.tick(20, render=False)


def scroll_phase(pyboy):
    address = rom_adapter.lookup(pyboy, "scroll_x")[1]
    return pyboy.memory[address] | (pyboy.memory[address + 1] << 8)


def sprite(pyboy, slot):
    address = OAM + slot * 4
    return tuple(pyboy.memory[address + offset] for offset in range(4))


def test_score_hud_stays_fixed_while_the_background_scrolls(gb):
    pyboy = gb.pyboy
    boot_to_play(pyboy)

    expected = [(16, 88 + index * 8, tile, 0) for index, tile in enumerate(HUD_SCORE_TILES)]
    assert [sprite(pyboy, HUD_SCORE_SLOT + index) for index in range(5)] == expected
    pyboy.tick(120, render=False)
    assert pyboy.memory[SCX_REG] != 0
    assert [sprite(pyboy, HUD_SCORE_SLOT + index) for index in range(5)] == expected


def test_scroll_speeds_and_streamed_pattern(gb):
    pyboy = gb.pyboy
    boot_to_play(pyboy)
    start = scroll_phase(pyboy)

    pyboy.tick(3600, render=False)
    assert scroll_phase(pyboy) == (start + 3600 * 0x0100) & 0xFFFF
    assert pyboy.memory[SCX_REG] == ((start >> 8) + 3600) & 0xFF

    pyboy.button_press("select")
    pyboy.tick(1, render=False)
    pyboy.button_release("select")
    pyboy.tick(2, render=False)
    fast_start = scroll_phase(pyboy)
    pyboy.tick(3600, render=False)
    assert scroll_phase(pyboy) == (fast_start + 3600 * 0x0180) & 0xFFFF

    phase_pixels = scroll_phase(pyboy) >> 8
    left_world = (phase_pixels // 8) & 0xFF
    left_map = (phase_pixels // 8) & 31
    for offset in range(21):
        map_col = (left_map + offset) & 31
        world_col = (left_world + offset) & 0xFF
        for row in list(range(8)) + list(range(9, 18)):
            assert pyboy.memory[VRAM_BG + row * 32 + map_col] == (
                TEXT_TILE_BASE + ((world_col + row) & 3)
            )


def test_scroll_pause_resume_preserves_phase(gb):
    pyboy = gb.pyboy
    boot_to_play(pyboy)
    pyboy.tick(5, render=False)

    pyboy.button_press("start")
    helpers.wait_for_callback(pyboy, "pause_init")
    pyboy.button_release("start")
    phase = scroll_phase(pyboy)
    register = pyboy.memory[SCX_REG]
    expected_pause_hud = [
        (80, 56 + index * 8, tile, 0) for index, tile in enumerate(PAUSE_HUD_TILES)
    ]
    assert [sprite(pyboy, PAUSE_HUD_SLOT + index) for index in range(6)] == expected_pause_hud
    pyboy.tick(120, render=False)
    assert scroll_phase(pyboy) == phase
    assert pyboy.memory[SCX_REG] == register
    assert [sprite(pyboy, PAUSE_HUD_SLOT + index) for index in range(6)] == expected_pause_hud

    pyboy.button_press("start")
    helpers.wait_for_callback(pyboy, "play_update")
    pyboy.button_release("start")
    assert all(sprite(pyboy, PAUSE_HUD_SLOT + index)[0] == 0 for index in range(6))
    resume_phase = scroll_phase(pyboy)
    pyboy.tick(3, render=False)
    assert scroll_phase(pyboy) == (resume_phase + 3 * 0x0100) & 0xFFFF
