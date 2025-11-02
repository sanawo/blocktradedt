#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动提交并推送到 GitHub 的脚本
"""
import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, check=True):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if check and result.returncode != 0:
            print(f"❌ 错误: {cmd}")
            print(result.stderr)
            return False
        return True
    except Exception as e:
        print(f"❌ 执行命令失败: {e}")
        return False

def auto_commit_push(commit_message=None):
    """自动提交并推送"""
    print("=" * 50)
    print("🚀 自动提交并推送到 GitHub")
    print("=" * 50)
    print()
    
    # 1. 检查状态
    print("[1/4] 检查 Git 状态...")
    run_command("git status --short", check=False)
    print()
    
    # 2. 添加所有更改
    print("[2/4] 添加所有更改...")
    if not run_command("git add ."):
        return False
    print("✅ 文件已暂存")
    print()
    
    # 3. 提交
    print("[3/4] 提交更改...")
    if not commit_message:
        commit_message = f"Auto commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    if not run_command(f'git commit -m "{commit_message}"'):
        print("⚠️  可能没有需要提交的更改")
    else:
        print(f"✅ 已提交: {commit_message}")
    print()
    
    # 4. 推送
    print("[4/4] 推送到 GitHub...")
    if not run_command("git push origin master"):
        return False
    print("✅ 已推送到 GitHub")
    print()
    
    print("=" * 50)
    print("✅ 完成！代码已推送到 GitHub")
    print("=" * 50)
    return True

if __name__ == "__main__":
    commit_msg = sys.argv[1] if len(sys.argv) > 1 else None
    success = auto_commit_push(commit_msg)
    sys.exit(0 if success else 1)

