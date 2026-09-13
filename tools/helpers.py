"""Shared PyBoy harness primitives for ROM tests."""

import pytest

import rom_adapter

ROOT = rom_adapter.ROOT
ROM = rom_adapter.ROM
SYM = rom_adapter.SYM
BOOT_CAP_FRAMES = 600


def wait_for_boot(pyboy, hook_name: str) -> None:
    booted = []
    rom_adapter.hook(pyboy, hook_name, lambda _: booted.append(True))
    for _ in range(BOOT_CAP_FRAMES):
        pyboy.tick(1, render=False)
        if booted:
            rom_adapter.unhook(pyboy, hook_name)
            return
    raise RuntimeError(f"ROM did not reach {hook_name} within {BOOT_CAP_FRAMES} frames")
