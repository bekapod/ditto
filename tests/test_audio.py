import rom_adapter


def test_a_triggers_the_temporary_sfx_after_sequence(gb, states):
    calls = []
    rom_adapter.hook(gb.pyboy, "audio_play_test_sfx", lambda _: calls.append(True))

    gb.pyboy.button("start")
    gb.pyboy.tick(1, render=False)
    for _ in range(30):
        if gb.state == states["STATE_PLAY"]:
            break
        gb.pyboy.tick(1, render=False)
    assert gb.state == states["STATE_PLAY"]

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
