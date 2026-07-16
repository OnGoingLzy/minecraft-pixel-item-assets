#!/usr/bin/env python3
"""Deterministic Minecraft pixel item asset generator using only Python stdlib."""

from __future__ import annotations

import argparse
import binascii
import json
import re
import struct
import zlib
from pathlib import Path
from typing import Any, Iterable

_IDENTIFIER_RE = re.compile(r"^[a-z0-9_.-]+$")
_ITEM_ID_RE = re.compile(r"^[a-z0-9_./-]+$")
_LOCALE_RE = re.compile(r"^[a-z0-9_]+$")


def load_spec(path: Path | str) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("spec root must be a JSON object")
    return data


def _parse_color(value: str) -> tuple[int, int, int, int]:
    if value.lower() == "transparent":
        return (0, 0, 0, 0)
    if not isinstance(value, str) or not value.startswith("#"):
        raise ValueError(f"invalid color {value!r}; use #RRGGBB or #RRGGBBAA")
    raw = value[1:]
    if len(raw) == 6:
        raw += "FF"
    if len(raw) != 8 or any(c not in "0123456789abcdefABCDEF" for c in raw):
        raise ValueError(f"invalid color {value!r}; use #RRGGBB or #RRGGBBAA")
    return tuple(int(raw[i : i + 2], 16) for i in range(0, 8, 2))  # type: ignore[return-value]


def _transparent_keys(palette: dict[str, str]) -> set[str]:
    return {key for key, value in palette.items() if _parse_color(value)[3] == 0}


def _is_safe_resource_path(value: str) -> bool:
    return bool(
        _ITEM_ID_RE.fullmatch(value)
        and all(segment not in {"", ".", ".."} for segment in value.split("/"))
    )


def _validate_display_names(display_names: Any) -> None:
    if display_names is None:
        return
    if not isinstance(display_names, dict):
        raise ValueError("minecraft.displayName must be a JSON object when present")
    for locale, name in display_names.items():
        if not isinstance(locale, str) or not _LOCALE_RE.fullmatch(locale):
            raise ValueError("minecraft.displayName locale must use lowercase letters, digits, and underscores")
        if not isinstance(name, str):
            raise ValueError("minecraft.displayName values must be strings")


def validate_spec(spec: dict[str, Any]) -> None:
    if spec.get("schemaVersion") != 1:
        raise ValueError("schemaVersion must be 1")

    mc = spec.get("minecraft")
    canvas = spec.get("canvas")
    palette = spec.get("palette")
    pixels = spec.get("pixels")
    if not isinstance(mc, dict) or not isinstance(canvas, dict):
        raise ValueError("minecraft and canvas must be JSON objects")
    if not isinstance(palette, dict) or not palette:
        raise ValueError("palette must be a non-empty JSON object")
    if not isinstance(pixels, list) or not all(isinstance(row, str) for row in pixels):
        raise ValueError("pixels must be an array of strings")

    mod_id = mc.get("modId")
    item_id = mc.get("itemId")
    version = mc.get("version")
    parent = mc.get("modelParent")
    if not isinstance(mod_id, str) or mod_id in {".", ".."} or not _IDENTIFIER_RE.fullmatch(mod_id):
        raise ValueError("minecraft.modId must use lowercase namespace characters")
    if not isinstance(item_id, str) or not _is_safe_resource_path(item_id):
        raise ValueError("minecraft.itemId must use lowercase resource-path characters")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+(?:\.\d+)?", version):
        raise ValueError("minecraft.version must look like 1.20.1")
    if not isinstance(parent, str) or ":" not in parent:
        raise ValueError("minecraft.modelParent must be a namespaced model path")
    _validate_display_names(mc.get("displayName"))

    width = canvas.get("width")
    height = canvas.get("height")
    margin = canvas.get("margin", 0)
    max_colors = canvas.get("maxSolidColors")
    allow_semi = canvas.get("allowSemiTransparent", False)
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        raise ValueError("canvas width and height must be positive integers")
    if len(pixels) != height or any(len(row) != width for row in pixels):
        raise ValueError("pixels dimensions must exactly match canvas width and height")
    if not isinstance(margin, int) or margin < 0 or margin * 2 >= min(width, height):
        raise ValueError("canvas.margin must be a valid non-negative integer")

    parsed_palette: dict[str, tuple[int, int, int, int]] = {}
    for key, value in palette.items():
        if not isinstance(key, str) or len(key) != 1:
            raise ValueError("each palette key must be exactly one character")
        parsed_palette[key] = _parse_color(value)
        if not allow_semi and parsed_palette[key][3] not in (0, 255):
            raise ValueError("semi-transparent palette colors are not allowed")

    used = set("".join(pixels))
    unknown = used - set(palette)
    if unknown:
        raise ValueError(f"pixels use unknown palette keys: {sorted(unknown)!r}")
    transparent = {key for key, rgba in parsed_palette.items() if rgba[3] == 0}
    if not transparent:
        raise ValueError("palette must include at least one fully transparent color")

    solid_used = {key for key in used if parsed_palette[key][3] != 0}
    if max_colors is not None:
        if not isinstance(max_colors, int) or max_colors < 1:
            raise ValueError("canvas.maxSolidColors must be a positive integer")
        if len(solid_used) > max_colors:
            raise ValueError("used solid color count exceeds canvas.maxSolidColors")

    min_region_area = canvas.get("minRegionArea")
    if min_region_area is not None:
        if not isinstance(min_region_area, int) or min_region_area < 1:
            raise ValueError("canvas.minRegionArea must be a positive integer")
        visited: set[tuple[int, int]] = set()
        for y in range(height):
            for x in range(width):
                key = pixels[y][x]
                if key in transparent or (x, y) in visited:
                    continue
                stack = [(x, y)]
                visited.add((x, y))
                area = 0
                while stack:
                    cx, cy = stack.pop()
                    area += 1
                    for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                        if 0 <= nx < width and 0 <= ny < height:
                            if (nx, ny) not in visited and pixels[ny][nx] == key:
                                visited.add((nx, ny))
                                stack.append((nx, ny))
                if area < min_region_area:
                    raise ValueError(
                        f"color region for palette key {key!r} has area {area}, "
                        f"below canvas.minRegionArea={min_region_area}"
                    )

    if margin:
        for y, row in enumerate(pixels):
            for x, key in enumerate(row):
                if x < margin or x >= width - margin or y < margin or y >= height - margin:
                    if key not in transparent:
                        raise ValueError("non-transparent pixel violates required canvas margin")


def _version_tuple(version: str) -> tuple[int, int, int]:
    parts = [int(part) for part in version.split(".")]
    return tuple((parts + [0, 0, 0])[:3])  # type: ignore[return-value]


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(kind)
    crc = binascii.crc32(payload, crc) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def write_png(path: Path, width: int, height: int, rgba: bytes) -> None:
    expected = width * height * 4
    if len(rgba) != expected:
        raise ValueError(f"RGBA byte length must be {expected}, got {len(rgba)}")
    scanlines = b"".join(
        b"\x00" + rgba[y * width * 4 : (y + 1) * width * 4]
        for y in range(height)
    )
    payload = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + _png_chunk(b"IDAT", zlib.compress(scanlines, level=9))
        + _png_chunk(b"IEND", b"")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _render_rgba(spec: dict[str, Any]) -> bytes:
    palette = {key: _parse_color(value) for key, value in spec["palette"].items()}
    output = bytearray()
    for row in spec["pixels"]:
        for key in row:
            output.extend(palette[key])
    return bytes(output)


def _scaled_rgba(
    spec: dict[str, Any],
    scale: int,
    *,
    white_background: bool,
) -> tuple[int, int, bytes]:
    if not isinstance(scale, int) or scale < 1:
        raise ValueError("scale must be a positive integer")
    width = spec["canvas"]["width"]
    height = spec["canvas"]["height"]
    palette = {key: _parse_color(value) for key, value in spec["palette"].items()}
    result = bytearray()
    for row in spec["pixels"]:
        expanded_row = bytearray()
        for key in row:
            rgba = palette[key]
            if white_background and rgba[3] == 0:
                rgba = (255, 255, 255, 255)
            expanded_row.extend(bytes(rgba) * scale)
        for _ in range(scale):
            result.extend(expanded_row)
    return width * scale, height * scale, bytes(result)


def _svg_text(spec: dict[str, Any], *, white_background: bool) -> str:
    width = spec["canvas"]["width"]
    height = spec["canvas"]["height"]
    palette = {key: _parse_color(value) for key, value in spec["palette"].items()}
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg"',
        f'  width="{width}" height="{height}" viewBox="0 0 {width} {height}"',
        '  shape-rendering="crispEdges">',
    ]
    if white_background:
        lines.append(f'  <rect x="0" y="0" width="{width}" height="{height}" fill="#FFFFFF"/>')
    for y, row in enumerate(spec["pixels"]):
        for x, key in enumerate(row):
            r, g, b, a = palette[key]
            if a == 0:
                continue
            color = f"#{r:02X}{g:02X}{b:02X}"
            attrs = f' fill="{color}"'
            if a != 255:
                attrs += f' fill-opacity="{a / 255:.6f}"'
            lines.append(f'  <rect x="{x}" y="{y}" width="1" height="1"{attrs}/>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def export_previews(
    spec: dict[str, Any],
    output_dir: Path | str,
    *,
    scale: int = 32,
    white_background: bool = True,
) -> list[Path]:
    validate_spec(spec)
    output = Path(output_dir)
    item_id = spec["minecraft"]["itemId"].replace("/", "_")
    width = spec["canvas"]["width"]
    height = spec["canvas"]["height"]
    svg = output / f"{item_id}.svg"
    png = output / f"{item_id}_{width * scale}.png"
    svg.parent.mkdir(parents=True, exist_ok=True)
    svg.write_text(_svg_text(spec, white_background=white_background), encoding="utf-8")
    scaled_width, scaled_height, rgba = _scaled_rgba(
        spec, scale, white_background=white_background
    )
    write_png(png, scaled_width, scaled_height, rgba)
    return [svg, png]


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _merge_json_object(path: Path, entries: dict[str, str]) -> None:
    existing: dict[str, Any] = {}
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"existing JSON file is invalid: {path}") from exc
        if not isinstance(loaded, dict):
            raise ValueError(f"existing JSON file must be an object: {path}")
        existing = loaded
    existing.update(entries)
    _write_json(path, existing)


def build_assets(
    spec: dict[str, Any],
    output_dir: Path | str,
    *,
    item_definition: str = "auto",
) -> list[Path]:
    validate_spec(spec)
    output = Path(output_dir)
    mc = spec["minecraft"]
    canvas = spec["canvas"]
    mod_id = mc["modId"]
    item_id = mc["itemId"]

    texture = output / "assets" / mod_id / "textures" / "item" / f"{item_id}.png"
    model = output / "assets" / mod_id / "models" / "item" / f"{item_id}.json"
    write_png(texture, canvas["width"], canvas["height"], _render_rgba(spec))
    _write_json(
        model,
        {
            "parent": mc["modelParent"],
            "textures": {"layer0": f"{mod_id}:item/{item_id}"},
        },
    )
    written = [texture, model]

    modern = _version_tuple(mc["version"]) >= (1, 21, 4)
    if item_definition not in {"auto", "yes", "no"}:
        raise ValueError("item_definition must be auto, yes, or no")
    should_write_item_definition = modern if item_definition == "auto" else item_definition == "yes"
    if should_write_item_definition:
        item_def = output / "assets" / mod_id / "items" / f"{item_id}.json"
        _write_json(
            item_def,
            {
                "model": {
                    "type": "minecraft:model",
                    "model": f"{mod_id}:item/{item_id}",
                }
            },
        )
        written.append(item_def)

    display_names = mc.get("displayName", {})
    for locale, name in display_names.items():
        lang_file = output / "assets" / mod_id / "lang" / f"{locale}.json"
        _merge_json_object(lang_file, {f"item.{mod_id}.{item_id.replace('/', '.')}": name})
        written.append(lang_file)

    return written


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="validate a .pixel.json specification")
    validate.add_argument("spec", type=Path)

    preview = sub.add_parser("preview", help="export crisp SVG and nearest-neighbor PNG previews")
    preview.add_argument("spec", type=Path)
    preview.add_argument("--output", "-o", type=Path, required=True)
    preview.add_argument("--scale", type=int, default=32)
    preview.add_argument(
        "--transparent-background",
        action="store_true",
        help="keep preview background transparent instead of white",
    )

    build = sub.add_parser("build", help="generate Minecraft item assets")
    build.add_argument("spec", type=Path)
    build.add_argument("--output", "-o", type=Path, required=True)
    build.add_argument(
        "--item-definition",
        choices=("auto", "yes", "no"),
        default="auto",
        help="write assets/<modid>/items/<item>.json; auto enables it for 1.21.4+",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        spec = load_spec(args.spec)
        if args.command == "validate":
            validate_spec(spec)
            print(f"OK: {args.spec}")
        elif args.command == "preview":
            paths = export_previews(
                spec,
                args.output,
                scale=args.scale,
                white_background=not args.transparent_background,
            )
            for path in paths:
                print(path)
        else:
            paths = build_assets(spec, args.output, item_definition=args.item_definition)
            for path in paths:
                print(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
