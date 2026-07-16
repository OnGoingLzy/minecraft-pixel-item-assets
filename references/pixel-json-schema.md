# Pixel JSON schema

The `.pixel.json` document is the editable source of truth. Generated PNG and Minecraft JSON files are derived artifacts.

## Root fields

| Field | Required | Meaning |
|---|---:|---|
| `schemaVersion` | yes | Must be `1` |
| `minecraft` | yes | Version, namespace, ID, model parent, language names |
| `canvas` | yes | Logical dimensions and validation policy |
| `palette` | yes | One-character keys mapped to RGBA colors |
| `pixels` | yes | One string per logical row |

## `minecraft`

```json
{
  "version": "1.20.1",
  "loader": "forge",
  "modId": "examplemod",
  "itemId": "emerald_sword",
  "modelParent": "minecraft:item/handheld",
  "displayName": {
    "en_us": "Emerald Sword",
    "zh_cn": "绿宝石剑"
  }
}
```

Rules:

- `modId` must be lowercase.
- `itemId` should be lowercase `snake_case`; `/` is allowed for nested resource paths.
- Use `minecraft:item/handheld` for swords and most tools.
- Use `minecraft:item/generated` for materials, food, gems, and ordinary flat items.
- `loader` is metadata. Simple client resources normally share the same asset layout across Forge, NeoForge, and Fabric.

## `canvas`

```json
{
  "width": 16,
  "height": 16,
  "margin": 1,
  "maxSolidColors": 8,
  "allowSemiTransparent": false,
  "minRegionArea": 2
}
```

- `width` and `height` must exactly match the pixel matrix.
- `margin` enforces transparent pixels around all four edges. Set `0` when a diagonal tool intentionally uses the full canvas.
- `maxSolidColors` counts used nontransparent palette entries.
- `allowSemiTransparent` defaults to `false`.
- `minRegionArea` is optional. Omit it for vanilla-like sprites that need meaningful single-pixel details.

## `palette`

Each key must be exactly one character. Colors accept `#RRGGBB`, `#RRGGBBAA`, or `transparent`.

```json
{
  ".": "#00000000",
  "D": "#075C35FF",
  "G": "#12A85AFF",
  "L": "#65E89BFF"
}
```

Use a dedicated transparent key, normally `.`.

## `pixels`

For a `16x16` canvas, provide exactly 16 strings, each exactly 16 characters long. Every character must exist in `palette`.

```json
"pixels": [
  "................",
  ".......LL.......",
  "......LGGL......",
  "................"
]
```

## Commands

```bash
python scripts/mc_item_asset.py validate item.pixel.json
python scripts/mc_item_asset.py preview item.pixel.json -o build/preview --scale 32
python scripts/mc_item_asset.py build item.pixel.json -o src/main/resources
```
