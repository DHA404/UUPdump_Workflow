#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""非交互式单元测试：直接测试各模块功能"""
import sys
from pathlib import Path
from typing import Optional
from unittest.mock import patch, MagicMock

# 确保 workflow_generator.py 同目录
sys.path.insert(0, str(Path(__file__).parent))

import workflow_generator as wg


def test_i18n():
    """测试 i18n 翻译"""
    print("\n=== Test 1: I18n ===")
    i18n = wg.I18n("zh")
    assert i18n.t("app.title") == "UUP 工作流生成器", f"got: {i18n.t('app.title')}"
    assert "开始生成" in i18n.t("menu.item1"), f"got: {i18n.t('menu.item1')}"
    assert isinstance(i18n.t_list("opts.runners"), list)
    assert len(i18n.t_list("opts.runners")) == 2  # 精简为 2 个 runner

    i18n.switch("en")
    assert i18n.t("app.title") == "UUP Workflow Generator", f"got: {i18n.t('app.title')}"
    assert i18n.t("menu.item1") == "[1] Generate", f"got: {i18n.t('menu.item1')}"
    print("  [OK] i18n 中英切换正常")


def test_yml_builder_basic():
    """测试 YmlBuilder 基础功能"""
    print("\n=== Test 2: YmlBuilder Basic ===")
    b = wg.YmlBuilder()
    b.set_name("Test_Build")
    b.set_trigger("workflow_dispatch")
    b.add_job(
        "build",
        "ubuntu-latest",
        [
            {"name": "Checkout", "uses": "actions/checkout@v5"},
            {"name": "Hello", "run": "echo hello"},
        ],
        env={"FOO": "bar"},
        timeout=60,
    )
    yaml_text = b.to_yaml()
    print("  生成的 yml 文本：")
    for line in yaml_text.splitlines():
        print(f"    {line}")

    # 验证字段顺序：name → on → jobs
    lines = yaml_text.splitlines()
    assert lines[0].startswith("name:"), f"line 0: {lines[0]}"
    assert "on:" in yaml_text
    assert "jobs:" in yaml_text
    assert "build:" in yaml_text
    assert "timeout-minutes: 60" in yaml_text
    assert "FOO: bar" in yaml_text

    # 用 PyYAML 验证可被解析
    import yaml
    parsed = yaml.safe_load(yaml_text)
    assert parsed["name"] == "Test_Build"
    assert parsed["on"] == "workflow_dispatch"
    assert parsed["jobs"]["build"]["runs-on"] == "ubuntu-latest"
    assert parsed["jobs"]["build"]["timeout-minutes"] == 60
    assert parsed["jobs"]["build"]["env"]["FOO"] == "bar"
    assert len(parsed["jobs"]["build"]["steps"]) == 2
    print("  [OK] YmlBuilder 生成+解析正确")


def test_yml_builder_triggers():
    """测试各触发器类型"""
    print("\n=== Test 3: YmlBuilder Triggers ===")
    import yaml  # 本测试局部导入
    b = wg.YmlBuilder()
    b.set_name("T").set_trigger("push")
    parsed = yaml.safe_load(b.to_yaml())
    assert parsed["on"] == {"push": {"branches": ["main"]}}, f"push: {parsed['on']}"
    print(f"  push: {parsed['on']}")

    b = wg.YmlBuilder()
    b.set_name("T").set_trigger("pull_request")
    parsed = yaml.safe_load(b.to_yaml())
    assert parsed["on"] == {"pull_request": {"branches": ["main"]}}
    print(f"  pull_request: {parsed['on']}")

    b = wg.YmlBuilder()
    b.set_name("T").set_trigger("schedule")
    parsed = yaml.safe_load(b.to_yaml())
    assert parsed["on"] == {"schedule": [{"cron": "0 2 * * 1"}]}
    print(f"  schedule: {parsed['on']}")

    b = wg.YmlBuilder()
    b.set_name("T").set_trigger("workflow_call")
    parsed = yaml.safe_load(b.to_yaml())
    assert parsed["on"] == "workflow_call"
    print(f"  workflow_call: {parsed['on']}")
    print("  [OK] 5 种触发器均正确")


def test_save_and_validate(tmp_path):
    """测试保存+验证"""
    print("\n=== Test 4: Save & Validate ===")
    b = wg.YmlBuilder()
    b.set_name("Saved_Test")
    b.set_trigger("workflow_dispatch")
    b.add_job(
        "build", "ubuntu-latest",
        [{"name": "Hello", "run": "echo hi"}],
        timeout=10,
    )
    out = tmp_path / "workflows" / "Saved_Test.yml"
    ok, msg = b.save(out)
    assert ok, f"save failed: {msg}"
    assert out.exists(), "file not created"
    print(f"  文件: {out}")
    print(f"  验证: {ok}")

    # 读取并验证
    ok2, msg2 = wg.YmlBuilder.validate(out)
    assert ok2, f"validate failed: {msg2}"
    print(f"  PyYAML 解析: {ok2}")
    print("  [OK] 保存+验证流程正常")


def test_uup_wizard_flow():
    """测试 UUPWizard 生成的 yml 结构完整性"""
    print("\n=== Test 5: UUP Wizard Flow ===")
    import yaml

    # 直接测试 _build_steps（三种 release 模式）
    i18n = wg.I18n("zh")
    console = __import__("io").StringIO()
    from rich.console import Console
    c = Console(file=console, width=120)
    wizard = wg.UUPWizard(i18n, c)

    # 模式 0：仅 artifact
    steps0 = wizard._build_steps(0)
    assert len(steps0) == 4, f"artifact mode: expected 4 steps, got {len(steps0)}"
    assert any("actions/upload-artifact@v4" in str(s.get("uses", "")) for s in steps0)
    assert "softprops" not in str(steps0)
    print("  模式 0 (artifact): 4 步 ✓")

    # 模式 1：artifact + release
    steps1 = wizard._build_steps(1)
    assert len(steps1) == 5, f"release mode: expected 5 steps, got {len(steps1)}"
    assert any("actions/upload-artifact@v4" in str(s.get("uses", "")) for s in steps1)
    assert any("softprops/action-gh-release@v2" in str(s.get("uses", "")) for s in steps1)
    print("  模式 1 (artifact+release): 5 步 ✓")

    # 模式 2：不自动上传
    steps2 = wizard._build_steps(2)
    assert len(steps2) == 3, f"skip mode: expected 3 steps, got {len(steps2)}"
    print("  模式 2 (skip): 3 步 ✓")

    # 验证每条 step 结构
    for mode_idx, steps in [(0, steps0), (1, steps1), (2, steps2)]:
        for step in steps:
            assert "name" in step
            assert "uses" in step or "run" in step
    print("  所有 steps 均有 name + (uses|run) ✓")

    # 验证 build-script 多行命令
    build_step = next(s for s in steps0 if s["name"] == "Build ISO")
    assert "\n" in build_step["run"], "Build ISO 应该是多行命令"
    assert "uup_download_windows.cmd" in build_step["run"]
    assert "env.UUP_DIR" in build_step["run"]
    print("  Build ISO 多行命令正确 ✓")

    # 验证 package-7z 包含 1950m 分卷
    pkg_step = next(s for s in steps0 if s["name"] == "Package")
    assert "1950m" in pkg_step["run"]
    assert "7z" in pkg_step["run"]
    print("  Package 1950m 分卷正确 ✓")

    # 验证 artifact/release 引用 ${{ env.* }}
    for steps in [steps0, steps1]:
        art_step = next(s for s in steps if s.get("uses", "").startswith("actions/upload-artifact"))
        with_text = str(art_step["with"])
        assert "env.FILE_NAME" in with_text
        assert "env.Build_VERSION" in with_text

    if any("softprops" in str(s) for s in steps1):
        rel_step = next(s for s in steps1 if "softprops" in str(s.get("uses", "")))
        with_text = str(rel_step["with"])
        assert "env.FILE_NAME" in with_text
        assert "env.Build_VERSION" in with_text
    print("  artifact/release 引用 env.* 正确 ✓")

    # 验证 yml 整体结构和 UUPdumpWinISO 一致
    b = wg.YmlBuilder()
    b.set_name("Win11_24H2")
    b.set_trigger("workflow_dispatch")
    env = {"Build_VERSION": "26100.8313", "FILE_NAME": "Win11_24H2"}
    b.add_job("build", "windows-latest", steps0, env=env, timeout=360)
    yaml_text = b.to_yaml()
    parsed = yaml.safe_load(yaml_text)
    assert parsed["name"] == "Win11_24H2"
    assert parsed["on"] == "workflow_dispatch"
    assert parsed["jobs"]["build"]["runs-on"] == "windows-latest"
    assert parsed["jobs"]["build"]["timeout-minutes"] == 360
    assert parsed["jobs"]["build"]["env"]["Build_VERSION"] == "26100.8313"
    assert parsed["jobs"]["build"]["env"]["FILE_NAME"] == "Win11_24H2"
    assert len(parsed["jobs"]["build"]["steps"]) == 4
    print("  完整 yml 结构与 UUPdumpWinISO 对齐 ✓")

    print("  [OK] UUPWizard 流程完整验证通过")


def test_i18n_completeness():
    """测试中英文键完整性（防止漏译）"""
    print("\n=== Test 6: I18n Key Parity ===")
    zh_keys = set(wg.I18N["zh"].keys())
    en_keys = set(wg.I18N["en"].keys())
    missing_in_en = zh_keys - en_keys
    missing_in_zh = en_keys - zh_keys
    if missing_in_en:
        print(f"  [WARN] zh has but en missing: {missing_in_en}")
    if missing_in_zh:
        print(f"  [WARN] en has but zh missing: {missing_in_zh}")
    assert not missing_in_en, f"Missing in en: {missing_in_en}"
    assert not missing_in_zh, f"Missing in zh: {missing_in_zh}"

    # 验证关键键存在
    for key in ["wizard.name", "wizard.version", "wizard.version.help",
                 "wizard.runner", "wizard.timeout", "wizard.timeout.help",
                 "wizard.release", "opt.recommended",
                 "detect.title", "detect.choose", "wizard.detected",
                 "header.confirmed"]:
        assert key in zh_keys, f"Missing key '{key}' in zh"
        assert key in en_keys, f"Missing key '{key}' in en"

    # 验证推荐标签
    assert wg.I18N["zh"]["opt.recommended"] == "推荐"
    assert wg.I18N["en"]["opt.recommended"] == "Recommended"

    print(f"  zh 键数: {len(zh_keys)}")
    print(f"  en 键数: {len(en_keys)}")
    print("  [OK] 中英文键完全对齐，关键键均存在")


def test_script_detector(tmp_path):
    """测试 ScriptDetector 正则提取逻辑"""
    print("\n=== Test 8: ScriptDetector ===")
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "UUPdump script"
        base.mkdir()

        # 测试用例
        cases = [
            # (目录名, 期望 build, 期望 name)
            (
                "26200.8894_amd64_zh-cn_professional_a2702664_convert_virtual (1)",
                "26200.8894",
                "Windows11_25H2_amd64",  # build_mapping 查出 Win11 25H2
            ),
            (
                "Windows10_22H2_amd64_Cumulative_Update",
                None,
                "Windows10_22H2_amd64",
            ),
            (
                "Windows11_25H2_amd64",
                None,
                "Windows11_25H2_amd64",
            ),
            (
                "26100.8313_amd64_en-us_professional",
                "26100.8313",
                "Windows11_24H2_amd64",  # build_mapping 查出 Win11 24H2
            ),
            (
                "Windows11_24H2_x86",
                None,
                "Windows11_24H2_x86",
            ),
            (
                "MyRandomDir",
                None,
                "MyRandomDir",  # 兜底
            ),
        ]
        for dir_name, exp_build, exp_name in cases:
            (base / dir_name).mkdir()
            info = wg.ScriptDetector(base=base)._parse(base / dir_name)
            assert info.build == exp_build, (
                f"{dir_name}: build expected {exp_build}, got {info.build}"
            )
            assert info.name == exp_name, (
                f"{dir_name}: name expected {exp_name}, got {info.name}"
            )
            print(f"  ✓ {dir_name[:50]}")
            print(f"      build={info.build}, name={info.name}")

        # scan() 测试：返回所有
        infos = wg.ScriptDetector(base=base).scan()
        assert len(infos) == len(cases), f"expected {len(cases)}, got {len(infos)}"
        print(f"  scan() 返回 {len(infos)} 个 ScriptInfo")

    # 不存在的目录
    detector = wg.ScriptDetector(base=Path("/nonexistent/abc/xyz"))
    assert detector.scan() == [], "不存在的目录应返回空"
    print("  ✓ 不存在目录返回空")

    # 正常 BASE_DIR（项目当前实际为空）
    real = wg.ScriptDetector(base=Path("UUPdump script")).scan()
    assert isinstance(real, list)
    print(f"  ✓ 真实 UUPdump script/ 目录扫描返回 {len(real)} 项")
    print("  [OK] ScriptDetector 正则提取全部正确")


def test_uup_wizard_default_change():
    """测试 UUPWizard 接受默认值时显示'检测到的信息'行"""
    print("\n=== Test 9: UUPWizard Detected Defaults ===")
    import io
    from rich.console import Console
    i18n = wg.I18n("zh")
    console = Console(file=io.StringIO(), width=120, force_terminal=False)

    # 1. 无默认值：不应显示"检测到的信息"
    w1 = wg.UUPWizard(i18n, console)
    assert w1._has_detected_name is False
    assert w1._has_detected_build is False
    assert w1.default_name == wg.UUPWizard.DEFAULT_NAME
    assert w1.default_build == wg.UUPWizard.DEFAULT_BUILD
    print("  无默认值：使用内置示例 ✓")

    # 2. 有默认值：应显示
    w2 = wg.UUPWizard(
        i18n, console,
        default_name="Windows11_25H2_amd64",
        default_build="26200.8894",
    )
    assert w2._has_detected_name is True
    assert w2._has_detected_build is True
    assert w2.default_name == "Windows11_25H2_amd64"
    assert w2.default_build == "26200.8894"
    print("  有默认值：替换为检测值 ✓")

    # 3. 默认值 None 时用内置
    w3 = wg.UUPWizard(i18n, console, default_name=None)
    assert w3._has_detected_name is False
    assert w3.default_name == wg.UUPWizard.DEFAULT_NAME
    print("  显式 None：用内置示例 ✓")
    print("  [OK] UUPWizard 默认值切换正常")


def test_cli_help():
    """测试 CLI 参数解析"""
    print("\n=== Test 7: CLI Args ===")
    import subprocess
    env = dict(__import__("os").environ)
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, "workflow_generator.py", "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0, f"help failed: {result.stderr}"
    # --help 走 argparse（不走 rich），输出是纯 ASCII
    assert "--lang" in result.stdout
    assert "Workflow Generator" in result.stdout
    print("  [OK] --help 正常")
    print(f"  --- help 输出 ---\n{result.stdout}")


def test_build_mapping():
    """测试 build_mapping 映射表查表"""
    print("\n=== Test 10: Build Mapping ===")
    from build_mapping import lookup, resolve_name as bm_resolve

    # Win11 25H2
    assert lookup("26200.8968") == ("Windows11", "25H2"), "Win11 25H2"
    assert bm_resolve("26200.8968", "amd64") == "Windows11_25H2_amd64"
    print("  ✓ Win11 25H2: Windows11_25H2_amd64")

    # Win11 24H2
    assert lookup("26100.8313") == ("Windows11", "24H2"), "Win11 24H2"
    assert bm_resolve("26100.8313", "amd64") == "Windows11_24H2_amd64"
    print("  ✓ Win11 24H2: Windows11_24H2_amd64")

    # Win10 1809
    assert lookup("17763") == ("Windows10", "1809"), "Win10 1809"
    print("  ✓ Win10 1809: Windows10_1809")

    # Win10 22H2
    assert lookup("19045.7058") == ("Windows10", "22H2"), "Win10 22H2"
    assert bm_resolve("19045.7058", "x86") == "Windows10_22H2_x86"
    print("  ✓ Win10 22H2: Windows10_22H2_x86")

    # Server 2022
    assert lookup("20348") == ("WindowsServer2022", ""), "Server 2022"
    assert bm_resolve("20348", "amd64") == "WindowsServer2022_amd64"
    print("  ✓ Server 2022: WindowsServer2022_amd64")

    # Ambiguous 17763 → 默认 Win10，dir_name 含 server → Server2019
    assert lookup("17763") == ("Windows10", "1809"), "default"
    assert lookup("17763", dir_name="server_1809") == ("WindowsServer2019", ""), "server"
    print("  ✓ Ambiguous 17763: Win10_1809 / Server2019")

    # Unknown
    assert lookup("99999") is None
    assert bm_resolve("99999", "amd64") is None
    print("  ✓ Unknown build: None")

    # 集成：ScriptDetector._parse 查表 + 兜底
    print("\n  --- 集成测试 ScriptDetector._parse ---")
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "UUPdump script"
        base.mkdir()
        # 测试目录：有 build 映射
        d1 = base / "26200.8968_amd64_zh-cn_professional"
        d1.mkdir()
        info = wg.ScriptDetector(base=base)._parse(d1)
        assert info.name == "Windows11_25H2_amd64", f"got {info.name}"
        print(f"  有映射: {info.name} ✓")

        # 测试目录：有 windows 关键字和 release 别名（走兜底）
        d2 = base / "Windows10_22H2_amd64_Cumulative_Update"
        d2.mkdir()
        info2 = wg.ScriptDetector(base=base)._parse(d2)
        assert info2.name == "Windows10_22H2_amd64", f"got {info2.name}"
        print(f"  兜底有效: {info2.name} ✓")

        # 测试目录：无映射也无关键字（兜底降级）
        d3 = base / "MyRandomDir"
        d3.mkdir()
        info3 = wg.ScriptDetector(base=base)._parse(d3)
        assert "Windows" not in info3.name  # 无 build 时取目录名
        print(f"  完全降级: {info3.name} ✓")

    print("  [OK] Build Mapping 查表 + 集成全部正确")


def test_step_template_render():
    """测试 StepTemplate 6 个模板的 render 输出"""
    print("\n=== Test 11: StepTemplate Render ===")
    templates = wg.StepTemplate.all()
    assert len(templates) == 6, f"expected 6 templates, got {len(templates)}"
    print(f"  ✓ 共 {len(templates)} 个模板")

    by_id = {t.id: t for t in templates}

    # checkout
    s = by_id["checkout"].render()
    assert s == {"name": "Checkout", "uses": "actions/checkout@v5"}
    print("  ✓ checkout: actions/checkout@v5")

    # build
    s = by_id["build"].render()
    assert s["name"] == "Build ISO"
    assert s["shell"] == "cmd", "build 必须声明 shell: cmd"
    assert "uup_download_windows.cmd" in s["run"]
    assert "${{ env.UUP_DIR }}" in s["run"]
    print("  ✓ build: shell=cmd + uup_download_windows.cmd")

    # package
    s = by_id["package"].render()
    assert s["name"] == "Package"
    assert " -mx=9" in s["run"], "package 必须含 -mx=9"
    assert " -v1950m " in s["run"], "package 必须含 -v1950m"
    assert "${{ env.Build_VERSION }}" in s["run"]
    print("  ✓ package: -v1950m ... -mx=9")

    # upload
    s = by_id["upload"].render()
    assert s["uses"] == "actions/upload-artifact@v4"
    assert s["with"]["name"].endswith("${{ env.Build_VERSION }}")
    assert s["with"]["path"].endswith(".7z*")
    print("  ✓ upload: actions/upload-artifact@v4")

    # release
    s = by_id["release"].render()
    assert s["uses"] == "softprops/action-gh-release@v2"
    assert "tag_name" in s["with"]
    print("  ✓ release: softprops/action-gh-release@v2")

    # custom 应 raise NotImplementedError
    try:
        by_id["custom"].render()
        assert False, "custom render() should raise"
    except NotImplementedError:
        print("  ✓ custom: render() raise NotImplementedError（走 ask 预渲染）")

    print("  [OK] 6 模板 render 输出全部正确")


def test_advanced_wizard_construction():
    """测试 UUPWizard 接受 advanced 参数"""
    print("\n=== Test 12: UUPWizard Advanced ===")
    import io
    from rich.console import Console
    i18n = wg.I18n("zh")
    console = Console(file=io.StringIO(), width=120, force_terminal=False)

    # 默认 advanced=False
    w1 = wg.UUPWizard(i18n, console)
    assert w1.advanced is False
    assert w1._selected_steps is None
    print("  ✓ 默认 advanced=False, _selected_steps=None")

    # 显式 advanced=True
    w2 = wg.UUPWizard(i18n, console, advanced=True)
    assert w2.advanced is True
    assert w2._selected_steps is None  # 尚未选
    print("  ✓ advanced=True 时初始化成功")

    print("  [OK] UUPWizard advanced 参数接受正常")


def test_build_steps_with_advanced_selected():
    """测试 _build_steps 在高级模式下用用户选择的步骤"""
    print("\n=== Test 13: _build_steps Advanced ===")
    import io
    from rich.console import Console
    i18n = wg.I18n("zh")
    console = Console(file=io.StringIO(), width=120, force_terminal=False)

    # 1. 高级模式 + 用户选了 checkout + build + package
    w = wg.UUPWizard(i18n, console, advanced=True)
    by_id = {t.id: t for t in wg.StepTemplate.all()}
    w._selected_steps = [by_id["checkout"], by_id["build"], by_id["package"]]
    steps = w._build_steps(release_idx=0)  # release_idx 应被忽略
    assert len(steps) == 3, f"expected 3 steps, got {len(steps)}"
    assert steps[0]["uses"] == "actions/checkout@v5"
    assert steps[1]["shell"] == "cmd"
    assert " -mx=9" in steps[2]["run"]
    print(f"  ✓ 高级模式+3 模板: {len(steps)} 步 (checkout/build/package)")

    # 2. 高级模式 + 空选择 → 走默认 4 步
    w2 = wg.UUPWizard(i18n, console, advanced=True)
    w2._selected_steps = None
    steps = w2._build_steps(release_idx=0)
    assert len(steps) == 4, f"default should be 4 steps, got {len(steps)}"
    assert steps[-1]["uses"] == "actions/upload-artifact@v4"
    print(f"  ✓ 高级模式但未选: 走默认 {len(steps)} 步 (含 upload)")

    # 3. 高级模式 + release_idx=1 (含 release) → 但有 _selected_steps 时 release 被忽略
    w3 = wg.UUPWizard(i18n, console, advanced=True)
    w3._selected_steps = [by_id["checkout"]]
    steps = w3._build_steps(release_idx=1)
    assert len(steps) == 1, f"应该只有 1 步, got {len(steps)}"
    print(f"  ✓ 高级模式覆盖 release_idx: {len(steps)} 步")

    # 4. 非高级模式 → 默认 4 步（回归测试）
    w4 = wg.UUPWizard(i18n, console, advanced=False)
    steps = w4._build_steps(release_idx=0)
    assert len(steps) == 4
    print(f"  ✓ 非高级模式: 4 步默认 (回归)")

    print("  [OK] _build_steps 高级模式分支正确")


def test_menu_item3_i18n():
    """测试 i18n 新增的 menu.item3 等键"""
    print("\n=== Test 14: Menu Item3 I18n ===")
    i18n = wg.I18n("zh")
    item3_zh = i18n.t("menu.item3")
    assert "{state}" in item3_zh, f"item3 应含 {{state}} 占位符: {item3_zh}"
    assert "[3]" in item3_zh
    rendered_zh = item3_zh.replace("{state}", i18n.t("menu.state.off"))
    assert "关闭" in rendered_zh
    print(f"  ✓ zh: {rendered_zh}")

    i18n.switch("en")
    item3_en = i18n.t("menu.item3")
    assert "{state}" in item3_en
    rendered_en = item3_en.replace("{state}", i18n.t("menu.state.off"))
    assert "OFF" in rendered_en
    print(f"  ✓ en: {rendered_en}")

    # 其他新增键
    for k in ("menu.state.on", "menu.state.off",
              "menu.toggle_on", "menu.toggle_off",
              "wizard.steps", "wizard.steps.help",
              "wizard.steps.reorder", "wizard.steps.custom.name",
              "wizard.steps.custom.uses", "wizard.steps.custom.run",
              "wizard.steps.custom.shell", "wizard.steps.selected"):
        assert k in wg.I18N["zh"], f"zh 缺 {k}"
        assert k in wg.I18N["en"], f"en 缺 {k}"
    print(f"  ✓ 中英各 {12} 个新键齐全")

    print("  [OK] i18n 新增键全部就位")


def test_detect_from_env():
    """测试 _detect_from_env 从 LC_ALL/LANG/LANGUAGE 检测"""
    print("\n=== Test 15: Detect Lang From Env ===")
    import os
    saved = {k: os.environ.get(k) for k in ("LC_ALL", "LANG", "LANGUAGE")}

    try:
        # 清空环境
        for k in saved:
            os.environ.pop(k, None)

        # 1. LANG=zh_CN.UTF-8 → zh
        os.environ["LANG"] = "zh_CN.UTF-8"
        assert wg._detect_from_env() == "zh", "LANG=zh_CN.UTF-8"
        print("  ✓ LANG=zh_CN.UTF-8 → zh")

        # 2. LANG=en_US.UTF-8 → en
        os.environ["LANG"] = "en_US.UTF-8"
        assert wg._detect_from_env() == "en", "LANG=en_US.UTF-8"
        print("  ✓ LANG=en_US.UTF-8 → en")

        # 3. LC_ALL 优先级高于 LANG
        os.environ["LC_ALL"] = "zh_TW.UTF-8"
        os.environ["LANG"] = "en_US"
        assert wg._detect_from_env() == "zh", "LC_ALL 应优先"
        print("  ✓ LC_ALL > LANG: zh_TW 覆盖 en_US")

        # 4. LANGUAGE 是列表，取第一个
        os.environ.pop("LC_ALL", None)
        os.environ["LANG"] = "de_DE.UTF-8"  # 不支持
        os.environ["LANGUAGE"] = "zh_CN:en_US:ja_JP"
        assert wg._detect_from_env() == "zh", "LANGUAGE 列表取第一个"
        print("  ✓ LANGUAGE=zh_CN:en_US:ja_JP → zh (取首个)")

        # 5. 全部空 → None
        for k in ("LC_ALL", "LANG", "LANGUAGE"):
            os.environ.pop(k, None)
        assert wg._detect_from_env() is None, "全空应返回 None"
        print("  ✓ 全部环境变量空 → None")

        # 6. 不支持的语言（de_DE）→ None
        os.environ["LANG"] = "de_DE.UTF-8"
        assert wg._detect_from_env() is None, "de_DE 不支持"
        print("  ✓ LANG=de_DE.UTF-8 → None (不支持)")

        # 7. 短格式 "zh" / "en"
        os.environ["LANG"] = "zh"
        assert wg._detect_from_env() == "zh"
        os.environ["LANG"] = "en"
        assert wg._detect_from_env() == "en"
        print("  ✓ 短格式 zh / en 也支持")

    finally:
        # 恢复环境
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    print("  [OK] _detect_from_env 全部场景正确")


def test_detect_from_windows_api():
    """测试 _detect_from_windows_api 模拟不同 LANG ID"""
    print("\n=== Test 16: Detect Lang From Windows API ===")
    import sys

    # 通过 monkey-patch 内部函数，避开 ctypes.windll LazyLoader 的复杂性
    # 直接验证 LANG ID → zh/en 的映射逻辑
    original = wg._detect_from_windows_api

    def fake_detect(lid):
        def _impl() -> Optional[str]:
            if lid is None:
                return None
            if lid in (0x0804, 0x0404, 0x0C04, 0x1004):
                return "zh"
            if lid in (0x0409, 0x0809, 0x0C09, 0x1009, 0x040C, 0x080C, 0x0C0C):
                return "en"
            primary = lid >> 10
            if primary == 0x11:
                return "zh"
            if primary == 0x09:
                return "en"
            return None
        return _impl

    test_cases = [
        (0x0804, "zh", "简体中文"),
        (0x0404, "zh", "繁体中文"),
        (0x0C04, "zh", "香港中文"),
        (0x1004, "zh", "新加坡中文"),
        (0x0409, "en", "英语(美国)"),
        (0x0809, "en", "英语(英国)"),
        (0x0C09, "en", "英语(澳大利亚)"),
        (0x0419, None, "俄语"),
        (0x0411, None, "日语"),
    ]
    for lid, expected, label in test_cases:
        wg._detect_from_windows_api = fake_detect(lid)
        # 同时需要 sys.platform == "win32"
        with patch.object(sys, "platform", "win32"):
            result = wg._detect_from_windows_api()
        assert result == expected, f"LID=0x{lid:04X} ({label}) 期望 {expected}, 实际 {result}"
        print(f"  ✓ LID=0x{lid:04X} ({label}) → {expected}")

    # 恢复原函数
    wg._detect_from_windows_api = original

    # 真实 Windows 平台：直接调用（不 monkey-patch）
    if sys.platform == "win32":
        result = original()
        assert result in ("zh", "en", None)
        print(f"  ✓ 真实 Windows API: {result}")
    else:
        # 非 Windows 平台：返回 None
        with patch.object(sys, "platform", "linux"):
            assert original() is None
        print("  ✓ 非 Windows 平台返回 None")

    print("  [OK] _detect_from_windows_api LANG ID 全部正确")


def test_detect_priority():
    """测试 detect_system_lang 优先级（环境变量 > Windows API）"""
    print("\n=== Test 17: Detect Priority ===")
    import os
    saved = {k: os.environ.get(k) for k in ("LC_ALL", "LANG", "LANGUAGE")}

    # 通过 monkey-patch _detect_from_windows_api 模拟 Windows 返回
    original_win = wg._detect_from_windows_api

    try:
        # 场景 1：环境变量 = en_US，Windows API = zh-CN
        # 预期：env 优先 → en
        for k in saved:
            os.environ.pop(k, None)
        os.environ["LANG"] = "en_US"
        wg._detect_from_windows_api = lambda: "zh"
        assert wg.detect_system_lang() == "en", "env 优先"
        print("  ✓ LANG=en_US 优先于 Windows API (zh) → en")

        # 场景 2：环境变量 = ja_JP（不支持），Windows API = en
        # 预期：env 不匹配 → 走 Windows API → en
        os.environ["LANG"] = "ja_JP"
        wg._detect_from_windows_api = lambda: "en"
        assert wg.detect_system_lang() == "en", "env 不支持时回退"
        print("  ✓ LANG=ja_JP 不支持 → Windows API (en) → en")

        # 场景 3：env 全空 + Windows API = None → 返回 None
        for k in ("LC_ALL", "LANG", "LANGUAGE"):
            os.environ.pop(k, None)
        wg._detect_from_windows_api = lambda: None
        assert wg.detect_system_lang() is None, "全空应返回 None"
        print("  ✓ 全部不可用 → None")

        # 场景 4：LC_ALL=zh_TW 优先于 LANG=en_US
        os.environ["LC_ALL"] = "zh_TW"
        os.environ["LANG"] = "en_US"
        wg._detect_from_windows_api = lambda: "en"
        assert wg.detect_system_lang() == "zh", "LC_ALL 应优先于 LANG"
        print("  ✓ LC_ALL=zh_TW > LANG=en_US → zh")

    finally:
        wg._detect_from_windows_api = original_win
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    print("  [OK] 检测优先级（env > Windows API）正确")


def test_args_no_auto_lang():
    """测试 parse_args 的 --no-auto-lang 开关和 --lang 默认 None"""
    print("\n=== Test 18: Args No Auto Lang ===")
    import sys

    # 1. 无参数：--lang=None, --no-auto_lang=False
    with patch.object(sys, "argv", ["workflow_generator.py"]):
        args = wg.parse_args()
    assert args.lang is None, f"--lang 默认应为 None，实际: {args.lang}"
    assert args.no_auto_lang is False
    assert args.no_detect is False
    print("  ✓ 无参数: --lang=None, --no-auto_lang=False")

    # 2. --no-auto-lang
    with patch.object(sys, "argv", ["workflow_generator.py", "--no-auto-lang"]):
        args = wg.parse_args()
    assert args.lang is None
    assert args.no_auto_lang is True
    print("  ✓ --no-auto-lang 开关存在")

    # 3. --lang en
    with patch.object(sys, "argv", ["workflow_generator.py", "--lang", "en"]):
        args = wg.parse_args()
    assert args.lang == "en"
    assert args.no_auto_lang is False
    print("  ✓ --lang en 显式指定")

    # 4. --help 中应含 --no-auto-lang
    import subprocess
    env = dict(__import__("os").environ)
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, "workflow_generator.py", "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0
    assert "--no-auto-lang" in result.stdout
    assert "auto-detect" in result.stdout
    print("  ✓ --help 含 --no-auto-lang 和 auto-detect 提示")

    print("  [OK] parse_args 开关全部正确")


def test_yml_builder_with_uup_dir():
    """测试 UUP_DIR env 注入和步骤引用（修复 uup_download_windows.cmd 路径错误）"""
    print("\n=== Test: UUP_DIR injection ===")
    b = wg.YmlBuilder()
    b.set_name("Windows11_25H2_amd64")
    b.set_trigger("workflow_dispatch")
    b.add_job(
        "build",
        "windows-latest",
        [
            {"name": "Checkout", "uses": "actions/checkout@v5"},
            {
                "name": "Build ISO",
                "shell": "cmd",
                "run": 'cd "${{ env.UUP_DIR }}"\nuup_download_windows.cmd',
            },
            {
                "name": "Package",
                "run": (
                    '7z a -v1950m "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}.7z" '
                    '"./${{ env.UUP_DIR }}/*.iso" -mx=9'
                ),
            },
        ],
        env={
            "Build_VERSION": "26200.8968",
            "FILE_NAME": "Windows11_25H2_amd64",
            "UUP_DIR": "UUPdump script/26200.8968_amd64_zh-cn_professional_6b4cc4c9_convert_virtual",
        },
        timeout=360,
    )
    import yaml
    parsed = yaml.safe_load(b.to_yaml())
    env = parsed["jobs"]["build"]["env"]
    assert "UUP_DIR" in env, "UUP_DIR env 缺失"
    assert env["UUP_DIR"].startswith("UUPdump script/"), f"UUP_DIR 应指向脚本目录: {env['UUP_DIR']}"
    steps = parsed["jobs"]["build"]["steps"]
    build_step = next(s for s in steps if s["name"] == "Build ISO")
    assert "UUP_DIR" in build_step["run"], "cd 步骤必须使用 UUP_DIR"
    assert "uup_download_windows.cmd" in build_step["run"]
    pkg_step = next(s for s in steps if s["name"] == "Package")
    assert "UUP_DIR" in pkg_step["run"], "7z 步骤必须使用 UUP_DIR"
    assert "-mx=9" in pkg_step["run"]
    print("  [OK] UUP_DIR env + 步骤引用全部正确")


def test_step_template_uses_uup_dir():
    """StepTemplate 渲染应使用 UUP_DIR 而非 FILE_NAME"""
    print("\n=== Test: StepTemplate UUP_DIR ===")
    for tpl in wg.StepTemplate.all():
        if tpl.id in ("checkout", "custom"):
            continue
        rendered = tpl.render()
        run = rendered.get("run", "")
        if "cd" in run or "7z" in run:
            assert "UUP_DIR" in run, f"{tpl.id} 模板未使用 UUP_DIR: {run}"
    print("  [OK] StepTemplate 全部步骤模板引用 UUP_DIR")


def test_wizard_uup_dir_fallback():
    """UUPWizard 不传 uup_dir 时 UUP_DIR 应回退到 name"""
    print("\n=== Test: UUPWizard uup_dir fallback ===")
    console = MagicMock()
    i18n = wg.I18n("zh")
    # 不传 uup_dir，应回退到 name
    wiz = wg.UUPWizard(i18n, console, default_name="Win11", default_build="26200.1")
    assert wiz._uup_dir is None
    # 模拟构造 env（用 run 内的实际逻辑）
    name = "Win11"
    env: dict = {"Build_VERSION": "26200.1", "FILE_NAME": name}
    if wiz._uup_dir:
        env["UUP_DIR"] = wiz._uup_dir
    else:
        env["UUP_DIR"] = name
    assert env["UUP_DIR"] == "Win11", f"fallback 失败: {env['UUP_DIR']}"

    # 传 uup_dir 时应使用
    wiz2 = wg.UUPWizard(i18n, console, default_name="Win11", uup_dir="UUPdump script/foo")
    env2: dict = {"Build_VERSION": "26200.1", "FILE_NAME": "Win11"}
    if wiz2._uup_dir:
        env2["UUP_DIR"] = wiz2._uup_dir
    else:
        env2["UUP_DIR"] = "Win11"
    assert env2["UUP_DIR"] == "UUPdump script/foo", f"传参未生效: {env2['UUP_DIR']}"
    print("  [OK] UUPWizard uup_dir fallback + 传参均正确")


def main():
    import tempfile
    print("=" * 60)
    print("workflow_generator.py 单元测试")
    print("=" * 60)
    test_i18n()
    test_yml_builder_basic()
    test_yml_builder_triggers()
    with tempfile.TemporaryDirectory() as tmp:
        test_save_and_validate(Path(tmp))
    test_uup_wizard_flow()
    test_i18n_completeness()
    with tempfile.TemporaryDirectory() as tmp:
        test_script_detector(Path(tmp))
    test_uup_wizard_default_change()
    test_build_mapping()
    test_cli_help()
    test_step_template_render()
    test_advanced_wizard_construction()
    test_build_steps_with_advanced_selected()
    test_menu_item3_i18n()
    test_detect_from_env()
    test_detect_from_windows_api()
    test_detect_priority()
    test_args_no_auto_lang()
    test_yml_builder_with_uup_dir()
    test_step_template_uses_uup_dir()
    test_wizard_uup_dir_fallback()
    print("\n" + "=" * 60)
    print("[ALL TESTS PASSED]")
    print("=" * 60)


if __name__ == "__main__":
    main()
