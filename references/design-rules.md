# Pixel item design rules

## Source of truth

Generate a pixel matrix first. Do not generate a large raster image and merely shrink it. Downscaling introduces ambiguous pixels and unstable silhouettes.

## Recommended modes

### Vanilla-like

- `16x16`
- 4–8 solid colors
- meaningful single-pixel highlights allowed
- asymmetrical lighting encouraged
- diagonal orientation for tools when appropriate

### Chunky icon

- `16x16`
- 3–5 solid colors
- one-pixel transparent margin
- optional `minRegionArea: 2`
- centered, front-facing silhouette

### High-detail mod icon

- `32x32`
- 8–16 colors
- no automatic antialiasing
- keep important details visible at inventory scale

## Palette

Pick roles rather than random colors:

1. outline/deep shadow
2. body/base
3. highlight
4. secondary material
5. optional accent

Avoid near-duplicate colors. At native size, each color should visibly contribute to depth or material identity.

## Silhouette

Before shading, render the subject in one color. It should remain recognizable. For swords, preserve blade, guard, grip, and pommel. For food, preserve the characteristic outer contour. For gems, preserve facets without visual noise.

## Transparency

The actual Minecraft PNG must have an alpha-transparent background. A white background is allowed only in preview exports.

## Review checklist

- exact dimensions
- no accidental edge contact
- no half-transparent edge pixels
- no isolated noise unless intentional
- model parent matches item behavior
- texture and JSON namespaces match
- icon remains recognizable at 100% native size
