# 工作流生成器 / Workflow Generator

> 交互式命令行工具，专为 UUP dump Windows ISO 构建定制，一键生成 GitHub Actions 工作流 yml 文件。
> Interactive CLI tool, tailored for UUP dump Windows ISO builds, generating GitHub Actions yml files in one shot.

## ✨ 功能特性 / Features

- 🖥️ **主菜单驱动** —— 3 项功能，简单直观
- 🌐 **中英双语** —— 启动参数或运行时一键切换（`zh` / `en`）
- 🎨 **彩色终端 UI** —— 基于 [rich](https://github.com/Textualize/rich) 库
- 🧙 **5 步交互式向导** —— 仿 UUPdumpWinISO 真实工作流步骤
- 🔍 **自动检测 UUP 脚本** —— 启动时扫描 `UUPdump script/`，单选后自动填充版本信息
- 🗺️ **Build 映射表** —— 内置 Win10 / Win11 / Windows Server 全部 build → 版本名映射（缺映射时自动回退兜底）
- ✅ **语法验证** —— PyYAML 反向解析，自动检查 yml 语法
- 📦 **单文件部署** —— 主程序就一个 Python 文件

## 📦 安装 / Installation

```powershell
# 1. 克隆仓库
git clone https://github.com/你的用户名/UUPdump_Workflow.git
cd UUPdump_Workflow

# 2. 安装依赖
pip install -r requirements.txt
```

依赖：
- [rich](https://github.com/Textualize/rich) >= 13.0
- [PyYAML](https://pyyaml.org/) >= 6.0

## 🚀 使用 / Usage

```powershell
# 启动主菜单（默认中文）
python workflow_generator.py

# 启动英文界面
python workflow_generator.py --lang en

# 跳过启动时自动检测 UUP 脚本
python workflow_generator.py --no-detect

# 查看帮助
python workflow_generator.py -h
```

## 📖 主菜单 / Main Menu

启动后显示如下界面（图为英文版，中文版对应翻译）：

```
╔══════════════════════════════════════╗
║     UUP Workflow Generator           ║
║     Tailored for UUP dump Windows... ║
║     Author: DHA404                  ║
╚══════════════════════════════════════╝
╭─────────── Main Menu ──────────╮
│  [1] Generate                  │
│  [2] Switch Language           │
│  [0] Exit                      │
╰───────────────────────────────╯
  Current language: English
Please choose [0-2]:
```

| 选项 | 功能 |
|------|------|
| `[1]` | 进入 UUP 向导生成 yml |
| `[2]` | 在中文 / English 之间切换 |
| `[0]` | 退出程序 |

## 🔍 启动时自动检测 / Startup Auto-Detect

每次启动时（如未指定 `--no-detect`），工具会自动扫描 `UUPdump script/` 下的子目录，从目录名提取元数据：

- **Build 编号**（正则 `26200\.8968`）
- **Windows 版本 + 补丁代号**（如 `Windows11` / `25H2`）
- **架构**（`amd64` / `x86` / `arm64`）

检测到脚本后弹出单选列表，确认后写入顶部"已确认脚本"行，并在向导的"工作流名称 / 版本号"两项中作为默认值。匹配 `build_mapping.py` 的 build 时直接给出标准版本名（如 `Windows11_25H2_amd64`）；未匹配时走兜底逻辑按目录名片段拼接。

```
━━━━ Detected UUP scripts ━━━━
  [[1]] 26200.8968_amd64_zh-cn_professional_6b4cc4c9_convert_virtual
       (FILE_NAME: Windows11_25H2_amd64, Build: 26200.8968)
  [[0]] Choose a script to use ([0] skip)
  > 1
```

## 🧙 向导流程 / Wizard Flow

选择 `[1] Generate` 后，向导按 5 步询问：

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

### 常见问题 / Troubleshooting

| 现象 | 可能原因 | 解决 |
|---|---|---|
| Actions 页签找不到 "Run workflow" 按钮 | yml 不在默认分支 / 缺少 `workflow_dispatch` | 推送到 `main` 分支 / 确认 `on: workflow_dispatch` 存在 |
| 触发后立即失败 | `actions/checkout@v5` 等 action 拉取失败 | 检查网络 / 代理；点击 "Re-run jobs" 重试 |
| Build ISO 步骤报错 "not recognized" | 未声明 `shell: cmd` | 本工具已自动加 `shell: cmd`；如手改过请确认 |
| 7z 步骤找不到 7z | Windows runner 未自带 7z | 本生成器假设已安装；如自建 runner 需先装 7-Zip |
| artifact 体积超限 | 单个 artifact 上限 10 GB | 已默认 `v1950m` 分卷；如仍超限改上传到 GitHub Release |
| 6 小时超时被打断 | 真实构建时间超过 360 分钟 | 修改生成的 yml 中 `timeout-minutes` 字段 |

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
# → ('Windows11', '25H2')

# 列出全部映射
python build_mapping.py --list
```

`workflow_generator.py` 通过 `from build_mapping import resolve_name` 集成该映射；缺失时静默降级为兜底命名。

## ✅ 验证 / Verification

```powershell
# 单元测试（10 项）
python -m pytest test_workflow_generator.py -v

# 端到端冒烟测试
python e2e_test.py
```

## ⚠️ 限制 / Limitations

- 仅支持基础 GitHub Actions 字段（`name` / `on` / `jobs` / `runs-on` / `steps` / `env` / `timeout-minutes`）
- 高级字段（`matrix` / `secrets` / `needs` / `reusable workflow`）需手写 yml
- 生成的步骤序列为固定 UUP 流程（Checkout → Build ISO → Package → Upload/Release），不自定义
- Windows 终端需 Windows 10+ 才能正确显示彩色（推荐 Windows Terminal）

## 🛠️ 项目结构 / Project Structure

```
UUPdump_Workflow/
├── workflow_generator.py     # 主程序（单文件 ~820 行）
├── build_mapping.py          # Build → 版本名映射表（独立可执行）
├── test_workflow_generator.py # 单元测试（10 项）
├── e2e_test.py               # 端到端冒烟测试
├── requirements.txt          # 依赖
├── .gitignore
├── README.md                 # 本文件
├── .github/
│   └── workflows/            # 生成的工作流输出目录
│       └── Windows11_25H2_amd64.yml
├── UUPdump script/           # 待打包的 UUP 脚本目录（启动时自动扫描）
│   └── 26200.8968_amd64_zh-cn_professional_6b4cc4c9_convert_virtual/
└── .example/                 # 参考项目（不影响主程序）
    └── UUPdumpWinISO-main/   # 真实 GitHub Actions 模板
```

##  许可证 / License

MIT

## 🙏 致谢 / Credits

- 字段参考：[UUPdumpWinISO](https://github.com/UUPdumpWinISO) 项目的 yml 模板
- GitHub Actions 官方文档：<https://docs.github.com/en/actions>
- 产物管理参考：[actions/upload-artifact@v4](https://github.com/actions/upload-artifact) / [actions/download-artifact@v4](https://github.com/actions/download-artifact)
- 终端 UI：[rich](https://github.com/Textualize/rich)
- YAML 解析：[PyYAML](https://pyyaml.org/)
