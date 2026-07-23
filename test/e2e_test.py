#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""端到端集成测试：生成真实可用 UUP workflow 文件"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import workflow_generator as wg

# 模拟用户输入：生成 UUP ISO 构建工作流
b = wg.YmlBuilder()
b.set_name("Windows11_24H2_amd64")
b.set_trigger("workflow_dispatch")
b.add_job(
    "Windows11_24H2_amd64",
    "windows-latest",
    [
        {"name": "Checkout", "uses": "actions/checkout@v5"},
        {
            "name": "Build ISO",
            "run": 'cd "${{ env.FILE_NAME }}"\nuup_download_windows.cmd',
        },
        {
            "name": "Package",
            "run": '7z a -v1950m "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}.7z" "./${{ env.FILE_NAME }}/*.iso"',
        },
        {
            "name": "Release",
            "uses": "softprops/action-gh-release@v2",
            "with": {
                "tag_name": "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}",
                "files": "${{ env.FILE_NAME }}-${{ env.Build_VERSION }}.7z*",
            },
        },
    ],
    env={"Build_VERSION": "26100.8313", "FILE_NAME": "Windows11_24H2_amd64"},
    timeout=360,
)

out = Path(".github/workflows/Windows11_24H2_amd64.yml")
ok, msg = b.save(out)
print("保存:", "成功" if ok else f"失败: {msg}")
print("路径:", out.resolve())
print()
print("--- 生成内容 ---")
print(out.read_text(encoding="utf-8"))
print("--- 验证通过 ---")
