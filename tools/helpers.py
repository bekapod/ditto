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


def wait_for_state(pyboy, state_name: str) -> None:
    """Wait until the given state descriptor is on top of the state stack.

    Used instead of re-hooking the same update callback: PyBoy's hook
    machinery only fires a hook reliably once per registration, so
    repeated waits on title/play poll the stack directly.
    """
    stack_addr = symbol_address("Fstate$stack$0_0$0")
    target = symbol_address(f"Fmain${state_name}$0_0$0")
    for _ in range(BOOT_CAP_FRAMES):
        top = pyboy.memory[stack_addr] | (pyboy.memory[stack_addr + 1] << 8)
        # init may run with the display off for several frames, so also
        # wait for the display to come back before reading its output.
        if top == target and pyboy.memory[0xFF40] & 0x80:
            # Let the state's first rendered frame transfer its OAM/VRAM.
            pyboy.tick(2, render=False)
            return
        pyboy.tick(1, render=False)
    raise RuntimeError(f"ROM did not reach {state_name} within {BOOT_CAP_FRAMES} frames")


def wait_for_fade(pyboy) -> None:
    """Wait until Pallet's fade is no longer active."""
    fade_active = symbol_address("_fade_active")
    for _ in range(BOOT_CAP_FRAMES):
        if not pyboy.memory[fade_active]:
            return
        pyboy.tick(1, render=False)
    raise RuntimeError(f"fade did not finish within {BOOT_CAP_FRAMES} frames")
