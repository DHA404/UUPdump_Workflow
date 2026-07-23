#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build 版本映射表（独立脚本）

双入口：
  - 命令行：python build_mapping.py <build>   → 查单个 build
  - 被导入：from build_mapping import lookup, resolve_name

用法：
  python build_mapping.py 26200          → Windows11_25H2
  python build_mapping.py 26200.8968     → Windows11_25H2
  python build_mapping.py 17763          → Windows10_1809 (also: WindowsServer2019)
  python build_mapping.py 99999          → Unknown build 99999
  python build_mapping.py                → 打印全量建表
"""
import sys
from typing import Dict, List, Optional, Tuple, Union

# ============================================================
# BUILD_MAP：build major → (product, alias)
# 若为 list → 多候选，通过 dir_name 含 "server" 来 disambiguate
# ============================================================
BUILD_MAP: Dict[int, Union[Tuple[str, str], List[Tuple[str, str]]]] = {
    # ── Windows 11 ──
    22000: ("Windows11", "21H2"),
    22621: ("Windows11", "22H2"),
    22631: ("Windows11", "23H2"),
    26100: ("Windows11", "24H2"),
    26200: ("Windows11", "25H2"),
    26300: ("Windows11", "26H2"),
    28000: ("Windows11", "26H1"),
    # ── Windows 10 ──
    10240: ("Windows10", "1507"),
    10586: ("Windows10", "1511"),
    14393: ("Windows10", "1607"),
    15063: ("Windows10", "1703"),
    16299: ("Windows10", "1709"),
    17134: ("Windows10", "1803"),
    17763: [("Windows10", "1809"), ("WindowsServer2019", "")],
    18362: ("Windows10", "19H1"),
    18363: ("Windows10", "19H2"),
    19041: ("Windows10", "20H1"),
    19044: ("Windows10", "21H2"),
    19045: ("Windows10", "22H2"),
    # ── Windows Server ──
    20348: ("WindowsServer2022", ""),
    20349: ("WindowsServer2022", ""),
    26280: ("WindowsServer2025", ""),
}


def _major(build_str: str) -> Optional[int]:
    """从 '26200.8968' 提取 26200；纯数字直接转"""
    try:
        return int(build_str.split(".")[0])
    except (ValueError, AttributeError):
        return None


def lookup(
    build_str: str, dir_name: str = ""
) -> Optional[Tuple[str, str]]:
    """查表返回 (product, alias)，ambiguous 时根据 dir_name 含 'server' 择一"""
    major = _major(build_str)
    if major is None:
        return None
    result = BUILD_MAP.get(major)
    if isinstance(result, list):
        # 多候选：优先匹配 server
        if dir_name and "server" in dir_name.lower():
            return result[1] if len(result) > 1 else result[0]
        return result[0]
    return result


def resolve_name(
    build_str: str, arch: str = "amd64", dir_name: str = ""
) -> Optional[str]:
    """查表构造完整 FILE_NAME，例：Windows11_25H2_amd64 / WindowsServer2022_amd64"""
    result = lookup(build_str, dir_name=dir_name)
    if result is None:
        return None
    product, alias = result
    if alias:
        return f"{product}_{alias}_{arch}"
    return f"{product}_{arch}"


def print_table() -> None:
    """格式化打印全量建表"""
    print("Build Mapping Table")
    print("=" * 55)
    print(f"{'Major':>8}  {'Product':<22} {'Alias':<10}")
    print("-" * 55)
    for major in sorted(BUILD_MAP.keys()):
        entry = BUILD_MAP[major]
        if isinstance(entry, list):
            first = True
            for product, alias in entry:
                label = alias if alias else "-"
                if first:
                    print(f"{major:>8}  {product:<22} {label:<10}")
                    first = False
                else:
                    print(f"{'':>8}  {product:<22} {label:<10}  [alternative]")
        else:
            product, alias = entry
            label = alias if alias else "-"
            print(f"{major:>8}  {product:<22} {label:<10}")
    print("=" * 55)


def main() -> None:
    if len(sys.argv) < 2:
        print_table()
        return

    build = sys.argv[1].strip()
    # ambiguous 时显示所有候选
    major = _major(build)
    if major is None:
        print(f"Invalid build: {build}")
        sys.exit(1)

    entry = BUILD_MAP.get(major)
    if entry is None:
        print(f"Unknown build {build}")
        sys.exit(1)

    if isinstance(entry, list):
        # 显示所有候选
        labels = [f"{p}_{a}" if a else p for p, a in entry]
        print(labels[0])
        if len(labels) > 1:
            print(f"(also: {', '.join(labels[1:])})")
    else:
        product, alias = entry
        if alias:
            print(f"{product}_{alias}")
        else:
            print(product)


if __name__ == "__main__":
    main()
