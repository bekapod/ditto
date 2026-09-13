import rom_adapter


def test_set_seed_writes_exported_run_seed(gb):
    seed = 0xBEEF
    rom_adapter.set_seed(gb.pyboy, seed)

    _, address = gb.pyboy.symbol_lookup(rom_adapter.symbol("run_seed"))
    assert gb.pyboy.memory[address] == 0xEF
    assert gb.pyboy.memory[address + 1] == 0xBE
