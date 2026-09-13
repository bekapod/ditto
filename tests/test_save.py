from pathlib import Path

from pyboy import PyBoy

import helpers
import rom_adapter


SAVE_FILE = helpers.ROOT / "build" / "ditto.sav"


def open_game(ram_file):
    return PyBoy(
        str(helpers.ROM),
        window="null",
        symbols=str(helpers.SYM),
        sound_emulated=True,
        no_input=True,
        ram_file=ram_file,
    )


def state_of(pyboy):
    return pyboy.memory[pyboy.symbol_lookup(rom_adapter.symbol("state"))]


def boot_to_play(pyboy):
    helpers.wait_for_boot(pyboy, "title_update")
    pyboy.button("start")
    for _ in range(helpers.BOOT_CAP_FRAMES):
        pyboy.tick(1, render=False)
        if state_of(pyboy) == 4:
            return
    raise RuntimeError("ROM did not reach play within the boot frame cap")


def test_score_survives_power_cycle():
    SAVE_FILE.unlink(missing_ok=True)
    first = None
    second = None
    first_ram = None
    second_ram = None
    try:
        SAVE_FILE.write_bytes(bytes(8192))
        first_ram = SAVE_FILE.open("r+b")
        first = open_game(first_ram)
        boot_to_play(first)
        first.tick(10, render=False)
        first_ram.seek(0)
        first.stop(save=True, ram_file=first_ram)
        first = None
        first_ram.close()
        first_ram = None

        assert SAVE_FILE.exists()
        raw_save = SAVE_FILE.read_bytes()
        assert raw_save[0] == 0xA5
        assert raw_save[1] == 1
        assert int.from_bytes(raw_save[2:4], "little") != 0

        second_ram = SAVE_FILE.open("r+b")
        second = open_game(second_ram)
        helpers.wait_for_boot(second, "title_update")
        second.memory[0x0000] = 0x0A
        assert second.memory[0xA000] == 0xA5
        assert second.memory[0xA001] == 1
        assert second.memory[0xA002] == raw_save[2]
        assert second.memory[0xA003] == raw_save[3]
        second.memory[0x0000] = 0
    finally:
        if first is not None:
            first.stop(save=False)
        if second is not None:
            second.stop(save=False)
        if first_ram is not None:
            first_ram.close()
        if second_ram is not None:
            second_ram.close()
        SAVE_FILE.unlink(missing_ok=True)
