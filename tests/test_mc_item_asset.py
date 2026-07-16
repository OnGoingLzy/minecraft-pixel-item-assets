import json
import struct
import tempfile
import unittest
from pathlib import Path

from scripts.mc_item_asset import build_assets, export_previews, load_spec, validate_spec


VALID_SPEC = {
    "schemaVersion": 1,
    "minecraft": {
        "version": "1.20.1",
        "loader": "forge",
        "modId": "examplemod",
        "itemId": "emerald_sword",
        "modelParent": "minecraft:item/handheld",
        "displayName": {"en_us": "Emerald Sword", "zh_cn": "绿宝石剑"},
    },
    "canvas": {
        "width": 4,
        "height": 4,
        "margin": 1,
        "maxSolidColors": 3,
        "allowSemiTransparent": False,
    },
    "palette": {
        ".": "#00000000",
        "G": "#16A05DFF",
        "D": "#0B5D35FF",
    },
    "pixels": [
        "....",
        ".GD.",
        ".DG.",
        "....",
    ],
}


class PixelAssetTests(unittest.TestCase):
    def test_valid_spec_passes(self):
        validate_spec(VALID_SPEC)

    def test_nontransparent_margin_is_rejected(self):
        broken = json.loads(json.dumps(VALID_SPEC))
        broken["pixels"][0] = "G..."
        with self.assertRaisesRegex(ValueError, "margin"):
            validate_spec(broken)

    def test_build_legacy_assets_without_item_definition(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            written = build_assets(VALID_SPEC, output)
            texture = output / "assets/examplemod/textures/item/emerald_sword.png"
            model = output / "assets/examplemod/models/item/emerald_sword.json"
            item_def = output / "assets/examplemod/items/emerald_sword.json"
            self.assertIn(texture, written)
            self.assertTrue(texture.exists())
            self.assertTrue(model.exists())
            self.assertFalse(item_def.exists())
            model_data = json.loads(model.read_text(encoding="utf-8"))
            self.assertEqual(model_data["parent"], "minecraft:item/handheld")
            self.assertEqual(model_data["textures"]["layer0"], "examplemod:item/emerald_sword")
            width, height = read_png_size(texture)
            self.assertEqual((width, height), (4, 4))

    def test_build_modern_assets_with_item_definition(self):
        spec = json.loads(json.dumps(VALID_SPEC))
        spec["minecraft"]["version"] = "1.21.4"
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            build_assets(spec, output)
            item_def = output / "assets/examplemod/items/emerald_sword.json"
            self.assertTrue(item_def.exists())
            item_data = json.loads(item_def.read_text(encoding="utf-8"))
            self.assertEqual(item_data["model"]["type"], "minecraft:model")
            self.assertEqual(item_data["model"]["model"], "examplemod:item/emerald_sword")

    def test_build_merges_existing_language_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            build_assets(VALID_SPEC, output)
            second = json.loads(json.dumps(VALID_SPEC))
            second["minecraft"]["itemId"] = "emerald_gem"
            second["minecraft"]["displayName"] = {"en_us": "Emerald Gem"}
            build_assets(second, output)
            lang_file = output / "assets/examplemod/lang/en_us.json"
            lang_data = json.loads(lang_file.read_text(encoding="utf-8"))
            self.assertEqual(lang_data["item.examplemod.emerald_sword"], "Emerald Sword")
            self.assertEqual(lang_data["item.examplemod.emerald_gem"], "Emerald Gem")

    def test_item_id_rejects_path_traversal_segment(self):
        broken = json.loads(json.dumps(VALID_SPEC))
        broken["minecraft"]["itemId"] = "tools/../outside"
        with self.assertRaisesRegex(ValueError, "itemId"):
            validate_spec(broken)

    def test_locale_rejects_path_separator(self):
        broken = json.loads(json.dumps(VALID_SPEC))
        broken["minecraft"]["displayName"] = {"../zh_cn": "绿宝石剑"}
        with self.assertRaisesRegex(ValueError, "locale"):
            validate_spec(broken)


    def test_export_previews_writes_crisp_svg_and_nearest_neighbor_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            written = export_previews(VALID_SPEC, output, scale=8, white_background=True)
            svg = output / "emerald_sword.svg"
            png = output / "emerald_sword_32.png"
            self.assertEqual(set(written), {svg, png})
            self.assertIn('shape-rendering="crispEdges"', svg.read_text(encoding="utf-8"))
            self.assertIn('viewBox="0 0 4 4"', svg.read_text(encoding="utf-8"))
            self.assertEqual(read_png_size(png), (32, 32))

    def test_region_area_rule_rejects_single_pixel_when_enabled(self):
        broken = json.loads(json.dumps(VALID_SPEC))
        broken["canvas"]["minRegionArea"] = 2
        broken["pixels"] = ["....", ".G..", ".DD.", "...."]
        with self.assertRaisesRegex(ValueError, "region"):
            validate_spec(broken)

    def test_load_spec_reads_utf8_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "item.pixel.json"
            path.write_text(json.dumps(VALID_SPEC, ensure_ascii=False), encoding="utf-8")
            loaded = load_spec(path)
            self.assertEqual(loaded["minecraft"]["displayName"]["zh_cn"], "绿宝石剑")


def read_png_size(path: Path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("not a PNG")
    return struct.unpack(">II", data[16:24])


if __name__ == "__main__":
    unittest.main()
