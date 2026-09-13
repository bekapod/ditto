import helpers


TEXT_TILE_BASE = 1
TEXT_SPRITE_TILE_BASE = 0xC0
MENU_CURSOR_TILE = 0xFE
OAM = 0xFE00
VRAM = 0x8000


def sprite(pyboy, slot):
    address = OAM + slot * 4
    return tuple(pyboy.memory[address + offset] for offset in range(4))


def wait_for_state(pyboy, state_name):
    """Wait until the given state descriptor is on top of the state stack.

    Used instead of re-hooking the same update callback: PyBoy's hook
    machinery only fires a hook reliably once per registration, so
    repeated waits on title/play poll the stack directly.
    """
    stack_addr = helpers.symbol_address("Fstate$stack$0_0$0")
    target = helpers.symbol_address(f"Fmain${state_name}$0_0$0")
    for _ in range(helpers.BOOT_CAP_FRAMES):
        top = pyboy.memory[stack_addr] | (pyboy.memory[stack_addr + 1] << 8)
        # init may run with the display off for several frames, so also
        # wait for the display to come back before reading its output.
        if top == target and pyboy.memory[0xFF40] & 0x80:
            # Let the state's first rendered frame transfer its OAM/VRAM.
            pyboy.tick(2, render=False)
            return
        pyboy.tick(1, render=False)
    raise RuntimeError(f"ROM did not reach {state_name} within 600 frames")


def test_state_sprite_cleanup(gb):
    pyboy = gb.pyboy

    y, x, tile, prop = sprite(pyboy, 0)
    assert (y, x, tile) == (80, 72, MENU_CURSOR_TILE)
    assert prop == 0
    assert any(pyboy.memory[VRAM + MENU_CURSOR_TILE * 16 : VRAM + (MENU_CURSOR_TILE + 1) * 16])
    assert all(sprite(pyboy, slot)[0] == 0 for slot in range(1, 40))

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

    pyboy.button("b")
    pyboy.tick(2, render=False)
    pyboy.button("start")
    wait_for_state(pyboy, "play_state")
    # The play state starts with a fade-in; edge input is ignored until
    # it completes, so wait it out before pressing anything.
    fade_active = helpers.symbol_address("_fade_active")
    for _ in range(600):
        if not pyboy.memory[fade_active]:
            break
        pyboy.tick(1, render=False)
    for slot in range(10):
        y, x, tile, prop = sprite(pyboy, slot)
        assert (y, x, prop) == (16, 88 + slot * 8, 0)
        assert TEXT_SPRITE_TILE_BASE <= tile < MENU_CURSOR_TILE
    assert all(sprite(pyboy, slot)[0] == 0 for slot in range(10, 40))
    pyboy.tick(20, render=False)

    pyboy.button("b")
    pyboy.tick(1, render=False)
    wait_for_state(pyboy, "title_state")
    assert sprite(pyboy, 0)[:2] == (80, 72)
    assert all(sprite(pyboy, slot)[0] == 0 for slot in range(1, 14))
