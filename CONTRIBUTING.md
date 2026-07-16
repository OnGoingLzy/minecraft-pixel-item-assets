# 贡献指南

欢迎提交问题与改进建议。提交像素素材时，请确保作品为原创，不逐像素复制 Mojang 或其他作者的纹理。

## 提交前检查

1. `.pixel.json` 必须是源文件；PNG、SVG 与 Minecraft JSON 都应由它重新生成。
2. 图标使用整数像素、透明背景与有限调色板；不得加入模糊、渐变或抗锯齿。
3. 对新增或修改的示例执行：

```powershell
python scripts/mc_item_asset.py validate path/to/item.pixel.json
python scripts/mc_item_asset.py preview path/to/item.pixel.json --output build/pixel-preview --scale 32
python scripts/mc_item_asset.py build path/to/item.pixel.json --output build/generated-resources
python -m unittest discover -s tests -v
```

4. 不要提交 `build/`、`__pycache__/` 或本地虚拟环境内容。
5. 请在 PR 中说明 Minecraft 版本、加载器、`modId`、物品 ID 和模型父级的假设。

## 文档

面向使用者的新增文档优先使用中文；若修改 README，请同步更新英文版本。
