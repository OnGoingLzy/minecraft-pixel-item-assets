# Minecraft Pixel Item Assets GitHub Repository Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a public, independently verifiable GitHub-ready repository for the Minecraft Pixel Item Assets skill.

**Architecture:** Preserve the source skill as the operational core: `SKILL.md` directs agents to the standard-library Python generator, its templates, and reference material. Add repository-facing documentation, CI and generated example previews around that core without changing generator behavior.

**Tech Stack:** Markdown, GitHub Actions, Python 3.11/3.12, Python standard library.

## Global Constraints

- Keep `SKILL.md`, `scripts/`, `assets/`, `references/`, and `agents/` behaviorally unchanged from the source skill.
- Use Chinese as the primary documentation language and provide a complete English README.
- Add no `LICENSE` file; state the resulting no-license reuse boundary in both README files.
- CI and local validation must use only the Python standard library.
- Verify validation, preview, and build using `assets/examples/emerald_sword.pixel.json`.

---

### Task 1: Establish the repository and copy the skill core

**Files:**
- Create: `E:/workbench/minecraft-pixel-item-assets/.gitignore`
- Create: `E:/workbench/minecraft-pixel-item-assets/SKILL.md`
- Create: `E:/workbench/minecraft-pixel-item-assets/agents/openai.yaml`
- Create: `E:/workbench/minecraft-pixel-item-assets/assets/**`
- Create: `E:/workbench/minecraft-pixel-item-assets/references/**`
- Create: `E:/workbench/minecraft-pixel-item-assets/scripts/**`

**Consumes:** `C:/Users/Administrator/.codex/skills/minecraft-pixel-item-assets/**`.

**Produces:** A Git repository whose skill generator can be invoked with `python scripts/mc_item_asset.py`.

- [ ] **Step 1: Initialise the repository and copy only runtime skill files**

Run:

```powershell
git init E:/workbench/minecraft-pixel-item-assets
Copy-Item -Recurse -Force C:/Users/Administrator/.codex/skills/minecraft-pixel-item-assets/agents E:/workbench/minecraft-pixel-item-assets/
Copy-Item -Recurse -Force C:/Users/Administrator/.codex/skills/minecraft-pixel-item-assets/assets E:/workbench/minecraft-pixel-item-assets/
Copy-Item -Recurse -Force C:/Users/Administrator/.codex/skills/minecraft-pixel-item-assets/references E:/workbench/minecraft-pixel-item-assets/
Copy-Item -Recurse -Force C:/Users/Administrator/.codex/skills/minecraft-pixel-item-assets/scripts E:/workbench/minecraft-pixel-item-assets/
Copy-Item -Force C:/Users/Administrator/.codex/skills/minecraft-pixel-item-assets/SKILL.md E:/workbench/minecraft-pixel-item-assets/
```

- [ ] **Step 2: Create an ignore file for generated and local files**

```gitignore
__pycache__/
*.py[cod]
.venv/
build/
dist/
.DS_Store
Thumbs.db
```

- [ ] **Step 3: Verify the copied source inventory**

Run: `rg --files E:/workbench/minecraft-pixel-item-assets`

Expected: `SKILL.md`, the generator script, all four templates, three reference documents, pixel editor and emerald sword example are present.

- [ ] **Step 4: Commit the preserved skill core**

```powershell
git -C E:/workbench/minecraft-pixel-item-assets add SKILL.md agents assets references scripts .gitignore
git -C E:/workbench/minecraft-pixel-item-assets commit -m "chore: import pixel item asset skill"
```

### Task 2: Write repository-facing bilingual documentation

**Files:**
- Create: `E:/workbench/minecraft-pixel-item-assets/README.md`
- Create: `E:/workbench/minecraft-pixel-item-assets/README.en.md`
- Create: `E:/workbench/minecraft-pixel-item-assets/CONTRIBUTING.md`
- Create: `E:/workbench/minecraft-pixel-item-assets/CHANGELOG.md`

**Consumes:** Generator CLI documented by `SKILL.md`; example at `assets/examples/emerald_sword.pixel.json`.

**Produces:** Installation, usage, format, contribution, changelog and no-license guidance for GitHub visitors.

- [ ] **Step 1: Document exactly these local commands in both README files**

```powershell
python scripts/mc_item_asset.py validate assets/examples/emerald_sword.pixel.json
python scripts/mc_item_asset.py preview assets/examples/emerald_sword.pixel.json --output build/pixel-preview --scale 32
python scripts/mc_item_asset.py build assets/examples/emerald_sword.pixel.json --output build/generated-resources
```

- [ ] **Step 2: State the no-license boundary in both README files**

Use this meaning in Chinese: `本仓库暂未提供 LICENSE。公开可浏览不表示已授予复制、修改、分发或商业使用的许可。` Use this meaning in English: `No LICENSE is currently provided. Public visibility does not grant permission to copy, modify, distribute, or use this work commercially.`

- [ ] **Step 3: Write contribution and changelog files**

`CONTRIBUTING.md` must require original pixel artwork, deterministic output checks and a direct invocation of `validate`. `CHANGELOG.md` must contain an `Unreleased` heading and a `0.1.0` entry describing the initial public repository packaging.

- [ ] **Step 4: Check Markdown links and commands**

Run: `rg -n "python scripts/mc_item_asset.py|LICENSE|README.en.md|CONTRIBUTING.md" E:/workbench/minecraft-pixel-item-assets/README.md E:/workbench/minecraft-pixel-item-assets/README.en.md`

Expected: Both README files expose the three commands and no-license statement.

- [ ] **Step 5: Commit documentation**

```powershell
git -C E:/workbench/minecraft-pixel-item-assets add README.md README.en.md CONTRIBUTING.md CHANGELOG.md
git -C E:/workbench/minecraft-pixel-item-assets commit -m "docs: add bilingual repository guides"
```

### Task 3: Generate a checked-in preview and CI validation

**Files:**
- Create: `E:/workbench/minecraft-pixel-item-assets/docs/examples/emerald_sword-preview.png`
- Create: `E:/workbench/minecraft-pixel-item-assets/docs/examples/emerald_sword-preview.svg`
- Create: `E:/workbench/minecraft-pixel-item-assets/.github/workflows/validate.yml`
- Modify: `E:/workbench/minecraft-pixel-item-assets/README.md`
- Modify: `E:/workbench/minecraft-pixel-item-assets/README.en.md`

**Consumes:** The example spec and `scripts/mc_item_asset.py` commands from Tasks 1–2.

**Produces:** A visible PNG/SVG example and GitHub CI executing validation, preview and build on Python 3.11 and 3.12.

- [ ] **Step 1: Generate the human-review preview**

Run:

```powershell
python E:/workbench/minecraft-pixel-item-assets/scripts/mc_item_asset.py preview E:/workbench/minecraft-pixel-item-assets/assets/examples/emerald_sword.pixel.json --output E:/workbench/minecraft-pixel-item-assets/docs/examples --scale 32
```

Expected: A transparent PNG and crisp SVG preview named for `emerald_sword` in `docs/examples/`.

- [ ] **Step 2: Create a matrix CI workflow**

```yaml
name: Validate pixel assets
on:
  push:
  pull_request:
jobs:
  validate:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: python scripts/mc_item_asset.py validate assets/examples/emerald_sword.pixel.json
      - run: python scripts/mc_item_asset.py preview assets/examples/emerald_sword.pixel.json --output build/pixel-preview --scale 32
      - run: python scripts/mc_item_asset.py build assets/examples/emerald_sword.pixel.json --output build/generated-resources
```

- [ ] **Step 3: Embed the preview in both README files**

Add `![Emerald sword pixel preview](docs/examples/emerald_sword-preview.png)` to each README near the usage example.

- [ ] **Step 4: Run the same three CI commands locally**

Run:

```powershell
Set-Location E:/workbench/minecraft-pixel-item-assets
python scripts/mc_item_asset.py validate assets/examples/emerald_sword.pixel.json
python scripts/mc_item_asset.py preview assets/examples/emerald_sword.pixel.json --output build/pixel-preview --scale 32
python scripts/mc_item_asset.py build assets/examples/emerald_sword.pixel.json --output build/generated-resources
```

Expected: all commands exit `0`; `build/generated-resources/assets/demo_mod/textures/item/emerald_sword.png`, model JSON and item-definition JSON exist.

- [ ] **Step 5: Parse all generated JSON and inspect the PNG signature**

Run:

```powershell
Get-ChildItem build/generated-resources -Recurse -Filter *.json | ForEach-Object { Get-Content -Raw $_ | ConvertFrom-Json | Out-Null }
$signature = [System.IO.File]::ReadAllBytes('build/generated-resources/assets/demo_mod/textures/item/emerald_sword.png')[0..7]
if ([System.BitConverter]::ToString($signature) -ne '89-50-4E-47-0D-0A-1A-0A') { throw 'Invalid PNG signature' }
```

- [ ] **Step 6: Commit preview and CI**

```powershell
git -C E:/workbench/minecraft-pixel-item-assets add .github docs/examples README.md README.en.md
git -C E:/workbench/minecraft-pixel-item-assets commit -m "ci: validate example asset matrix"
```
