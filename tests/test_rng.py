import os

import pytest

import rom_adapter

if os.environ.get("ROM_NAME", "ditto") != "ditto":
    pytest.skip("RNG diagnostics run against the default ROM", allow_module_level=True)


def test_set_seed_writes_exported_run_seed(gb):
    seed = 0xBEEF
    rom_adapter.set_seed(gb.pyboy, seed)

    _, address = rom_adapter.lookup(gb.pyboy, "run_seed")
    assert gb.pyboy.memory[address] == 0xEF
    assert gb.pyboy.memory[address + 1] == 0xBE
