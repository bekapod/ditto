import rom_adapter


def test_a_triggers_the_temporary_sfx(gb):
    calls = []
    rom_adapter.hook(gb.pyboy, "audio_play_test_sfx", lambda _: calls.append(True))

    gb.pyboy.button("a")
    gb.pyboy.tick(1, render=False)

    rom_adapter.unhook(gb.pyboy, "audio_play_test_sfx")
    assert calls
