import unittest
from pathlib import Path

from scripts.mc_item_asset import load_spec, validate_spec

ROOT = Path(__file__).resolve().parents[1]


class PackageStructureTests(unittest.TestCase):
    def test_required_skill_files_exist(self):
        required = [
            "SKILL.md",
            "README.md",
            "agents/openai.yaml",
            "assets/icon.svg",
            "assets/pixel-editor.html",
            "assets/examples/emerald_sword.pixel.json",
            "references/pixel-json-schema.md",
            "references/version-matrix.md",
            "references/design-rules.md",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_skill_frontmatter_is_discoverable(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: minecraft-pixel-item-assets\n"))
        self.assertIn("description: Use when", text)
        self.assertIn("scripts/mc_item_asset.py", text)

    def test_example_spec_is_valid(self):
        spec = load_spec(ROOT / "assets/examples/emerald_sword.pixel.json")
        validate_spec(spec)
        self.assertEqual(spec["canvas"]["width"], 16)
        self.assertEqual(spec["canvas"]["height"], 16)

    def test_editor_has_png_svg_and_json_exports(self):
        text = (ROOT / "assets/pixel-editor.html").read_text(encoding="utf-8")
        for token in ("exportPng", "exportSvg", "exportJson", "imageSmoothingEnabled"):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
