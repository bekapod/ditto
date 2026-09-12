def test_blank_program_reaches_title(gb, states):
    assert gb.state == states["STATE_TITLE"]
