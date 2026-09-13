import helpers
import rom_adapter

SCX_REG = 0xFF43
VRAM_BG = 0x9800
TEXT_TILE_BASE = 1


def boot_to_play(pyboy):
    pyboy.button("start")
    helpers.wait_for_callback(pyboy, "play_update")
    pyboy.tick(20, render=False)


def scroll_phase(pyboy):
    address = rom_adapter.lookup(pyboy, "scroll_x")[1]
    return pyboy.memory[address] | (pyboy.memory[address + 1] << 8)


def test_scroll_speeds_and_streamed_pattern(gb):
    pyboy = gb.pyboy
    boot_to_play(pyboy)
    start = scroll_phase(pyboy)

    pyboy.tick(3600, render=False)
    assert scroll_phase(pyboy) == (start + 3600 * 0x0100) & 0xFFFF
    assert pyboy.memory[SCX_REG] == ((start >> 8) + 3600) & 0xFF

    pyboy.button("select")
    pyboy.tick(1, render=False)
    pyboy.tick(3600, render=False)
    assert scroll_phase(pyboy) == (start + 3600 * 0x0100 + 0x0180 + 3600 * 0x0180) & 0xFFFF

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
    phase = scroll_phase(pyboy)
    register = pyboy.memory[SCX_REG]

    pyboy.button("start")
    pyboy.tick(1, render=False)
    pyboy.tick(120, render=False)
    assert scroll_phase(pyboy) == phase
    assert pyboy.memory[SCX_REG] == register

    pyboy.button("start", delay=2)
    pyboy.tick(3, render=False)
    assert scroll_phase(pyboy) == (phase + 0x0100) & 0xFFFF
