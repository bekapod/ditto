import helpers


TEXT_TILE_BASE = 1
OAM = 0xFE00


def sprite(pyboy, slot):
    address = OAM + slot * 4
    return tuple(pyboy.memory[address + offset] for offset in range(4))


def wait_for(pyboy, callback):
    reached = []
    helpers.rom_adapter.hook(pyboy, callback, lambda _: reached.append(True))
    for _ in range(helpers.BOOT_CAP_FRAMES):
        pyboy.tick(1, render=False)
        if reached:
            helpers.rom_adapter.unhook(pyboy, callback)
            return
    raise RuntimeError(f"ROM did not reach {callback} within 600 frames")


def test_state_sprite_cleanup(gb):
    pyboy = gb.pyboy

    y, x, tile, prop = sprite(pyboy, 0)
    assert (y, x, tile) == (80, 64, TEXT_TILE_BASE + 39)
    assert prop == 0
    assert all(sprite(pyboy, slot)[0] == 0 for slot in range(1, 40))

    pyboy.button("start")
    wait_for(pyboy, "play_update")
    for slot, coordinates in enumerate(((112, 64), (112, 72), (120, 64), (120, 72))):
        y, x, tile, prop = sprite(pyboy, slot)
        assert (y, x, tile, prop) == (*coordinates, TEXT_TILE_BASE + 39, 0)
    assert all(sprite(pyboy, slot)[0] == 0 for slot in range(4, 40))
    pyboy.tick(20, render=False)

    pyboy.button("b")
    pyboy.tick(1, render=False)
    wait_for(pyboy, "title_update")
    assert sprite(pyboy, 0)[:2] == (80, 64)
    assert all(sprite(pyboy, slot)[0] == 0 for slot in range(1, 4))
