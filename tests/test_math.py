import os
import struct

import pytest

import rom_adapter

if os.environ.get("ROM_NAME", "ditto") != "ditto":
    pytest.skip("math diagnostics run against the default ROM", allow_module_level=True)


def read_i16_array(pyboy, name, count):
    _, address = rom_adapter.lookup(pyboy, name)
    return [
        struct.unpack_from("<h", bytes(pyboy.memory[address + i * 2 : address + i * 2 + 2]))[0]
        for i in range(count)
    ]


def read_u8_array(pyboy, name, count):
    _, address = rom_adapter.lookup(pyboy, name)
    return list(pyboy.memory[address : address + count])


def test_fixed_point_and_hit_cases(gb):
    assert read_i16_array(gb.pyboy, "debug_fx_cases", 10) == [
        -512,
        -2,
        128,
        256,
        -1,
        0,
        1,
        -256,
        0,
        256,
    ]
    assert read_u8_array(gb.pyboy, "debug_hit_cases", 5) == [0, 1, 0, 1, 0]
