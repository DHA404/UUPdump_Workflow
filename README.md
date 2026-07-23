# UUP 工作流生成器 / UUP Workflow Generator

> 交互式命令行工具，专为 **UUP dump Windows ISO 构建** 量身定制，一键生成 GitHub Actions 工作流 yml 文件。
> Interactive CLI tool, tailored for **UUP dump Windows ISO builds**, generating GitHub Actions workflow yml files in one shot.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()

---

## 📑 目录 / Table of Contents

- [✨ 功能特性 / Features](#-功能特性--features)
- [📦 环境要求 / Requirements](#-环境要求--requirements)
- [🚀 安装 / Installation](#-安装--installation)
- [💡 使用 / Usage](#-使用--usage)
- [🖥️ 主菜单 / Main Menu](#-主菜单--main-menu)
- [🆕 高级选项 / Advanced Options](#-高级选项--advanced-options)
- [🌐 自动语言检测 / Auto Language Detection](#-自动语言检测--auto-language-detection)
- [🔍 启动时自动检测脚本 / Startup Auto-Detect](#-启动时自动检测脚本--startup-auto-detect)
- [🧙 向导流程 / Wizard Flow](#-向导流程--wizard-flow)
- [🗺️ Build 映射表 / Build Mapping Table](#-build-映射表--build-mapping-table)
- [📝 生成示例 / Generated Example](#-生成示例--generated-example)
- [▶️ 运行工作流教程 / Run the Workflow](#-运行工作流教程--run-the-workflow)
- [🛠️ 项目结构 / Project Structure](#-项目结构--project-structure)
- [❓ 常见问题 / FAQ](#-常见问题--faq)
- [⚠️ 限制 / Limitations](#-限制--limitations)
- [🤝 贡献 / Contributing](#-贡献--contributing)
- [📜 许可证 / License](#-许可证--license)
- [🙏 致谢 / Credits](#-致谢--credits)

---

## ✨ 功能特性 / Features

- 🖥️ **主菜单驱动** —— 4 项功能，结构清晰（生成 / 切语言 / 高级选项 / 退出）
- 🌐 **中英双语 + 自动检测** —— 启动时按 `LC_ALL` / `LANG` / `LANGUAGE` / Windows API 自动判断；可显式覆盖或关闭
- 🎨 **彩色终端 UI** —— 基于 [rich](https://github.com/Textualize/rich) 库，Panel / Box / 颜色自适应
- 🧙 **5 步交互式向导** —— 仿 [UUPdumpWinISO](https://github.com/UUPdumpWinISO) 真实工作流步骤
- 🔍 **启动时自动检测 UUP 脚本** —— 扫描 `UUPdump script/`，单选后自动填充版本信息
- 🗺️ **Build 映射表** —— 内置 Win10 / Win11 / Windows Server 全部 build → 版本名映射（缺映射时自动回退兜底）
- ⚙️ **高级选项 / 步骤选择器** —— 6 个内置步骤模板，可多选 + 排序 + 自定义步骤，不选走默认 4 步序列
- ✅ **语法验证** —— PyYAML 反向解析，自动检查 yml 语法
- 📦 **单文件部署** —— 主程序仅一个 Python 文件
- 🪟 **跨平台** —— Windows / Linux / macOS 全兼容（仅 Windows 启用 API 检测）

## 📦 环境要求 / Requirements

| 项目 | 要求 |
|------|------|
| Python | **3.8+**（推荐 3.10+） |
| 依赖 | [rich](https://github.com/Textualize/rich) >= 13.0、[PyYAML](https://pyyaml.org/) >= 6.0 |
| 操作系统 | Windows 10+ / Linux / macOS（终端需支持 UTF-8 + ANSI 转义码） |
| 网络 | 首次安装需要联网（`pip install`） |
| 磁盘 | < 5 MB |

> **Windows 用户注意**：推荐使用 [Windows Terminal](https://aka.ms/terminal) 以正确显示中文与彩色；旧版 `cmd.exe` 也能运行但颜色可能失真。

## 🚀 安装 / Installation

```powershell
# 1. 克隆仓库
git clone https://github.com/你的用户名/UUPdump_Workflow.git
cd UUPdump_Workflow

# 2. （推荐）创建虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # Windows PowerShell
# source .venv/bin/activate      # Linux / macOS bash

# 3. 安装依赖
pip install -r requirements.txt
```

依赖：
- [rich](https://github.com/Textualize/rich) >= 13.0
- [PyYAML](https://pyyaml.org/) >= 6.0

## 💡 使用 / Usage

### 最简启动

```powershell
# 启动主菜单（自动检测语言 → 默认 zh）
python workflow_generator.py
```

### 完整 CLI 开关

| 参数 | 默认 | 说明 |
|------|------|------|
| `--lang {zh,en}` | **自动检测** | 强制界面语言（覆盖自动检测） |
| `--no-detect` | 关闭 | 跳过启动时自动扫描 `UUPdump script/` |
| `--no-auto-lang` | 关闭 | 关闭自动检测语言（回退到 zh） |
| `-h` / `--help` | — | 显示帮助信息 |

```powershell
# 示例
python workflow_generator.py                 # 启动 + 自动检测
python workflow_generator.py --lang en       # 强制英文
python workflow_generator.py --no-detect     # 跳过 UUP 脚本扫描
python workflow_generator.py --no-auto-lang  # 关闭自动语言检测
python workflow_generator.py -h              # 帮助
```

## 🖥️ 主菜单 / Main Menu

启动后显示如下界面（图为英文版，中文版对应翻译）：

```
╔══════════════════════════════════════════╗
║     UUP Workflow Generator               ║
║     Tailored for UUP dump Windows...     ║
║     Author: DHA404                      ║
╚══════════════════════════════════════════╝
╭─────────── Main Menu ────────────╮
│  [1] Generate                    │
│  [2] Switch Language             │
│  [3] Advanced Options (currently: OFF)  │
│  [0] Exit                        │
╰──────────────────────────────────╯
  Current language: English
Please choose [0-3]:
```

| 选项 | 功能 |
|------|------|
| `[1]` | 进入 UUP 向导生成 yml（5 步问答） |
| `[2]` | 在中文 / English 之间切换 |
| `[3]` | **开启/关闭高级选项**（影响本次会话） |
| `[0]` | 退出程序 |

> **关于高级选项**：默认 `OFF`，此时向导用固定的 4 步序列（Checkout → Build ISO → Package → Upload/Release）。开启后，向导第 0 步插入「步骤选择器」，可从 6 个模板中多选并调整顺序。

## 🆕 高级选项 / Advanced Options

通过主菜单 `[3]` 一键开启/关闭（**仅当前会话有效**，不写入配置文件）。

开启后，向导第 0 步弹出「步骤选择器」，内置 6 个 GitHub Actions 步骤模板：

| # | 模板 | 说明 | 用途 |
|---|------|------|------|
| 1 | **拉取代码** | `actions/checkout@v5` | 检出本仓库 |
| 2 | **构建 ISO** | `shell: cmd` + `uup_download_windows.cmd` | 调用 UUP 脚本生成 ISO |
| 3 | **7z 分卷压缩** | `7z a -v1950m ... -mx=9` | 最高级别压缩并分卷 |
| 4 | **上传工作流产物** | `actions/upload-artifact@v4` | 保留 90 / 400 天 |
| 5 | **发布到 GitHub Release** | `softprops/action-gh-release@v2` | 永久保留 + 对外分发 |
| 6 | **自定义步骤** | 手动输入 `uses` / `run` / `shell` | 任何 GitHub Actions 步骤 |

### 使用流程

1. 主菜单按 `[3]` 切换为 `ON`
2. 按 `[1]` 进入向导
3. **第 0 步：步骤选择器**
   - 输入多选编号（空格、英文逗号、中文逗号分隔均可），例：`1 2 3 4`
   - 输入 `0` 或留空 → **跳过，使用默认 4 步序列**
4. 提示「调整顺序」，可重新输入顺序编号，留空保持原序
5. 若选了模板 6「自定义步骤」，立即弹出 4 个字段输入框（`name` / `uses` / `run` / `shell`）
6. 继续完成第 1-5 步（名称 / 版本 / 运行环境 / 超时 / 发布方式）
7. 确认后生成 yml

> **典型用法**：小白用户保持 `OFF` 走默认序列；高级用户开启后可选 `1 2 3`（不要上传）或 `1 2 3 5`（直接发 Release，不保留 artifact）。

## 🌐 自动语言检测 / Auto Language Detection

启动时按以下优先级决定界面语言（**无需任何配置**）：

| 优先级 | 来源 | 示例 |
|--------|------|------|
| 1（最高） | CLI `--lang` 显式参数 | `python workflow_generator.py --lang en` |
| 2 | 环境变量 `LC_ALL` / `LANG` / `LANGUAGE`（POSIX 标准） | `LANG=zh_CN.UTF-8` |
| 3 | Windows API `GetUserDefaultUILanguage()` | Windows 中文系统 |
| 4（兜底） | 硬编码 `zh` | — |

当使用自动检测结果时，启动后会打印一行提示：

```
✔ 自动检测语言: 中文
✔ Auto-detected language: English
```

### 关闭自动检测

```powershell
python workflow_generator.py --no-auto-lang
```

### 支持的语言标识

- **中文**：`zh_CN.UTF-8` / `zh_TW` / `zh` / 任何 `zh*`
- **English**：`en_US.UTF-8` / `en_GB` / `en` / 任何 `en*`
- **其他**（如 `de_DE` / `ja_JP`）→ 返回 `None`，回退到中文

## 🔍 启动时自动检测脚本 / Startup Auto-Detect

每次启动时（如未指定 `--no-detect`），工具自动扫描 `UUPdump script/` 下的子目录，从目录名提取元数据：

- **Build 编号**（正则 `26200\.8968`）
- **Windows 版本 + 补丁代号**（如 `Windows11` / `25H2`）
- **架构**（`amd64` / `x86` / `arm64`）

检测到脚本后弹出单选列表，确认后写入顶部"已确认脚本"行，并在向导的"工作流名称 / 版本号"两项中作为默认值。匹配 `build_mapping.py` 时直接给出标准版本名（如 `Windows11_25H2_amd64`）；未匹配时走兜底逻辑按目录名片段拼接。

```
━━━━ Detected UUP scripts ━━━━
  [[1]] 26200.8968_amd64_zh-cn_professional_6b4cc4c9_convert_virtual
       (FILE_NAME: Windows11_25H2_amd64, Build: 26200.8968)
  [[0]] Choose a script to use ([0] skip)
  > 1
```

## 🧙 向导流程 / Wizard Flow

选择 `[1] Generate` 后，向导按 **5 步** 询问（高级模式为 6 步，含第 0 步步骤选择器）：

| # | 字段 | 说明 / Example |
|---|------|----------------|
| 1 | **工作流名称** | `Windows11_24H2_amd64`（有检测信息时显示"检测到的信息"） |
| 2 | **版本号 (Build_VERSION)** | `26100.8313`（UUP dump 上的 Build 编号） |
| 3 | **运行环境** | `windows-latest` (推荐) / `windows-2022` |
| 4 | **超时（分钟）** | 默认 `360`（6 小时，参考 UUPdumpWinISO 模板） |
| 5 | **发布方式** | 仅上传 artifact / 同时发布到 GitHub Release / 不自动上传 |

完成后：
- 终端预览生成的 yml
- 询问输出路径（默认 `.github/workflows/<name>.yml`，存在时确认是否覆盖）
- 自动用 PyYAML 验证语法
- 成功：✔ 显示路径；失败：✘ 显示错误

## 🗺️ Build 映射表 / Build Mapping Table

`build_mapping.py` 内置 Win10 / Win11 / Windows Server 全版本 build → 产品代号映射：

| Build | 产品 | 别名 |
|-------|------|------|
| 22000 | Windows11 | 21H2 |
| 22621 | Windows11 | 22H2 |
| 22631 | Windows11 | 23H2 |
| 26100 | Windows11 | 24H2 |
| 26200 | Windows11 | 25H2 |
| 26300 | Windows11 | 26H2 |
| 28000 | Windows11 | 26H1 |
| 10240 – 19045 | Windows10 | 1507 – 22H2 |
| 17763 | Windows10 / WindowsServer2019 | 1809 |
| 20348 / 20349 | WindowsServer2022 | — |
| 26280 | WindowsServer2025 | — |

单独运行可作查询工具：

```powershell
# 查询单个 build
python build_mapping.py 26200.8968
# → Windows11_25H2

# 查询 ambiguous build
python build_mapping.py 17763
# → Windows10_1809
# (also: WindowsServer2019)

# 列出全部映射
python build_mapping.py --list
```

`workflow_generator.py` 通过 `from build_mapping import resolve_name` 集成该映射；缺失时静默降级为兜底命名。

## 📝 生成示例 / Generated Example

向导生成的 yml 形如：

```yaml
name: Windows11_25H2_amd64
on: workflow_dispatch
jobs:
  build:
    runs-on: windows-latest
    env:
      Build_VERSION: '26200.8968'
      FILE_NAME: Windows11_25H2_amd64
    timeout-minutes: 360
    steps:
    - name: Checkout
      uses: actions/checkout@v5
    - name: Build ISO
      shell: cmd
      run: 'cd "${{ env.FILE_NAME }}"

        uup_download_windows.cmd'
    - name: Package
      run: 7z a -v1950m "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}.7z" "./${{ env.FILE_NAME }}/*.iso" -mx=9
    - name: Upload artifact
      uses: actions/upload-artifact@v4
      with:
        name: ${{ env.FILE_NAME }}-${{ env.Build_VERSION }}
        path: ${{ env.FILE_NAME }}-${{ env.Build_VERSION }}.7z*
```

> `shell: cmd` 与 `-mx=9` 与 `.example/UUPdumpWinISO-main` 真实工作流保持一致：CMD 显式声明确保 `.cmd` 脚本被正确执行；最高压缩级别减小 artifact 体积。

## ▶️ 运行工作流教程 / Run the Workflow

> 从生成 yml 到下载 ISO 镜像的 4 步完整流程。
> 4-step end-to-end flow: from yml generation to ISO download.

### 前置条件 / Prerequisites

- 拥有 GitHub 账号 + 对目标仓库的 **Write** 权限（手动触发 workflow 需要）
- 本地已安装 [git](https://git-scm.com/downloads)
- 已通过本工具生成 yml（参见上方「向导流程 / Wizard Flow」）

### 步骤 1：获取代码到 GitHub / Step 1: Get Code on GitHub

**方式 A：Fork 已有项目（推荐，最简单）**

如果本项目已在 GitHub 上发布（README 顶部克隆链接对应的仓库），直接 Fork：

```
1. 浏览器打开项目页（如 https://github.com/原作者/UUPdump_Workflow）
2. 右上角点 "Fork" 按钮 → 选自己的账号
3. 本地克隆自己的 fork：
   git clone https://github.com/<user>/UUPdump_Workflow.git
4. 把生成的 yml 放进 .github/workflows/、UUP 脚本放进 UUPdump script/
5. 提交并推送：
   git add .github/workflows/<name>.yml
   git add "UUPdump script/<dirname>"
   git commit -m "Add UUP workflow for <name>"
   git push
```

> Fork 后原项目的 `workflow_dispatch` yml 仍会同步到你的 fork，**省去从零创建仓库的全部初始化步骤**。这也是 GitHub 上游更新自动合并到 fork 的标准方式。

**方式 B：从本地新建仓库（无上游时）**

如果还没有对应的 GitHub 仓库，先去 GitHub 网站点 `+` → `New repository` 创建一个**空的**（不要勾选 README / .gitignore / license）仓库，然后回到本地项目根目录：

```powershell
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

### 步骤 2：触发 workflow_dispatch / Step 2: Trigger via workflow_dispatch

**方式 A：GitHub UI**

```
仓库页 → 上方 "Actions" 页签
       → 左侧列表选中 workflow 名（如 Windows11_25H2_amd64）
       → 右侧 "Run workflow" 下拉
       → 选择分支（默认 main）
       → 绿色 "Run workflow" 按钮
```

⚠️ **关键前提**：`workflow_dispatch` 触发的 yml **必须**位于默认分支（`main`）。如果在其他分支的 yml 写了 `on: workflow_dispatch`，Actions 页签不会出现 "Run workflow" 按钮（参考 [DispatchOps 模式](https://github.github.io/gh-aw/patterns/dispatchops/)）。

**方式 B：REST API（适合 CI 联动）**

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <PAT>" \
  https://api.github.com/repos/<user>/<repo>/actions/workflows/<name>.yml/dispatches \
  -d '{"ref":"main"}'
```

`<PAT>` 需 `repo` + `workflow` 权限。返回 204 表示提交成功。

### 步骤 3：监控运行 / Step 3: Monitor Progress

```
Actions → workflow 名 → 最新 run 列表 → 点击进入
       → 展开各 step（Checkout / Build ISO / Package / Upload artifact）
       → 右上 "Re-run jobs" → "Re-run all jobs" 可重跑
```

- **实时日志**：每步右上有 ⏵ 按钮可展开 100+ 行输出
- **超时 360 分钟**（6 小时）：参考 [UUPdumpWinISO](https://github.com/UUPdumpWinISO) 模板的安全值；UUP 下载 + ISO 转换通常 1-3 小时
- **windows-latest runner 配置**：约 2 vCPU / 7 GB RAM / 14 GB SSD

### 步骤 4：下载产物 / Step 4: Download Artifact

| 方式 | 命令 / 路径 | 适用场景 |
|---|---|---|
| 浏览器 UI | `Actions → run → 底部 Artifacts → 点击下载` | 偶发下载 |
| `gh` CLI | `gh run download <run-id> --name <name>-<build>` | 经常下载 |
| `curl` + 解压 | 见下方代码 | 脚本 / 远程机器 |
| REST API | `GET /repos/{owner}/{repo}/actions/artifacts/{id}/zip` | 自建工具 |

```bash
# curl 方式（产物名格式：<FILE_NAME>-<Build_VERSION>，如 Windows11_25H2_amd64-26200.8968）
curl -L -o artifact.zip \
  -H "Authorization: Bearer <PAT>" \
  https://api.github.com/repos/<user>/<repo>/actions/artifacts/<artifact-id>/zip

# 7z 分卷（artifact 内部是 *.7z.001 / *.7z.002 / ...）
7z x artifact.zip -o./<name>-<build>/
7z x ./<name>-<build>/*.7z.001   # 自动拼接所有分卷
```

> **保留期**：artifact 默认 90 天（公开仓库）/ 400 天（私有仓库）。如需永久保留，可在向导第 5 步选择"同时发布到 GitHub Release"。

## 🛠️ 项目结构 / Project Structure

```
UUPdump_Workflow/
├── workflow_generator.py          # 主程序（单文件 ~1200 行，含 i18n / 向导 / 高级选项 / 语言检测）
├── build_mapping.py               # Build → 版本名映射表（独立可执行，含 CLI 查询）
├── test/
│   └── test_workflow_generator.py # 单元测试（18 项）
├── e2e_test.py                    # 端到端冒烟测试
├── requirements.txt               # 依赖
├── .gitignore
├── README.md                      # 本文件
├── .trae/
│   └── documents/                 # 实施计划与状态归档
├── .github/
│   └── workflows/                 # 生成的工作流输出目录
│       └── Windows11_25H2_amd64.yml
├── UUPdump script/                # 待打包的 UUP 脚本目录（启动时自动扫描）
│   └── 26200.8968_amd64_zh-cn_professional_6b4cc4c9_convert_virtual/
└── .example/                      # 参考项目（不影响主程序）
    └── UUPdumpWinISO-main/        # 真实 GitHub Actions 模板
```

## ❓ 常见问题 / FAQ

| # | 问题 | 解答 |
|---|------|------|
| 1 | 启动后菜单是英文，怎么切中文？ | 主菜单按 `[2]` 切换；或 `python workflow_generator.py --lang zh` |
| 2 | `--lang en` 没生效？ | 拼写检查：`--lang en`（两个短横线 + 空格 + en） |
| 3 | 自动检测到的语言不对？ | 显式指定：`python workflow_generator.py --lang en`；或关闭自动检测：`--no-auto-lang` |
| 4 | Windows Terminal 中文显示乱码？ | 设置 `PYTHONIOENCODING=utf-8` 和 `PYTHONUTF8=1` |
| 5 | 生成的 yml 报 `not recognized`？ | 已自动加 `shell: cmd`；如手改过请确认 |
| 6 | Actions 页签找不到 "Run workflow" 按钮？ | yml 不在默认分支 / 缺少 `workflow_dispatch` → 推送到 `main` / 确认 `on: workflow_dispatch` |
| 7 | 触发后立即失败？ | `actions/checkout@v5` 拉取失败 → 检查网络 / 代理；点击 "Re-run jobs" 重试 |
| 8 | 7z 步骤找不到 7z？ | Windows runner 未自带 7z → 本生成器假设已安装；如自建 runner 需先装 7-Zip |
| 9 | artifact 体积超限？ | 单个 artifact 上限 10 GB → 已默认 `v1950m` 分卷；如仍超限改上传到 GitHub Release |
| 10 | 6 小时超时被打断？ | 真实构建时间超过 360 分钟 → 修改 yml 中 `timeout-minutes` 字段 |
| 11 | 想跳过 UUP 脚本自动检测？ | `python workflow_generator.py --no-detect` |
| 12 | Build 不在映射表内？ | 自动回退到 `Windows_<build>_<arch>` 格式兜底命名；可在 [build_mapping.py](build_mapping.py) 补全 |
| 13 | 高级选项怎么用？ | 主菜单按 `[3]` 开启 → 进入 `[1]` 向导第 0 步多选步骤模板 |
| 14 | 自定义步骤支持什么？ | 任意 `name` / `uses` / `run` / `shell` 组合（`uses` 和 `run` 至少填一个） |

## ⚠️ 限制 / Limitations

- 仅支持基础 GitHub Actions 字段（`name` / `on` / `jobs` / `runs-on` / `steps` / `env` / `timeout-minutes`）
- 高级字段（`matrix` / `secrets` / `needs` / `reusable workflow`）需手写 yml
- 语言仅支持中文 / English（其他 locale 走兜底中文）
- 步骤模板仅 6 个内置；自定义步骤需在向导中输入字段
- Windows 终端需 Windows 10+ 才能正确显示彩色（推荐 Windows Terminal）

## 🤝 贡献 / Contributing

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/my-feature`
3. 提交修改：`git commit -m "Add my feature"`
4. 推送分支：`git push origin feature/my-feature`
5. 在 GitHub 上发起 Pull Request

### 本地测试

```powershell
# 单元测试（18 项）
cd test
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
python test_workflow_generator.py

# 端到端冒烟测试
python e2e_test.py
```

## 📜 许可证 / License

本项目基于 [MIT](LICENSE) 许可证开源。

## 🙏 致谢 / Credits

- 字段参考：[UUPdumpWinISO](https://github.com/UUPdumpWinISO) 项目的 yml 模板
- GitHub Actions 官方文档：<https://docs.github.com/en/actions>
- 产物管理参考：[actions/upload-artifact@v4](https://github.com/actions/upload-artifact) / [actions/download-artifact@v4](https://github.com/actions/download-artifact)
- 发布参考：[softprops/action-gh-release@v2](https://github.com/softprops/action-gh-release)
- 终端 UI：[rich](https://github.com/Textualize/rich)
- YAML 解析：[PyYAML](https://pyyaml.org/)

---

**作者 / Author**：DHA404
