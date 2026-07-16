# Minecraft item resource version matrix

This skill targets Minecraft Java Edition 1.20 and later.

## 1.20.x through 1.21.3-style projects

Generate:

```text
assets/<modid>/textures/item/<item_id>.png
assets/<modid>/models/item/<item_id>.json
assets/<modid>/lang/<locale>.json
```

Typical flat model:

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "examplemod:item/example_item"
  }
}
```

Typical sword/tool model uses `minecraft:item/handheld`.

## 1.21.4 and later

In addition to the texture and model JSON, generate a client item-definition file:

```text
assets/<modid>/items/<item_id>.json
```

```json
{
  "model": {
    "type": "minecraft:model",
    "model": "examplemod:item/example_item"
  }
}
```

The generator uses this behavior automatically when `minecraft.version >= 1.21.4`.

## Overrides and edge cases

Use an explicit override when the project has backports, custom loaders, generated resources, or a nonstandard resource pipeline:

```bash
--item-definition yes
--item-definition no
```

Do not assume a loader changes a simple texture/model path. Inspect the existing project resources and datagen code first.

Complex animated, predicate-based, component-driven, or custom-rendered items may require additional files or code beyond this skill's simple flat-item workflow.
