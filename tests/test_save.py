import os
from pathlib import Path

import pytest
from pyboy import PyBoy

if os.environ.get("ROM_NAME", "ditto") != "ditto-save":
    pytest.skip("save tests run against the ditto-save example", allow_module_level=True)

import helpers
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


def boot_to_play(pyboy):
    helpers.wait_for_boot(pyboy, "title_update")
    pyboy.button("start")
    helpers.wait_for_callback(pyboy, "play_update")
    pyboy.tick(20, render=False)


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
        # Header: magic, schema version, checksum; then the payload.
        assert raw_save[0] == 0xA5
        assert raw_save[1] == 1
        assert int.from_bytes(raw_save[3:5], "little") != 0

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
