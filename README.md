# UUP 工作流生成器 / UUP Workflow Generator

> 交互式命令行工具，为 **UUP dump Windows ISO 构建** 量身定制，一键生成 GitHub Actions 工作流 yml 文件。
> Interactive CLI tool for **UUP dump Windows ISO builds**. Generates a GitHub Actions workflow yml in one shot.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()

---

## 目录 / Contents

- [它做什么](#它做什么)
- [功能特性 / Features](#功能特性--features)
- [环境要求 / Requirements](#环境要求--requirements)
- [安装 / Installation](#安装--installation)
- [使用 / Usage](#使用--usage)
- [主菜单 / Main Menu](#主菜单--main-menu)
- [高级选项 / Advanced Options](#高级选项--advanced-options)
- [自动检测 / Auto-Detect](#自动检测--auto-detect)
  - [检测语言](#检测语言)
  - [检测 UUP 脚本](#检测-uup-脚本)
- [向导流程 / Wizard Flow](#向导流程--wizard-flow)
- [Build 映射表 / Build Mapping](#build-映射表--build-mapping)
- [生成的工作流 / Generated Workflow](#生成的工作流--generated-workflow)
- [运行工作流 / Run the Workflow](#运行工作流--run-the-workflow)
- [项目结构 / Project Structure](#项目结构--project-structure)
- [常见问题 / FAQ](#常见问题--faq)
- [限制 / Limitations](#限制--limitations)
- [本地测试 / Local Tests](#本地测试--local-tests)
- [贡献 / Contributing](#贡献--contributing)
- [许可证 / License](#许可证--license)
- [致谢 / Credits](#致谢--credits)

---

## 它做什么

把 `UUPdump_script/` 里 UUP dump 下载好的脚本目录，生成一个可在 GitHub Actions 上运行的 `yml` 工作流。这个工作流在云端下载 UUP 文件、转换成 Windows ISO、按 7z 分卷压缩后上传到产物。

不需要手动写 yml，也基本不用改配置。启动后多数步骤直接回车用默认值。

## 功能特性 / Features

- **主菜单驱动**——生成 / 切语言 / 高级选项 / 退出，四个选项
- **中英双语 + 自动检测**——按 `LC_ALL` / `LANG` / `LANGUAGE` / Windows API 自动判断界面语言；可覆盖或关闭
- **彩色终端界面**——基于 [rich](https://github.com/Textualize/rich)，中英文自适应
- **5 步交互式向导**——参考 [UUPdumpWinISO](https://github.com/UUPdumpWinISO) 的真实工作流步骤
- **自动检测 UUP 脚本**——扫描 `UUPdump_script/`，识别 build、架构、**语言**，自动填充名称与版本号
- **Build 映射表**——内置 Win10 / Win11 / Windows Server 的 build→版本名映射，识别 26H1 / 26H2 系列，缺映射时自动兜底
- **区分 Windows Server 2025**——build 26100 同时被 Win11 24H2 和 Server 2025 使用，工具会读 UUP 脚本内容自动区分
- **CI 运行时修复**——在工作流里给生成的 UUP 脚本自动打补丁，修掉官方脚本的几处缺陷（见下）
- **高级选项 / 步骤选择器**——6 个内置步骤模板，可多选、排序、加自定义步骤
- **语法验证**——用 PyYAML 反向解析，保存前先检查语法

### 生成的 ISO 构建对官方 UUP 脚本做了什么

UUP dump 官方生成的 `uup_download_windows.cmd` 有几处已知缺陷，本工具在工作流的 Build ISO 步骤里自动修复：

1. `goto` 后面的 `exit /b 1` 是死代码（`goto` 不返回，后面代码跑不到）
2. 获取下载脚本的接口没有超时参数，网络卡住时假死好几分钟
3. Store Apps（应用列表）下载失败会整体退出，导致最终只产出一个空包——现在碰到这种情况会跳过应用，继续构建系统 ISO

改写是幂等的：对已经正常的脚本不会产生改动。

## 环境要求 / Requirements

| 项目 | 要求 |
|------|------|
| Python | **3.8+**（推荐 3.10+） |
| 依赖 | [rich](https://github.com/Textualize/rich) >= 13.0、[PyYAML](https://pyyaml.org/) >= 6.0 |
| 操作系统 | Windows 10+ / Linux / macOS（终端支持 UTF-8 + ANSI 即可） |
| 网络 | 首次安装需要联网（`pip install`） |
| 磁盘 | < 5 MB |

> Windows 用户建议用 [Windows Terminal](https://aka.ms/terminal) 显示中文和颜色；旧版 `cmd.exe` 能跑，但颜色可能失真。

## 安装 / Installation

```powershell
git clone https://github.com/你的用户名/UUPdump_Workflow.git
cd UUPdump_Workflow

# （可选）创建虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1     # Windows PowerShell
# source .venv/bin/activate      # Linux / macOS

pip install -r requirements.txt
```

依赖：`rich>=13.0`、`PyYAML>=6.0`。

## 使用 / Usage

### 最简启动

```powershell
python workflow_generator.py
```

启动后自动检测语言（默认中文），扫描 `UUPdump_script/`，进主菜单。

### 完整 CLI 开关

| 参数 | 默认 | 说明 |
|------|------|------|
| `--lang {zh,en}` | 自动检测 | 强制界面语言 |
| `--no-detect` | 关闭 | 跳过启动时的 UUP 脚本扫描 |
| `--no-auto-lang` | 关闭 | 关闭自动语言检测（回退到中文） |
| `-h` / `--help` | — | 帮助 |

```powershell
python workflow_generator.py --lang en        # 强制英文
python workflow_generator.py --no-detect      # 不扫描 UUP 脚本
python workflow_generator.py --no-auto-lang   # 关闭自动语言检测
```

`build_mapping.py` 可单独当查询工具用：

```powershell
python build_mapping.py           # 打印全部 build 映射
python build_mapping.py 26200     # → Windows11_25H2
python build_mapping.py 26100     # → Windows11_24H2 (also: WindowsServer2025)
python build_mapping.py 99999     # → Unknown build 99999
```

## 主菜单 / Main Menu

启动后是这样一个界面（英文版示例，中文版对应翻译）：

```
╔══════════════════════════════════════════╗
║     UUP Workflow Generator               ║
║     Tailored for UUP dump Windows...     ║
║     Author: DHA404                       ║
╚══════════════════════════════════════════╝
╭─────────── Main Menu ────────────╮
│  [1] Generate                    │
│  [2] Switch Language             │
│  [3] Advanced Options (currently: OFF)   │
│  [0] Exit                        │
╰──────────────────────────────────╯
  Current language: English
Please choose [0-3]:
```

| 选项 | 功能 |
|------|------|
| `[1]` | 进入向导生成 yml |
| `[2]` | 中 / 英文切换 |
| `[3]` | 开/关高级选项（本次会话有效） |
| `[0]` | 退出 |

> 高级选项默认关闭，向导走固定 4 步序列（Checkout → Build ISO → Package → Upload/Release）。开启后第 0 步插入「步骤选择器」。

## 高级选项 / Advanced Options

主菜单按 `[3]` 开关（仅当前会话有效，不写配置文件）。开启后向导第 0 步是步骤选择器，内置 6 个模板：

| # | 模板 | 说明 |
|---|------|------|
| 1 | 拉取代码 | `actions/checkout@v5` |
| 2 | 构建 ISO | `shell: cmd` + `uup_download_windows.cmd`（含自动补丁） |
| 3 | 7z 分卷压缩 | `7z a -v1950m ... -mx=0`（仅存储切分，不压缩，解压快） |
| 4 | 上传工作流产物 | `actions/upload-artifact@v4` |
| 5 | 发布到 GitHub Release | `softprops/action-gh-release@v2` |
| 6 | 自定义步骤 | 手动输入 `uses` / `run` / `shell` |

流程：`[3]` 开 → `[1]` 进向导 → 第 0 步多选编号（空格 / 英文逗号 / 中文逗号都行，如 `1 2 3 4`；输入 `0` 或留空用默认 4 步）→ 可调整顺序 → 若选了「自定义步骤」补填字段 → 完成第 1-5 步。

> 常见组合：`1 2 3`（只打包不上传）、`1 2 3 5`（直接发 Release）。

### 为什么 7z 用 `-mx=0`

ISO 里的 WIM/ESD 已经是压缩过的，7z 再压（`-mx=9`）几乎省不了体积，反而让打包和解压慢好几倍。`-mx=0` 只做分卷切分（每卷 1950MB，绕开 GitHub 单文件约 2GB 的限制），打包和解压都接近硬盘读写速度。如果对这点有疑问，看本文「生成的工作流」里的分卷说明。

## 自动检测 / Auto-Detect

### 检测语言

按以下优先级决定界面语言：

| 优先级 | 来源 | 示例 |
|--------|------|------|
| 1（最高） | CLI `--lang` | `--lang en` |
| 2 | 环境变量 `LC_ALL` / `LANG` / `LANGUAGE` | `LANG=zh_CN.UTF-8` |
| 3 | Windows API `GetUserDefaultUILanguage()` | 中文系统 |
| 4（兜底） | 硬编码中文 | — |

识别规则：`zh*` 算中文，`en*` 算英文，其他（如 `de_DE`、`ja_JP`）回退中文。用自动检测时启动会打印一行提示，比如「✔ 自动检测语言: 中文」。

### 检测 UUP 脚本

启动时（未指定 `--no-detect`）扫描 `UUPdump_script/`，从目录名提取：

- **Build 编号**（如 `26200.8968`）
- **架构**（`amd64` / `x86` / `arm64`）
- **语言**（如 `zh-cn`）

```
━━━━ Detected UUP scripts ━━━━
  [[1]] 26200.8968_amd64_zh-cn_professional_6b4cc4c9_convert_virtual
       (FILE_NAME: Windows11_25H2_amd64_zh-cn, Build: 26200.8968)
  [[0]] Choose a script to use ([0] skip)
  > 1
```

选中的脚本会作为向导里「工作流名称 / 版本号」的默认值，名称会带上语言后缀（如 `Windows11_26H1_amd64_zh-cn`）。build 匹配到 `build_mapping.py` 时给标准名；匹配不到就走兜底逻辑拼目录名。

## 向导流程 / Wizard Flow

`[1] Generate` 后按 5 步询问（高级模式 6 步，多第 0 步选择器）：

| # | 字段 | 说明 |
|---|------|------|
| 1 | 工作流名称 | 有检测信息时默认已是 `Windows11_26H1_amd64_zh-cn` 这种格式 |
| 2 | 版本号 | UUP dump 上的 Build 编号，如 `26100.8313` |
| 3 | 运行环境 | `windows-latest`（推荐）/ `windows-2022` |
| 4 | 超时（分钟） | 默认 `360`（6 小时） |
| 5 | 发布方式 | 仅上传 artifact / 同时发 Release / 不自动上传 |

完成后预览 yml，确认保存路径（默认 `.github/workflows/<name>.yml`，存在时会问是否覆盖），自动做语法校验。

## Build 映射表 / Build Mapping

| Build | 产品 | 别名 |
|-------|------|------|
| 22000 | Windows11 | 21H2 |
| 22621 | Windows11 | 22H2 |
| 22631 | Windows11 | 23H2 |
| 26100 | Windows11 / **WindowsServer2025** | 24H2 / — |
| 26200 | Windows11 | 25H2 |
| 26300 | Windows11 | 26H2 |
| 26340 | Windows11 | 26H2（Insider / Experimental） |
| 28000 | Windows11 | 26H1 |
| 28020 | Windows11 | 26H1（Insider / Experimental） |
| 10240 – 19045 | Windows10 | 1507 – 22H2 |
| 17763 | Windows10 / WindowsServer2019 | 1809 / — |
| 20348 / 20349 | WindowsServer2022 | — |
| 26280 | WindowsServer2025 | — |

说明：

- **build 26100 同时是 Win11 24H2 和 Windows Server 2025**。工具会读该脚本目录里的 `uup_download_windows.cmd`，看它请求的版本是服务器版还是客户端版（`edition=server*` 还是 `edition=professional...`），据此区分成 `Windows11_24H2` 或 `WindowsServer2025`。
- **26340、28020 是 Insider / Experimental 分支**，编号由 26300 / 28000 用启用包（eKB）递增而来，仍归到 26H2 / 26H1。
- 不在表内的 build 会走兜底命名（`Windows_<build>_<arch>`）。

## 生成的工作流 / Generated Workflow

向导生成的 yml 大致是这样：

```yaml
name: Windows11_26H1_amd64_zh-cn
on: workflow_dispatch
jobs:
  build:
    runs-on: windows-latest
    env:
      Build_VERSION: '26300.9539'
      FILE_NAME: Windows11_26H1_amd64_zh-cn
      UUP_DIR: UUPdump_script/26300.9539_amd64_zh-cn_professional_95cc0dd5_convert_virtual
    timeout-minutes: 360
    steps:
    - name: Checkout
      uses: actions/checkout@v5
    - name: Build ISO
      shell: cmd
      run: 'cd "${{ env.UUP_DIR }}"

        powershell -NoProfile -Command "$c=[IO.File]::ReadAllText(''uup_download_windows.cmd'');...设置超时...跳过Store Apps失败..."

        uup_download_windows.cmd'
    - name: Package
      run: 7z a -v1950m "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}.7z" "./${{ env.UUP_DIR }}/*.iso" -mx=0
    - name: Upload artifact
      uses: actions/upload-artifact@v4
      with:
        name: ${{ env.FILE_NAME }}-${{ env.Build_VERSION }}
        path: ${{ env.FILE_NAME }}-${{ env.Build_VERSION }}.7z*
```

要点：

- **Build ISO 步骤**在运行脚本前先用 PowerShell 打补丁（修死代码、加超时、Store Apps 失败跳过），对正常脚本无改动。
- **Package 用 `-mx=0` 分卷**：只切分不压缩，分卷每卷 1950MB，避免超过 GitHub 单文件上传限制，也省掉解压等待。
- **`FILE_NAME` 与 `UUP_DIR` 解耦**：`FILE_NAME` 管产物命名，`UUP_DIR` 指向脚本目录；检测到脚本目录时 `UUP_DIR` 填嵌套路径，否则退回 `FILE_NAME`。

### 产物是"套娃"压缩吗

构建完你下载的 artifact 是一个 zip，里面是多个 `*.7z.001 / .7z.002` 分卷，解压这些分卷才得到 ISO。有两层"外包"：

1. GitHub 上传 artifact 时额外打了一层 zip（平台行为，无法关闭）
2. Package 步骤的 7z 分卷（为绕开单文件大小限制，现在 `-mx=0` 不压缩，只切分）

取 ISO 的命令：

```bash
7z x artifact.zip -o./<name>-<build>/
7z x ./<name>-<build>/*.7z.001   # 自动拼接所有分卷
```

## 运行工作流 / Run the Workflow

从 yml 到拿到 ISO 的完整流程。

### 前置

- GitHub 账号 + 目标仓库的 **Write** 权限
- 本地已装 [git](https://git-scm.com/downloads)
- 已用本工具生成 yml

### 步骤 1：把代码放到 GitHub

**方式 A：Fork 现有项目**

```
1. 打开项目页 → 右上角 "Fork"
2. 本地克隆：git clone https://github.com/<user>/UUPdump_Workflow.git
3. 放入生成的 yml 到 .github/workflows/、UUP 脚本到 UUPdump_script/
4. 提交并推送
```

Fork 会带上上游的工作流，省去从零初始化。

**方式 B：从本地新建空仓库**

```powershell
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

### 步骤 2：触发

**方式 A：GitHub UI**

```
仓库 → Actions → 选 workflow → Run workflow → 选 main → Run workflow
```

`workflow_dispatch` 的 yml 必须放在默认分支（`main`），否则 Actions 页不会出现 "Run workflow"。

**方式 B：REST API**

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <PAT>" \
  https://api.github.com/repos/<user>/<repo>/actions/workflows/<name>.yml/dispatches \
  -d '{"ref":"main"}'
```

`<PAT>` 需要 `repo` + `workflow` 权限，返回 204 表示提交成功。

### 步骤 3：监控

Actions → workflow → run → 展开各 step 看日志。超时 360 分钟；UUP 下载 + ISO 转换通常 1-3 小时。

### 步骤 4：下载产物

| 方式 | 命令 / 路径 |
|---|---|
| 浏览器 | Actions → run → 底部 Artifacts → 下载 |
| `gh` CLI | `gh run download <run-id> --name <name>-<build>` |
| REST API | `GET /repos/{owner}/{repo}/actions/artifacts/{id}/zip` |

artifact 默认保留 90 天（公开仓库）/ 400 天（私有）。要永久保留，向导第 5 步选「同时发布到 GitHub Release」。

## 项目结构 / Project Structure

```
UUPdump_Workflow/
├── workflow_generator.py          # 主程序（i18n / 向导 / 高级选项 / 语言检测 / CI 补丁）
├── build_mapping.py               # Build → 版本名映射表（可独立查询）
├── test/
│   ├── test_workflow_generator.py # 单元测试（21 项）
│   └── e2e_test.py                # 端到端冒烟测试
├── requirements.txt               # 依赖
├── .gitignore
├── README.md                      # 本文件
├── .trae/documents/               # 实施计划与变更记录
├── .github/workflows/             # 生成的工作流输出目录
├── UUPdump_script/                # UUP dump 下载的脚本目录（启动时自动扫描）
└── .example/                      # 参考项目（不影响主程序）
```

## 常见问题 / FAQ

| # | 问题 | 解答 |
|---|------|------|
| 1 | 菜单是英文，怎么切中文？ | 主菜单按 `[2]`；或 `--lang zh` |
| 2 | 中文乱码？ | 设 `PYTHONIOENCODING=utf-8` 和 `PYTHONUTF8=1`，且终端支持 UTF-8 |
| 3 | Actions 找不到 "Run workflow"？ | yml 不在默认分支，或没有 `workflow_dispatch` → 推送到 `main` |
| 4 | 触发后立即失败？ | `actions/checkout@v5` 拉取失败 → 查网络 / 代理，重跑 |
| 5 | 7z 步骤找不到 7z？ | runner 没装 7-Zip；自建 runner 需先装 |
| 6 | artifact 体积超限？ | 已默认 `v1950m` 分卷；仍超就改发 GitHub Release |
| 7 | 构建出来的包是空的（0 文件）？ | 通常是 Store Apps 下载失败导致旧版脚本退出；新版本已自动跳过应用、继续构建 ISO。若仍为空，看 CI 日志里是否 `WU_REQUEST_FAILED`，并确认 `UUP_DIR` 正确 |
| 8 | 构建卡在 "Retrieving aria2 script for Microsoft Store Apps"？ | `uupdump.net` 的动态接口在你的网络下被干扰：给脚本头部设 `set "all_proxy=..."` 走代理，或干脆放 CI 上跑 |
| 9 | build 不在映射表内？ | 自动回退 `Windows_<build>_<arch>`；可在 [build_mapping.py](build_mapping.py) 补全 |
| 10 | 高级选项怎么用？ | 主菜单 `[3]` 开 → 向导第 0 步多选模板 |
| 11 | 报找不到路径？ | `UUP_DIR` 没指向脚本目录：确认 `env.UUP_DIR` 等于 `UUPdump_script/<dir_name>` |
| 12 | 7z 找不到 `*.iso`？ | ISO 在 `UUP_DIR` 目录内，7z 输入路径已自动用 `UUP_DIR` |

## 限制 / Limitations

- 只支持基础 GitHub Actions 字段（`name` / `on` / `jobs` / `runs-on` / `steps` / `env` / `timeout-minutes`）
- `matrix` / `secrets` / `needs` / 可复用工作流等高级字段需手写 yml
- 界面只支持中文 / English，其他 locale 回退中文
- 步骤模板只有 6 个内置，自定义步骤需在向导里填字段

## 本地测试 / Local Tests

```powershell
# 单元测试（21 项）
cd test
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
python test_workflow_generator.py

# 端到端冒烟测试
python e2e_test.py
```

## 贡献 / Contributing

1. Fork 本仓库
2. 建分支：`git checkout -b feature/my-feature`
3. 改完提交
4. 推分支，发 Pull Request

## 许可证 / License

[MIT](LICENSE)。

## 致谢 / Credits

- 字段参考：[UUPdumpWinISO](https://github.com/UUPdumpWinISO) 的 yml 模板
- GitHub Actions 官方文档：<https://docs.github.com/en/actions>
- 产物管理：[actions/upload-artifact@v4](https://github.com/actions/upload-artifact) / [actions/download-artifact@v4](https://github.com/actions/download-artifact)
- 发布：[softprops/action-gh-release@v2](https://github.com/softprops/action-gh-release)
- 终端 UI：[rich](https://github.com/Textualize/rich)
- YAML 解析：[PyYAML](https://pyyaml.org/)

---

**作者 / Author**：DHA404