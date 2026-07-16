# Minecraft Pixel Item Assets：GitHub 发布整理规格

## 目标

将现有 `minecraft-pixel-item-assets` 技能整理为可公开浏览、可独立验证、适合推送 GitHub 的仓库，且不改变其资源生成行为。

## 范围

- 保留技能定义、Python 标准库生成器、模板、像素编辑器、参考资料和示例。
- 新增中文 README、英文 README、贡献指南、变更日志与 Git 忽略规则。
- 增加 GitHub Actions，在 Python 3.11、3.12 上对示例执行验证、预览和资源构建。
- 将由示例生成的预览图放在 `docs/examples/`，供 README 展示。

## 仓库结构

```text
SKILL.md
README.md
README.en.md
CONTRIBUTING.md
CHANGELOG.md
.gitignore
.github/workflows/validate.yml
agents/
assets/
references/
scripts/
docs/examples/
```

## 许可证边界

仓库不包含 `LICENSE`。README 必须明确：公开仓库不等同于授予开源许可证；除 GitHub 服务条款下的查看与分叉所必需的权限外，代码与素材不自动获得复制、修改或分发许可。

## 验收标准

1. `python scripts/mc_item_asset.py validate assets/examples/emerald_sword.pixel.json` 成功。
2. `preview` 可生成透明 PNG 与 SVG 预览。
3. `build` 可生成正确的纹理、模型、语言和 1.21.4+ 物品定义资源。
4. README 中的命令、目录和许可证说明与仓库内容一致。
5. CI 工作流与本地验证命令一致，并仅依赖 Python 标准库。
