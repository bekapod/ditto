import sys
from pathlib import Path

import pytest
from pyboy import PyBoy

sys.path.insert(0, str(Path(__file__).parents[1] / "engine" / "tools"))
import helpers
import rom_adapter


class Harness:
    def __init__(self, pyboy):
        self.pyboy = pyboy

    @property
    def state(self):
        return self.pyboy.memory[self.pyboy.symbol_lookup(rom_adapter.symbol("state"))]


@pytest.fixture(scope="session")
def states():
    return rom_adapter.states()


@pytest.fixture
def gb():
    if not helpers.ROM.exists():
        pytest.fail(f"{helpers.ROM.name} not found — build it first")
    pyboy = PyBoy(
        str(helpers.ROM),
        window="null",
        symbols=str(helpers.SYM),
        sound_emulated=True,
        no_input=True,
    )
    harness = Harness(pyboy)
    helpers.wait_for_boot(pyboy, "title_update")
    yield harness
    pyboy.stop(save=False)
