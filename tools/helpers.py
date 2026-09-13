"""Shared PyBoy harness primitives for ROM tests."""

import pytest

import rom_adapter

ROOT = rom_adapter.ROOT
ROM = rom_adapter.ROM
SYM = rom_adapter.SYM
BOOT_CAP_FRAMES = 600


def symbol_address(name: str) -> int:
    """Resolve an exact .sym symbol name to its address."""
    with open(SYM) as sym_file:
        for line in sym_file:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == name:
                address = parts[0].split(":")[1]
                return int(address, 16)
    raise ValueError(f"Symbol not found: {name}")


def wait_for_boot(pyboy, hook_name: str) -> None:
    wait_for_callback(pyboy, hook_name)


def wait_for_callback(pyboy, hook_name: str) -> None:
    reached = []
    rom_adapter.hook(pyboy, hook_name, lambda _: reached.append(True))
    for _ in range(BOOT_CAP_FRAMES):
        pyboy.tick(1, render=False)
        if reached:
            rom_adapter.unhook(pyboy, hook_name)
            return
    raise RuntimeError(f"ROM did not reach {hook_name} within {BOOT_CAP_FRAMES} frames")
