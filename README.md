# Ditto

Ditto is a Pallet starter project and integration consumer for Game Boy projects
built with GBDK. The default ROM shows the smallest complete Pallet application:
a title screen, a play state, and a return to the title.

## Build the default ROM

Install GBDK-2020 at `~/gbdk/`, or set `GBDK_HOME` to its install path. Then
run:

```sh
make
```

The command writes `build/ditto.gb`. Boot the ROM, press Start at the title, and
press B in play to return.

Run a local Pallet checkout with:

```sh
make local
```

Plain `make` uses the Pallet revision in the `engine` submodule. `make local`
uses `../pallet/engine.mk`.

## Add game code

Keep state modules in `src/states/`. Give each state one private context struct
when it needs mutable data. Keep controls, tuning, actors, levels, combat,
inventory, and progression in game-owned modules.

Pallet provides input queries, state transitions, camera, sprite and OAM
primitives, hitboxes, bounded queues, save framing, audio scheduling, and the
frame loop.

Keep `main.c` to hardware setup, resource initialization, a positional
`pallet_game_t` initializer, and `pallet_run(&game)`. SDCC does not support
designated initializers in this build.

## Build the examples

The feature examples are standalone ROMs. Each example uses the same public
Pallet interface as the default ROM.

```sh
make examples
make example-menus
make example-scroll
make example-save
make example-audio
```

The ROMs are written to these paths:

- `build/ditto-menus.gb` demonstrates menus and pause overlays.
- `build/ditto-scroll.gb` demonstrates scrolling, effects, and a HUD.
- `build/ditto-save.gb` demonstrates versioned save data.
- `build/ditto-audio.gb` demonstrates music and sound effects.

Read the corresponding file under `examples/` when you need a starting point
for one of these features.

## Run the tests

Build every ROM and run its matching PyBoy tests with:

```sh
make test
```

To run one ROM directly, set `ROM_ROOT` and `ROM_NAME`:

```sh
cd tests
ROM_ROOT=.. ROM_NAME=ditto-scroll uv run pytest
```

## Artwork

Use the four DMG greens in `art/palette.gpl`, ordered from darkest to lightest.
Create a 160 x 144 indexed image in Aseprite and use only those four colors.
Preserve the palette order when you export a PNG.

Use these filename suffixes:

- `*_map.png` for tile maps. The build compares the map with `art/tileset.png`.
- `*_screen.png` for full-screen images.
- Other `.png` files for tile sheets.

## Advanced Pallet options

Override Pallet capacities with `PALLET_*` compiler flags in the build
configuration. Use raw OAM operations for custom sprite layouts. Add a
`pallet_game_t.on_vblank` callback only for short, custom VBlank work. Pallet
retains ownership of camera and palette register composition.
