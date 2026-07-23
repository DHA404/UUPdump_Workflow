#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流生成器 - 交互式生成 GitHub Actions yml 文件
Workflow Generator - Interactively create GitHub Actions yml files

用法 / Usage:
    python workflow_generator.py                  # 启动主菜单 (default zh)
    python workflow_generator.py --lang en        # 启动英文界面
    python workflow_generator.py -h               # 查看帮助
"""
import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Windows 终端 ANSI 颜色支持
if sys.platform == "win32":
    os.system("")  # 触发 VT 模式

try:
    import yaml
    # PyYAML 默认按 YAML 1.1 解析，会把 on/off/yes/no 当布尔值
    # GitHub Actions 实际使用 YAML 1.2，这些是普通字符串
    # 移除 SafeLoader 的 bool 隐式解析器，让 on/off 保持字符串
    yaml.SafeLoader.yaml_implicit_resolvers = {
        k: [r for r in v if r[0] != "tag:yaml.org,2002:bool"]
        for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }
except ImportError:
    print("缺少 PyYAML 依赖，请运行: pip install -r requirements.txt")
    sys.exit(1)

# 可选依赖：build_mapping.py（缺失时静默降级，兜底逻辑正常工作）
try:
    from build_mapping import resolve_name  # type: ignore
except ImportError:
    resolve_name = None  # type: ignore

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich import box
except ImportError:
    print("缺少 rich 依赖，请运行: pip install -r requirements.txt")
    sys.exit(1)


# ============================================================
# i18n 翻译字典 / Internationalization Dictionary
# ============================================================
I18N: Dict[str, Dict[str, Any]] = {
    "zh": {
        # 应用标题
        "app.title": "UUP 工作流生成器",
        "app.subtitle": "为 UUP dump Windows ISO 构建量身定制",
        "app.author": "作者: DHA404",
        # 菜单
        "menu.title": "主菜单",
        "menu.item1": "[1] 开始生成",
        "menu.item2": "[2] 切换语言",
        "menu.item0": "[0] 退出",
        "menu.choose": "请选择",
        # 向导
        "wizard.name": "工作流名称",
        "wizard.name.help": "建议格式：Windows版本_架构\n例如：Windows11_24H2_amd64",
        "wizard.version": "版本号 (Build_VERSION)",
        "wizard.version.help": "UUP dump 上的 Build 编号\n例如：26100.8313",
        "wizard.runner": "运行环境",
        "wizard.timeout": "超时（分钟）",
        "wizard.timeout.help": "UUP 下载+ISO 转换通常需要 1-3 小时\n默认 360 分钟（6 小时）",
        "wizard.release": "发布方式",
        # 高级选项 - 菜单
        "menu.item3": "[3] 高级选项（当前：{state}）",
        "menu.state.on": "开启",
        "menu.state.off": "关闭",
        "menu.toggle_on": "✔ 高级选项: 开启",
        "menu.toggle_off": "✔ 高级选项: 关闭",
        # 高级选项 - 步骤选择器
        "wizard.steps": "步骤选择器",
        "wizard.steps.help": "多选步骤模板并调整顺序\n输入 0 跳过（使用默认 4 步）",
        "wizard.steps.reorder": "调整顺序（直接回车保持当前顺序）",
        "wizard.steps.custom.name": "自定义步骤名称",
        "wizard.steps.custom.uses": "`uses:` 字段（可留空）",
        "wizard.steps.custom.run": "`run:` 字段（可留空）",
        "wizard.steps.custom.shell": "`shell:` 字段（默认 cmd）",
        "wizard.steps.selected": "已选步骤",
        # 检测
        "detect.title": "检测到 UUP 脚本",
        "detect.choose": "选择要使用的脚本（【0】跳过）",
        "wizard.detected": "检测到的信息",
        "header.confirmed": "已确认脚本",
        # 选项
        "opts.runners": [
            "windows-latest",
            "windows-2022",
        ],
        "opts.release": [
            "仅上传到工作流产物 (Artifact)",
            "同时发布到 GitHub Release",
            "不自动上传",
        ],
        "opt.recommended": "推荐",
        # 语言
        "lang.current": "当前语言",
        "lang.zh": "中文",
        "lang.en": "English",
        "lang.choose": "选择语言",
        # 消息
        "msg.success": "生成成功",
        "msg.failed": "验证失败",
        "msg.overwrite": "文件已存在，是否覆盖？",
        "msg.output": "输出路径",
        "msg.preview": "预览",
        "msg.cancelled": "已取消",
        # 退出
        "goodbye": "再见！",
    },
    "en": {
        "app.title": "UUP Workflow Generator",
        "app.subtitle": "Tailored for UUP dump Windows ISO builds",
        "app.author": "Author: DHA404",
        "menu.title": "Main Menu",
        "menu.item1": "[1] Generate",
        "menu.item2": "[2] Switch Language",
        "menu.item0": "[0] Exit",
        "menu.choose": "Please choose",
        "wizard.name": "Workflow name",
        "wizard.name.help": "Format: WindowsVersion_Architecture\ne.g. Windows11_24H2_amd64",
        "wizard.version": "Version (Build_VERSION)",
        "wizard.version.help": "Build number from UUP dump\ne.g. 26100.8313",
        "wizard.runner": "Runner",
        "wizard.timeout": "Timeout (minutes)",
        "wizard.timeout.help": "UUP download+ISO conversion takes 1-3 hours\nDefault 360 min (6 hours)",
        "wizard.release": "Release type",
        # Advanced options - menu
        "menu.item3": "[3] Advanced Options (currently: {state})",
        "menu.state.on": "ON",
        "menu.state.off": "OFF",
        "menu.toggle_on": "✔ Advanced Options: ON",
        "menu.toggle_off": "✔ Advanced Options: OFF",
        # Advanced options - step selector
        "wizard.steps": "Step Selector",
        "wizard.steps.help": "Multi-select step templates and reorder\nEnter 0 to skip (use default 4 steps)",
        "wizard.steps.reorder": "Reorder (Enter to keep current order)",
        "wizard.steps.custom.name": "Custom step name",
        "wizard.steps.custom.uses": "`uses:` field (can be empty)",
        "wizard.steps.custom.run": "`run:` field (can be empty)",
        "wizard.steps.custom.shell": "`shell:` field (default cmd)",
        "wizard.steps.selected": "Selected steps",
        # 检测
        "detect.title": "Detected UUP scripts",
        "detect.choose": "Choose a script to use ([0] skip)",
        "wizard.detected": "Detected info",
        "header.confirmed": "Confirmed script",
        "opts.runners": [
            "windows-latest",
            "windows-2022",
        ],
        "opts.release": [
            "Upload artifact only",
            "Also publish to GitHub Release",
            "Skip upload",
        ],
        "opt.recommended": "Recommended",
        "lang.current": "Current language",
        "lang.zh": "Chinese",
        "lang.en": "English",
        "lang.choose": "Choose language",
        "msg.success": "Generated successfully",
        "msg.failed": "Validation failed",
        "msg.overwrite": "File exists, overwrite?",
        "msg.output": "Output path",
        "msg.preview": "Preview",
        "msg.cancelled": "Cancelled",
        "goodbye": "Goodbye!",
    },
}


# ============================================================
# I18n 类：多语言管理器
# ============================================================
class I18n:
    """多语言管理器，支持运行时热切换"""

    def __init__(self, default: str = "zh") -> None:
        self.lang: str = default if default in I18N else "zh"

    def t(self, key: str) -> Any:
        """翻译函数（支持 str 和 list），未找到时回退到中文，仍未找到返回 key"""
        primary = I18N.get(self.lang, I18N["zh"])
        if key in primary:
            return primary[key]
        fallback = I18N["zh"]
        if key in fallback:
            return fallback[key]
        return key

    def t_str(self, key: str) -> str:
        """保证返回 str 类型"""
        val = self.t(key)
        return str(val) if val is not None else key

    def t_list(self, key: str) -> List[str]:
        """返回 list[str]"""
        val = self.t(key)
        if isinstance(val, list):
            return [str(x) for x in val]
        return [str(val)]

    def switch(self, lang: str) -> bool:
        """切换语言，返回是否成功"""
        if lang in I18N:
            self.lang = lang
            return True
        return False

    def current(self) -> str:
        return self.lang


# ============================================================
# ScriptInfo：检测到的一个 UUP 脚本目录的元数据
# ============================================================
@dataclass
class ScriptInfo:
    """单个 UUP 脚本目录的元数据，由 ScriptDetector 解析得出"""
    dir_name: str                                # 原始目录名
    name: Optional[str] = None                   # 默认 FILE_NAME（Windows11_25H2_amd64 形式）
    build: Optional[str] = None                  # 默认 Build 编号（26200.8894 形式）


# ============================================================
# ScriptDetector：扫描 UUPdump script/ 目录，正则提取元数据
# ============================================================
class ScriptDetector:
    """扫描 `UUPdump script/` 下的一层子目录，正则提取 build/Windows 版本/架构"""

    BASE_DIR = Path("UUPdump script")
    # 5-6 位数字 . 4-5 位数字（用 lookaround 替代 \b，避免与下划线冲突）
    BUILD_RE = re.compile(r"(?:^|(?<=[^.\d]))(\d{5,}\.\d{4,})(?=[^.\d]|$)")
    # Windows10 / Windows11
    WIN_RE = re.compile(r"Windows(10|11)", re.IGNORECASE)
    # 25H2 / 22H2
    RELEASE_RE = re.compile(r"(\d{2})H(\d)", re.IGNORECASE)
    # amd64 / x86 / arm64（用 lookaround 排除字母/数字，下划线算分隔符）
    ARCH_RE = re.compile(r"(?<![a-zA-Z0-9])(amd64|x86|arm64)(?![a-zA-Z0-9])", re.IGNORECASE)

    def __init__(self, base: Optional[Path] = None) -> None:
        self.base = base if base is not None else self.BASE_DIR

    def scan(self) -> List[ScriptInfo]:
        """扫描 BASE_DIR 下的一层子目录，返回 ScriptInfo 列表"""
        if not self.base.exists() or not self.base.is_dir():
            return []
        infos: List[ScriptInfo] = []
        for d in sorted(self.base.iterdir()):
            if d.is_dir():
                infos.append(self._parse(d))
        return infos

    def _parse(self, d: Path) -> ScriptInfo:
        """从目录名提取元数据（优先查 build_mapping 映射表，失败走兜底逻辑）"""
        name_str = d.name
        build_m = self.BUILD_RE.search(name_str)
        arch_m = self.ARCH_RE.search(name_str)

        build = build_m.group(1) if build_m else None
        arch = arch_m.group(1) if arch_m else None

        # 优先查 build_mapping 映射表
        mapped: Optional[str] = None
        if build and resolve_name is not None:
            mapped = resolve_name(build, arch or "amd64", dir_name=name_str)

        if mapped:
            default_name = mapped
        else:
            # 兜底逻辑（原样保留）
            win_m = self.WIN_RE.search(name_str)
            rel_m = self.RELEASE_RE.search(name_str)
            windows_v = win_m.group(1) if win_m else None
            release = f"{rel_m.group(1)}H{rel_m.group(2)}" if rel_m else None

            if build and arch:
                default_name = f"Windows_{build}_{arch}"
            elif windows_v and release and arch:
                default_name = f"Windows{windows_v}_{release}_{arch}"
            elif windows_v and arch:
                default_name = f"Windows{windows_v}_{arch}"
            elif release and arch:
                default_name = f"Windows_{release}_{arch}"
            elif arch:
                default_name = f"Windows_{arch}"
            elif build:
                default_name = f"Windows_{build}"
            else:
                default_name = name_str.split(" ")[0] if name_str else "MyWorkflow"

        return ScriptInfo(
            dir_name=name_str,
            name=default_name,
            build=build,
        )

    def ask_user(self, i18n: "I18n", console: "Console") -> Optional[ScriptInfo]:
        """扫描并让用户单选，返回选中的 ScriptInfo 或 None（跳过/无）"""
        infos = self.scan()
        if not infos:
            return None

        console.print(
            f"\n[bold cyan]━━━━ {i18n.t_str('detect.title')} ━━━━[/bold cyan]"
        )
        for i, info in enumerate(infos, 1):
            build_str = info.build or "-"
            console.print(
                f"  [[{i}]] {info.dir_name}  "
                f"[dim](FILE_NAME: {info.name}, Build: {build_str})[/dim]"
            )
        console.print(
            f"  [dim][[0]] {i18n.t_str('detect.choose')}[/dim]"
        )
        try:
            choice = Prompt.ask("  >", default="1").strip()
            idx = int(choice)
        except (ValueError, EOFError):
            return None
        if idx == 0 or not (1 <= idx <= len(infos)):
            return None
        return infos[idx - 1]


# ============================================================
# StepTemplate：步骤模板，供「高级选项」中的步骤选择器使用
# ============================================================
@dataclass
class StepTemplate:
    """6 个内置 GitHub Actions 步骤模板之一（高级模式用）"""
    id: str                                # 模板 id（英文）
    name: str                              # 显示名（中文）
    description: str                       # 详细说明
    default_order: int                     # 在推荐序列中的默认位置

    def render(self) -> Dict[str, Any]:
        """渲染为 step dict（占位符为字面量 ${{ env.* }}）"""
        if self.id == "checkout":
            return {"name": "Checkout", "uses": "actions/checkout@v5"}
        if self.id == "build":
            return {
                "name": "Build ISO",
                "shell": "cmd",
                "run": (
                    'cd "${{ env.FILE_NAME }}"\n'
                    "uup_download_windows.cmd"
                ),
            }
        if self.id == "package":
            return {
                "name": "Package",
                "run": (
                    '7z a -v1950m "${{ env.FILE_NAME }}-'
                    '${{ env.Build_VERSION }}.7z" '
                    '"./${{ env.FILE_NAME }}/*.iso"'
                    ' -mx=9'
                ),
            }
        if self.id == "upload":
            return {
                "name": "Upload artifact",
                "uses": "actions/upload-artifact@v4",
                "with": {
                    "name": "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}",
                    "path": "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}.7z*",
                },
            }
        if self.id == "release":
            return {
                "name": "Release",
                "uses": "softprops/action-gh-release@v2",
                "with": {
                    "tag_name": "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}",
                    "files": "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}.7z*",
                },
            }
        if self.id == "custom":
            # custom 模板在 ask_user 阶段收集后渲染，不走 render
            raise NotImplementedError("custom 模板需在 ask_user 中预渲染")
        raise ValueError(f"未知模板 id: {self.id}")

    @staticmethod
    def all() -> List["StepTemplate"]:
        """返回 6 个内置模板"""
        return [
            StepTemplate("checkout", "拉取代码", "actions/checkout@v5", 1),
            StepTemplate("build",    "构建 ISO", "shell: cmd + uup_download_windows.cmd", 2),
            StepTemplate("package",  "7z 分卷压缩", "7z a -v1950m ... -mx=9", 3),
            StepTemplate("upload",   "上传工作流产物", "actions/upload-artifact@v4", 4),
            StepTemplate("release",  "发布到 GitHub Release", "softprops/action-gh-release@v2", 5),
            StepTemplate("custom",   "自定义步骤", "手动输入 uses / run / shell", 6),
        ]


# ============================================================
# YmlBuilder 类：yml 数据结构构建器
# ============================================================
class YmlBuilder:
    """构造 GitHub Actions yml 数据结构，最后用 PyYAML 序列化"""

    def __init__(self) -> None:
        self.data: Dict[str, Any] = {
            "name": "",
            "on": "workflow_dispatch",
            "jobs": {},
        }

    def set_name(self, name: str) -> "YmlBuilder":
        self.data["name"] = name
        return self

    def set_trigger(self, trigger: str) -> "YmlBuilder":
        """设置触发器（字符串形式：workflow_dispatch / push / pull_request / schedule / workflow_call）"""
        if trigger == "push":
            self.data["on"] = {"push": {"branches": ["main"]}}
        elif trigger == "pull_request":
            self.data["on"] = {"pull_request": {"branches": ["main"]}}
        elif trigger == "schedule":
            self.data["on"] = {"schedule": [{"cron": "0 2 * * 1"}]}
        else:
            self.data["on"] = trigger
        return self

    def add_job(
        self,
        job_id: str,
        runs_on: str,
        steps: List[Dict[str, Any]],
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> "YmlBuilder":
        """添加一个 job（字段顺序按 GitHub Actions 惯例：runs-on → env → timeout → steps）"""
        job: Dict[str, Any] = {}
        job["runs-on"] = runs_on
        if env:
            job["env"] = env
        if timeout is not None and timeout > 0:
            job["timeout-minutes"] = timeout
        job["steps"] = steps
        self.data["jobs"][job_id] = job
        return self

    def to_yaml(self) -> str:
        """序列化为 yml 文本（保留字段顺序）"""
        text = yaml.dump(
            self.data,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            indent=2,
            width=1000,
            default_style=None,
        )
        # PyYAML dumper 默认对 YAML 1.1 布尔关键字（on/off/yes/no）加引号
        # GitHub Actions 接受无引号形式更符合 YAML 1.2 习惯
        # 仅替换键名位置（行首或缩进后），避免影响含这些字符的 value
        import re
        text = re.sub(r"^(\s*)'on':", r"\1on:", text, flags=re.MULTILINE)
        text = re.sub(r"^(\s*)'off':", r"\1off:", text, flags=re.MULTILINE)
        return text

    def save(self, path: Path) -> tuple[bool, str]:
        """保存到文件并验证，返回 (成功, 消息)"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self.to_yaml(), encoding="utf-8")
        except OSError as e:
            return False, str(e)
        return self.validate(path)

    @staticmethod
    def validate(path: Path) -> tuple[bool, str]:
        """用 PyYAML 验证 yml 语法"""
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
            return True, ""
        except yaml.YAMLError as e:
            return False, str(e)
        except OSError as e:
            return False, str(e)


# ============================================================
# UUPWizard 类：UUP 专用交互式向导
# ============================================================
class UUPWizard:
    """UUP ISO 构建专用的引导式交互向导，纯小白也可用"""

    DEFAULT_NAME = "Windows11_24H2_amd64"
    DEFAULT_BUILD = "26100.8313"

    def __init__(
        self,
        i18n: I18n,
        console: Console,
        default_name: Optional[str] = None,
        default_build: Optional[str] = None,
        advanced: bool = False,
    ) -> None:
        self.i18n = i18n
        self.console = console
        # 默认值：如未指定则用内置示例
        self.default_name = default_name or self.DEFAULT_NAME
        self.default_build = default_build or self.DEFAULT_BUILD
        # 是否检测到非默认信息（用于决定是否显示"检测到的信息"行）
        self._has_detected_name = default_name is not None
        self._has_detected_build = default_build is not None
        # 高级选项：用户开启时，向导第 0 步插入步骤选择器
        self.advanced = advanced
        # 步骤选择器的结果（None = 用默认 4 步序列）
        self._selected_steps: Optional[List[Any]] = None

    def run(self) -> Optional[YmlBuilder]:
        """执行 5 步引导式问答，返回 YmlBuilder 或 None（用户取消）"""
        builder = YmlBuilder()

        # ── 第 0 步（仅高级模式）：步骤选择器 ──
        if self.advanced:
            self._selected_steps = self._ask_step_selector()
            # None = 用户跳过，走默认 4 步序列
            if not self._selected_steps:
                self._selected_steps = None

        # ── 第一步：工作流名称 ──
        self.console.print(
            f"\n[bold cyan]──── {self.i18n.t_str('wizard.name')} (1/5) ────[/bold cyan]"
        )
        self.console.print(f"[dim]{self.i18n.t_str('wizard.name.help')}[/dim]")
        if self._has_detected_name:
            self.console.print(
                f"[green]{self.i18n.t_str('wizard.detected')}: "
                f"{self.default_name}[/green]"
            )
        name = Prompt.ask("  >", default=self.default_name).strip()
        if not name:
            self.console.print(f"[red]{self.i18n.t_str('msg.cancelled')}[/red]")
            return None
        builder.set_name(name)
        # 固定触发器为 workflow_dispatch（UUP 专用）
        builder.set_trigger("workflow_dispatch")

        # ── 第二步：版本号 ──
        self.console.print(
            f"\n[bold cyan]──── {self.i18n.t_str('wizard.version')} (2/5) ────[/bold cyan]"
        )
        self.console.print(f"[dim]{self.i18n.t_str('wizard.version.help')}[/dim]")
        if self._has_detected_build:
            self.console.print(
                f"[green]{self.i18n.t_str('wizard.detected')}: "
                f"{self.default_build}[/green]"
            )
        version = Prompt.ask("  >", default=self.default_build).strip()
        if not version:
            version = self.default_build

        # ── 第三步：运行环境 ──
        runs_on = self._ask_choice(
            "wizard.runner", "opts.runners", recommended_indices=[0]
        )
        if runs_on is None:
            return None

        # ── 第四步：超时时间 ──
        self.console.print(
            f"\n[bold cyan]──── {self.i18n.t_str('wizard.timeout')} (4/5) ────[/bold cyan]"
        )
        self.console.print(f"[dim]{self.i18n.t_str('wizard.timeout.help')}[/dim]")
        try:
            timeout_str = Prompt.ask("  >", default="360").strip()
            timeout = int(timeout_str) if timeout_str else 360
        except ValueError:
            timeout = 360

        # ── 第五步：发布方式 ──
        release_choice = self._ask_choice(
            "wizard.release", "opts.release", recommended_indices=[0]
        )
        if release_choice is None:
            return None
        release_idx = self.i18n.t_list("opts.release").index(release_choice)

        # ── 自动构造 env ──
        env: Dict[str, str] = {
            "Build_VERSION": version,
            "FILE_NAME": name,
        }

        # ── 构造固定步骤 ──
        steps = self._build_steps(release_idx)

        # ── 确认信息 ──
        self._show_confirm(name, version, runs_on, timeout, release_idx, steps)

        if not Confirm.ask(
            f"\n[bold cyan]确认生成？[/bold cyan]", default=True
        ):
            self.console.print(f"[yellow]{self.i18n.t_str('msg.cancelled')}[/yellow]")
            return None

        builder.add_job("build", runs_on, steps, env=env, timeout=timeout)
        return builder

    def _build_steps(self, release_idx: int) -> List[Dict[str, Any]]:
        """构造步骤列表：高级模式用用户选择，否则用默认 4 步固定序列"""
        # 高级模式 + 用户已选步骤 → 用用户选择的模板
        if self.advanced and self._selected_steps:
            return [t.render() if hasattr(t, "render") else t for t in self._selected_steps]

        # 默认 4 步固定序列（保持现有行为）
        steps: List[Dict[str, Any]] = [
            {
                "name": "Checkout",
                "uses": "actions/checkout@v5",
            },
            {
                "name": "Build ISO",
                "shell": "cmd",
                "run": (
                    'cd "${{ env.FILE_NAME }}"\n'
                    "uup_download_windows.cmd"
                ),
            },
            {
                "name": "Package",
                "run": (
                    '7z a -v1950m "${{ env.FILE_NAME }}-'
                    '${{ env.Build_VERSION }}.7z" '
                    '"./${{ env.FILE_NAME }}/*.iso"'
                    ' -mx=9'
                ),
            },
        ]
        if release_idx == 0:
            # 仅上传 artifact
            steps.append({
                "name": "Upload artifact",
                "uses": "actions/upload-artifact@v4",
                "with": {
                    "name": "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}",
                    "path": "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}.7z*",
                },
            })
        elif release_idx == 1:
            # artifact + release
            steps.append({
                "name": "Upload artifact",
                "uses": "actions/upload-artifact@v4",
                "with": {
                    "name": "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}",
                    "path": "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}.7z*",
                },
            })
            steps.append({
                "name": "Release",
                "uses": "softprops/action-gh-release@v2",
                "with": {
                    "tag_name": "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}",
                    "files": "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}.7z*",
                },
            })
        # release_idx == 2: 不自动上传，steps 仅到 Package
        return steps

    def _ask_step_selector(self) -> Optional[List[Any]]:
        """高级模式第 0 步：6 模板多选 + 排序

        返回：有序的 StepTemplate 列表（含 custom 模板的预渲染 dict）
              或 None（用户输入 0/空 跳过，走默认 4 步序列）
        """
        templates = StepTemplate.all()
        # ── 1. 显示模板清单 ──
        self.console.print(
            f"\n[bold cyan]──── {self.i18n.t_str('wizard.steps')} (0/?) ────[/bold cyan]"
        )
        self.console.print(f"[dim]{self.i18n.t_str('wizard.steps.help')}[/dim]")
        for i, t in enumerate(templates, 1):
            self.console.print(
                f"  [cyan][[{i}]][/cyan] [bold]{t.name}[/bold]  "
                f"[dim]— {t.description}[/dim]"
            )

        # ── 2. 多选 ──
        try:
            raw = Prompt.ask(
                "  >",
                default="0",
            ).strip()
        except (EOFError, KeyboardInterrupt):
            return None

        if not raw or raw == "0":
            return None  # 跳过

        # 解析：支持空格、逗号、中文逗号分隔
        for sep in [",", "，", " "]:
            raw = raw.replace(sep, " ")
        tokens = [t for t in raw.split() if t]
        try:
            indices = sorted({int(t) for t in tokens})
        except ValueError:
            self.console.print(f"[red]✘ 输入格式错误[/red]")
            return None
        if not indices or any(i < 1 or i > 6 for i in indices):
            self.console.print(f"[red]✘ 编号越界（应为 1-6）[/red]")
            return None

        # ── 3. 排序（按输入顺序，可重排） ──
        # 用户的原始顺序（去重）
        order_input: List[int] = []
        for t in tokens:
            try:
                idx = int(t)
                if idx not in order_input:
                    order_input.append(idx)
            except ValueError:
                pass

        # 提示调整顺序
        selected_names = [templates[i - 1].name for i in order_input]
        self.console.print(
            f"\n[bold green]{self.i18n.t_str('wizard.steps.selected')}: "
            f"{' → '.join(selected_names)}[/bold green]"
        )
        self.console.print(f"[dim]{self.i18n.t_str('wizard.steps.reorder')}[/dim]")
        try:
            reorder_raw = Prompt.ask("  >", default="").strip()
        except (EOFError, KeyboardInterrupt):
            return None

        if reorder_raw:
            for sep in [",", "，", " "]:
                reorder_raw = reorder_raw.replace(sep, " ")
            reorder_tokens = [t for t in reorder_raw.split() if t]
            try:
                reorder = [int(t) for t in reorder_tokens]
                # 校验：必须是原 indices 的排列
                if sorted(reorder) == sorted(indices) and len(reorder) == len(indices):
                    order_input = reorder
                else:
                    self.console.print(
                        f"[yellow]⚠ 排序输入与原选择不一致，保持原顺序[/yellow]"
                    )
            except ValueError:
                self.console.print(
                    f"[yellow]⚠ 排序输入格式错误，保持原顺序[/yellow]"
                )

        # ── 4. 组装结果（含 custom 模板的预渲染） ──
        result: List[Any] = []
        for i in order_input:
            t = templates[i - 1]
            if t.id == "custom":
                # 立即收 4 个字段，直接生成 dict（不走 render）
                custom_dict = self._ask_custom_step()
                if custom_dict is None:
                    self.console.print(f"[yellow]⚠ 自定义步骤输入取消，回退到默认[/yellow]")
                    return None
                result.append(custom_dict)
            else:
                result.append(t)
        return result

    def _ask_custom_step(self) -> Optional[Dict[str, Any]]:
        """收集 custom 模板的 4 个字段（name / uses / run / shell）"""
        try:
            name = Prompt.ask(
                f"  [cyan]{self.i18n.t_str('wizard.steps.custom.name')}[/cyan]"
            ).strip()
        except (EOFError, KeyboardInterrupt):
            return None
        if not name:
            return None
        try:
            uses = Prompt.ask(
                f"  [cyan]{self.i18n.t_str('wizard.steps.custom.uses')}[/cyan]",
                default="",
            ).strip()
            run = Prompt.ask(
                f"  [cyan]{self.i18n.t_str('wizard.steps.custom.run')}[/cyan]",
                default="",
            ).strip()
            shell = Prompt.ask(
                f"  [cyan]{self.i18n.t_str('wizard.steps.custom.shell')}[/cyan]",
                default="cmd",
            ).strip() or "cmd"
        except (EOFError, KeyboardInterrupt):
            return None
        # uses / run 至少一个
        if not uses and not run:
            self.console.print(
                f"[red]✘ uses 和 run 至少填一个[/red]"
            )
            return None
        d: Dict[str, Any] = {"name": name}
        if uses:
            d["uses"] = uses
        if run:
            d["run"] = run
        if shell:
            d["shell"] = shell
        return d

    def _show_confirm(
        self,
        name: str,
        version: str,
        runs_on: str,
        timeout: int,
        release_idx: int,
        steps: List[Dict[str, Any]],
    ) -> None:
        """显示确认信息"""
        release_labels = self.i18n.t_list("opts.release")
        step_icons = {
            "Checkout": "拉取代码",
            "Build ISO": "运行 uup_download_windows.cmd",
            "Package": "7z 分卷压缩",
            "Upload artifact": "上传工作流产物",
            "Release": "发布到 GitHub Release",
        }
        lang = self.i18n.current()
        self.console.print(
            f"\n[bold cyan]════ {self.i18n.t_str('msg.preview')} ════[/bold cyan]"
        )
        self.console.print(f"  工作流名称: [bold]{name}[/bold]")
        self.console.print(f"  版本号:      [bold]{version}[/bold]")
        self.console.print(f"  运行环境:    [bold]{runs_on}[/bold]")
        self.console.print(f"  超时:        [bold]{timeout}[/bold] 分钟")
        self.console.print(f"  发布方式:    [bold]{release_labels[release_idx]}[/bold]")
        self.console.print(f"\n  [dim]步骤清单:[/dim]")
        for i, step in enumerate(steps, 1):
            sname = step.get("name", "")
            desc = step_icons.get(sname, "")
            self.console.print(f"    {i}. {sname} → {desc}")

    def _ask_choice(
        self,
        title_key: str,
        items_key: str,
        recommended_indices: Optional[List[int]] = None,
    ) -> Optional[str]:
        """显示选项列表让用户选，返回选中项或 None（取消）"""
        items = self.i18n.t_list(items_key)
        rec_set = set(recommended_indices or [])
        rec_label = self.i18n.t_str("opt.recommended")
        self.console.print(
            f"\n[bold cyan]──── {self.i18n.t_str(title_key)} (3/5) ────[/bold cyan]"
            if title_key == "wizard.runner"
            else
            f"\n[bold cyan]──── {self.i18n.t_str(title_key)} (5/5) ────[/bold cyan]"
            if title_key == "wizard.release"
            else
            f"\n[bold cyan]{self.i18n.t_str(title_key)}[/bold cyan]"
        )
        for i, item in enumerate(items):
            marker = ""
            if i in rec_set:
                marker = f" [bold green]({rec_label})[/bold green]"
            self.console.print(f"  [[{i + 1}]] {item}{marker}")
        self.console.print(
            f"  [dim][0] {self.i18n.t_str('msg.cancelled')}[/dim]"
        )
        try:
            idx_str = Prompt.ask("  >", default="1").strip()
            idx = int(idx_str)
        except (ValueError, EOFError):
            return None
        if idx == 0:
            return None
        if 1 <= idx <= len(items):
            return items[idx - 1]
        return items[0]


# ============================================================
# 主菜单
# ============================================================
def print_header(
    i18n: I18n,
    console: Console,
    confirmed: Optional[ScriptInfo] = None,
) -> None:
    """打印程序头部 Panel（含已确认脚本信息，如提供）"""
    title = i18n.t_str("app.title")
    subtitle = i18n.t_str("app.subtitle")
    author = i18n.t_str("app.author")
    body = (
        f"[bold cyan]{title}[/bold cyan]\n"
        f"[dim]{subtitle}[/dim]\n"
        f"[dim]{author}[/dim]"
    )
    if confirmed:
        body += (
            f"\n[bold green]✔ {i18n.t_str('header.confirmed')}:[/bold green] "
            f"[cyan]{confirmed.dir_name}[/cyan]"
        )
    console.print()
    console.print(
        Panel(
            body,
            border_style="cyan",
            box=box.DOUBLE,
            padding=(1, 2),
        )
    )


def print_menu(i18n: I18n, console: Console, advanced: bool = False) -> None:
    """打印主菜单（4 项，含高级选项开关状态）"""
    state = i18n.t_str("menu.state.on" if advanced else "menu.state.off")
    item3 = i18n.t_str("menu.item3").replace("{state}", state)
    menu_text = (
        f"  {i18n.t_str('menu.item1')}\n"
        f"  {i18n.t_str('menu.item2')}\n"
        f"  {item3}\n"
        f"  {i18n.t_str('menu.item0')}"
    )
    console.print(
        Panel(
            menu_text,
            title=f"[bold]{i18n.t_str('menu.title')}[/bold]",
            border_style="green",
            box=box.ROUNDED,
        )
    )
    lang_name = i18n.t_str(f"lang.{i18n.current()}")
    console.print(
        f"  [dim]{i18n.t_str('lang.current')}: [bold]{lang_name}[/bold][/dim]"
    )


def action_generate(
    i18n: I18n,
    console: Console,
    confirmed: Optional[ScriptInfo] = None,
    advanced: bool = False,
) -> None:
    """主菜单项 1：进入 UUP 向导生成 yml"""
    wizard = UUPWizard(
        i18n,
        console,
        default_name=confirmed.name if confirmed else None,
        default_build=confirmed.build if confirmed else None,
        advanced=advanced,
    )
    builder = wizard.run()
    if builder is None:
        return

    # 预览
    console.print(
        f"\n[bold cyan]━━━ {i18n.t_str('msg.preview')} ━━━[/bold cyan]"
    )
    console.print(
        Panel(builder.to_yaml(), border_style="dim", box=box.SIMPLE)
    )

    # 输出路径
    default_path = Path(f".github/workflows/{builder.data['name']}.yml")
    console.print(
        f"\n[bold]{i18n.t_str('msg.output')}[/bold]: [cyan]{default_path}[/cyan]"
    )

    if default_path.exists():
        if not Confirm.ask(f"  {i18n.t_str('msg.overwrite')}", default=False):
            console.print(f"[yellow]{i18n.t_str('msg.cancelled')}[/yellow]")
            return

    ok, msg = builder.save(default_path)
    if ok:
        console.print(
            f"[bold green]✔ {i18n.t_str('msg.success')}[/bold green] → {default_path}"
        )
    else:
        console.print(
            f"[bold red]✘ {i18n.t_str('msg.failed')}[/bold red]: {msg}"
        )


def action_switch_lang(i18n: I18n, console: Console) -> None:
    """主菜单项 2：切换语言"""
    new_lang = "en" if i18n.current() == "zh" else "zh"
    i18n.switch(new_lang)
    lang_name = i18n.t_str(f"lang.{new_lang}")
    console.print(
        f"\n[bold green]✔ {i18n.t_str('lang.current')}: {lang_name}[/bold green]"
    )


# ============================================================
# CLI 入口
# ============================================================
def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="工作流生成器 / Workflow Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例 / Example:\n"
               "  python workflow_generator.py             # 启动主菜单\n"
               "  python workflow_generator.py --lang en   # 英文界面\n",
    )
    parser.add_argument(
        "--lang",
        choices=["zh", "en"],
        default="zh",
        help="界面语言 / Interface language (default: zh)",
    )
    parser.add_argument(
        "--no-detect",
        action="store_true",
        help="跳过自动检测 UUP 脚本目录 / Skip auto-detect of UUP scripts",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    i18n = I18n(default=args.lang)
    console = Console()

    # ── 启动时检测本地 UUP 脚本 ──
    confirmed: Optional[ScriptInfo] = None
    if not args.no_detect:
        detector = ScriptDetector()
        confirmed = detector.ask_user(i18n, console)

    # ── 高级选项状态：仅当前会话有效 ──
    advanced = False

    while True:
        try:
            print_header(i18n, console, confirmed=confirmed)
            print_menu(i18n, console, advanced=advanced)

            choice = Prompt.ask(
                f"[bold]{i18n.t_str('menu.choose')}[/bold]",
                choices=["0", "1", "2", "3"],
                default="1",
            )

            if choice == "1":
                action_generate(i18n, console, confirmed=confirmed, advanced=advanced)
            elif choice == "2":
                action_switch_lang(i18n, console)
            elif choice == "3":
                advanced = not advanced
                toggle_key = "menu.toggle_on" if advanced else "menu.toggle_off"
                console.print(f"\n[bold green]{i18n.t_str(toggle_key)}[/bold green]\n")
                continue  # 直接回到菜单（不显示「按回车继续」）
            elif choice == "0":
                console.print(
                    f"\n[bold cyan]{i18n.t_str('goodbye')}[/bold cyan]\n"
                )
                return 0

            # 等待用户按回车继续
            console.print()
            Prompt.ask(
                "[dim]>>> Press Enter to continue[/dim]"
                if i18n.current() == "en"
                else "[dim]>>> 按回车继续[/dim]",
                default="",
            )

        except KeyboardInterrupt:
            console.print(
                f"\n[bold cyan]{i18n.t_str('goodbye')}[/bold cyan]\n"
            )
            return 0
        except EOFError:
            return 0
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
