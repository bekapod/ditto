# ditto

Shared Game Boy template and engine for original DMG hardware.

## Build the ROM

If GBDK-2020 is not installed at `~/gbdk/`, set `GBDK_HOME` to its install path. Then run:

```sh
make
```

`make` writes the ROM to `build/ditto.gb`.

## Export artwork

Use the four DMG greens in `art/palette.gpl`. The entries are ordered darkest to lightest.

In Aseprite:

1. Create a `160 × 144` canvas.
2. Open the palette panel and import `art/palette.gpl`.
3. Set the image to indexed color mode.
4. Use only the four imported colors.
5. Export a PNG and preserve its indexed palette.
6. Put the PNG in `art/`.

Use the filename suffix that matches the asset type:

- `*_map.png` is a tile map. The build compares it with `art/tileset.png`.
- `*_screen.png` is a full-screen image.
- Any other PNG is a tile sheet.

The build passes `-keep_palette_order` to `png2asset`. Keep the PNG palette in darkest-to-lightest order.