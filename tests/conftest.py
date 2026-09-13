import sys
from pathlib import Path

import pytest
from pyboy import PyBoy

sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))
import helpers
import rom_adapter


class Harness:
    def __init__(self, pyboy):
        self.pyboy = pyboy


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
