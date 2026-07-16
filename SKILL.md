---
name: minecraft-pixel-item-assets
description: Use when creating, editing, validating, or exporting low-resolution Minecraft Java Edition mod item icons and their PNG textures, item model JSON, client item-definition JSON, language files, or resource directory structure for Minecraft 1.20 and later.
---

# Minecraft Pixel Item Assets

## Purpose

Create deterministic Minecraft item resources from a structured pixel matrix. Treat the `.pixel.json` file as the source of truth; generate PNG, SVG preview, and Minecraft JSON files from it.

## Required workflow

1. Inspect the project before generating files. Resolve Minecraft version, loader, `modId`, item registry ID, resource root, and whether the item is handheld.
2. Before writing derived files, ask for the resource output path unless the user supplied one. First offer the detected project's `src/main/resources` path; write there only after the user explicitly approves. If they decline, request and use their chosen output path.
2. If a value cannot be inferred, use conservative defaults and state them in the result:
   - version: project version, otherwise `1.20.1`
   - texture size: `16x16`
   - ordinary item parent: `minecraft:item/generated`
   - sword/tool parent: `minecraft:item/handheld`
3. Create or update a `.pixel.json` specification using `references/pixel-json-schema.md`.
4. Keep the PNG background transparent. Never use white as fake transparency.
5. Validate before exporting:

```bash
python scripts/mc_item_asset.py validate path/to/item.pixel.json
```

6. Export human-review previews:

```bash
python scripts/mc_item_asset.py preview path/to/item.pixel.json \
  --output build/pixel-preview --scale 32
```

7. Generate resources directly into the project resource root:

```bash
python scripts/mc_item_asset.py build path/to/item.pixel.json \
  --output src/main/resources
```

8. Verify generated paths and run the project resource/datagen/build checks. Do not claim completion without opening or parsing the generated PNG and JSON files.

## Pixel design rules

- Use exact logical dimensions, normally `16x16` or `32x32`.
- Use integer pixels only. No gradients, antialiasing, blur, filters, fractional coordinates, or semitransparent edge pixels.
- Use alpha `0` for empty pixels and `255` for solid pixels unless the user explicitly requests translucency.
- Keep the silhouette recognizable at native size.
- Prefer a limited palette with intentional highlights and shadows.
- A one-pixel transparent margin is recommended for centered icons, but diagonal vanilla-like tools may use available space when required.
- Allow meaningful one-pixel highlights and corners. Use `minRegionArea` only for deliberately chunky styles.
- Create original designs; do not copy an official Mojang texture pixel-for-pixel.

Read `references/design-rules.md` before designing a new icon family.

## Version behavior

- For legacy-style item resources, generate `assets/<modid>/models/item/<id>.json` referencing `textures/item/<id>.png`.
- For Minecraft `1.21.4+`, the generator also creates `assets/<modid>/items/<id>.json` by default.
- Override uncertain or backported setups with `--item-definition yes|no`.

Read `references/version-matrix.md` when the project version is not straightforward.

## Editing and review

Use `assets/pixel-editor.html` for manual pixel editing. It runs locally with no dependencies and exports `.pixel.json`, exact-size transparent PNG, and crisp SVG.

When the user supplies an existing PNG, do not trace it with smoothing. Reconstruct it into the pixel matrix, validate alpha and palette, then regenerate all derived files.

## Deliverables

Report:

- source `.pixel.json`
- generated texture path
- generated model/item-definition paths
- native dimensions and solid-color count
- validation command and result
- any assumptions about version, loader, or model parent
