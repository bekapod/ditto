"""Small PyBoy helpers for symbol-addressed ROM tests."""

import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("ROM_ROOT", Path.cwd()))
ROM_NAME = os.environ.get("ROM_NAME", "ditto")
ROM = ROOT / "build" / f"{ROM_NAME}.gb"
SYM = ROM.with_suffix(".sym")


def symbol(name: str) -> str:
    return "_" + name


def lookup(pyboy, name: str):
    candidates = (
        symbol(name),
        f"Fmain${name}$0$0",
        f"Fmain${name}$0_0$0",
    )
    for candidate in candidates:
        try:
            return pyboy.symbol_lookup(candidate)
        except ValueError:
            pass
    raise ValueError(f"Symbol not found: {name}")


def hook(pyboy, name: str, callback) -> None:
    bank, address = lookup(pyboy, name)
    pyboy.hook_register(1 if address >= 0x4000 else bank, address, callback, None)


def unhook(pyboy, name: str) -> None:
    bank, address = lookup(pyboy, name)
    pyboy.hook_deregister(1 if address >= 0x4000 else bank, address)


def set_seed(pyboy, seed: int) -> None:
    """Overwrite the exported 16-bit run seed in little-endian order."""
    _, address = lookup(pyboy, "run_seed")
    seed &= 0xFFFF
    pyboy.memory[address] = seed & 0xFF
    pyboy.memory[address + 1] = seed >> 8


def eval_defs(pairs, seed=None) -> dict[str, int]:
    values: dict[str, int] = dict(seed or {})
    for name, expression in pairs:
        try:
            values[name] = int(eval(expression, {"__builtins__": {}}, values))
        except NameError:
            continue
    return values


def parse_cdefs(filename: str) -> dict[str, int]:
    source = (ROOT / filename).read_text()
    pairs = re.findall(
        r"(?m)^#define (\w+) +(.+?)\s*(?:(?://|/\*).*)?$", source
    )
    return eval_defs(pairs)
