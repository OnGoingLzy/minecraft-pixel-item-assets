# Minecraft Pixel Item Assets

[English](README.en.md) · [技能定义](SKILL.md) · [贡献指南](CONTRIBUTING.md) · [变更记录](CHANGELOG.md)

一个用于 Minecraft Java Edition 模组物品图标的 Codex 技能与零依赖生成工具。它以 `.pixel.json` 像素矩阵为唯一事实来源，确定性地生成透明 PNG 纹理、SVG 预览、物品模型 JSON、语言文件，以及适用于 Minecraft 1.21.4 及以上版本的物品定义 JSON。

![绿宝石剑像素预览](docs/examples/emerald_sword_512.png)

## 包含内容

- `SKILL.md`：智能体触发条件与工作流程。
- `scripts/mc_item_asset.py`：仅使用 Python 标准库的验证、预览与导出命令行工具。
- `assets/pixel-editor.html`：可离线运行的像素编辑器，可导出 `.pixel.json`、PNG 和 SVG。
- `assets/examples/emerald_sword.pixel.json`：完整的 16×16 示例。
- `references/`：像素 JSON 格式、设计规范和 Minecraft 版本矩阵。

## 安装为 Codex 技能

将整个目录复制到项目或用户的技能目录，然后在对话中使用：

```text
$minecraft-pixel-item-assets
```

示例提示词：

```text
$minecraft-pixel-item-assets 为我的 NeoForge 1.21.1 模组创建一个 16×16 的物品图标；modId 为 examplemod，物品 ID 为 emerald_sword，并生成到 src/main/resources。
```

## 快速开始

本项目不依赖第三方 Python 包。克隆后在仓库根目录执行：

```powershell
python scripts/mc_item_asset.py validate assets/examples/emerald_sword.pixel.json
python scripts/mc_item_asset.py preview assets/examples/emerald_sword.pixel.json --output build/pixel-preview --scale 32
python scripts/mc_item_asset.py build assets/examples/emerald_sword.pixel.json --output build/generated-resources
```

生成的资源位于 `build/generated-resources/assets/<modId>/`；普通物品默认使用 `minecraft:item/generated`，工具类物品使用 `minecraft:item/handheld`。Minecraft 1.21.4 及以上版本默认额外生成 `assets/<modId>/items/<itemId>.json`。

## 资源格式与质量要求

- 使用 16×16 或 32×32 的整数像素；背景必须透明，不可用白色替代透明。
- 不使用渐变、抗锯齿、模糊、滤镜或分数像素。
- 默认实色像素 alpha 为 `255`，空像素 alpha 为 `0`。
- 修改格式前请阅读 [像素 JSON 格式](references/pixel-json-schema.md)；设计前请阅读 [设计规范](references/design-rules.md)。
- 版本或资源布局不明确时，请参阅 [版本矩阵](references/version-matrix.md)。

## 验证

```powershell
python -m unittest discover -s tests -v
```

GitHub Actions 会在 Python 3.11 和 3.12 上执行示例的校验、预览和资源构建。

## 许可证说明

本仓库暂未提供 `LICENSE`。公开可浏览不表示已授予复制、修改、分发或商业使用的许可；如需复用，请先联系仓库维护者取得书面授权。
