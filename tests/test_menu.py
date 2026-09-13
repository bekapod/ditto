import helpers
import rom_adapter


def test_sound_test_uses_selected_menu_item(gb):
    pyboy = gb.pyboy
    calls = []
    rom_adapter.hook(pyboy, "audio_play_test_sfx", lambda _: calls.append(True))

    pyboy.button_press("left")
    pyboy.tick(1, render=False)
    pyboy.button_release("left")
    pyboy.tick(1, render=False)
    pyboy.button_press("a")
    pyboy.tick(1, render=False)
    pyboy.button_release("a")
    pyboy.tick(1, render=False)

    rom_adapter.unhook(pyboy, "audio_play_test_sfx")
    assert calls == [True]
    helpers.wait_for_callback(pyboy, "title_update")


def test_start_confirms_the_default_menu_item(gb):
    pyboy = gb.pyboy

    pyboy.button("start")
    helpers.wait_for_callback(pyboy, "play_update")
