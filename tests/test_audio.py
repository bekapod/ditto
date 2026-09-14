import os

import pytest

import helpers
import rom_adapter

if os.environ.get("ROM_NAME", "ditto") != "ditto-audio":
    pytest.skip("audio tests run against the ditto-audio example", allow_module_level=True)


def test_a_triggers_the_temporary_sfx_after_sequence(gb):
    calls = []
    rom_adapter.hook(gb.pyboy, "audio_play_test_sfx", lambda _: calls.append(True))

    gb.pyboy.button("start")
    helpers.wait_for_callback(gb.pyboy, "play_update")
    gb.pyboy.tick(20, render=False)

    gb.pyboy.button("a")
    gb.pyboy.tick(1, render=False)
    gb.pyboy.button("a")
    gb.pyboy.tick(1, render=False)
    gb.pyboy.button("a")
    gb.pyboy.tick(1, render=False)

    gb.pyboy.tick(17, render=False)
    assert not calls
    gb.pyboy.tick(10, render=False)
    rom_adapter.unhook(gb.pyboy, "audio_play_test_sfx")
    assert calls == [True]
