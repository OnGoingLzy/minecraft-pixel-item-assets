# Minecraft Pixel Item Assets

[中文说明](README.md) · [Skill definition](SKILL.md) · [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)

A Codex skill and dependency-free generator for Minecraft Java Edition mod item icons. A `.pixel.json` matrix is the source of truth and deterministically produces transparent PNG textures, SVG previews, item model JSON, language files, and item-definition JSON for Minecraft 1.21.4+.

![Emerald sword pixel preview](docs/examples/emerald_sword_512.png)

## Contents

- `SKILL.md`: agent trigger conditions and workflow.
- `scripts/mc_item_asset.py`: standard-library-only validation, preview, and export CLI.
- `assets/pixel-editor.html`: offline pixel editor that exports `.pixel.json`, PNG, and SVG.
- `assets/examples/emerald_sword.pixel.json`: complete 16×16 example.
- `references/`: pixel JSON schema, design rules, and Minecraft version matrix.

## Install as a Codex skill

Copy this directory into a project or user skill directory, then invoke:

```text
$minecraft-pixel-item-assets
```

Example prompt:

```text
$minecraft-pixel-item-assets Create a 16×16 item icon for my NeoForge 1.21.1 mod. Use modId examplemod and item ID emerald_sword, then generate it into src/main/resources.
```

## Quick start

No third-party Python packages are required. From the repository root, run:

```powershell
python scripts/mc_item_asset.py validate assets/examples/emerald_sword.pixel.json
python scripts/mc_item_asset.py preview assets/examples/emerald_sword.pixel.json --output build/pixel-preview --scale 32
python scripts/mc_item_asset.py build assets/examples/emerald_sword.pixel.json --output build/generated-resources
```

Resources are written under `build/generated-resources/assets/<modId>/`. Ordinary items default to `minecraft:item/generated`; tools use `minecraft:item/handheld`. Minecraft 1.21.4+ additionally generates `assets/<modId>/items/<itemId>.json` by default.

## Asset rules

- Use 16×16 or 32×32 integer pixels and a transparent background; never fake transparency with white.
- Do not use gradients, antialiasing, blur, filters, or fractional pixels.
- Solid pixels use alpha `255` and empty pixels use alpha `0` by default.
- Read the [pixel JSON schema](references/pixel-json-schema.md), [design rules](references/design-rules.md), and [version matrix](references/version-matrix.md) before changing a resource family.

## Validation

```powershell
python -m unittest discover -s tests -v
```

GitHub Actions validates, previews, and builds the example on Python 3.11 and 3.12.

## License notice

No `LICENSE` is currently provided. Public visibility does not grant permission to copy, modify, distribute, or use this work commercially. Contact the repository maintainer for written permission before reuse.
