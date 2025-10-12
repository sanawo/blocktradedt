#!/usr/bin/env python3
"""
GitHub推送助手脚本
"""
import subprocess
import os
import sys

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n正在执行: {description}")
    print(f"命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"✅ 成功: {description}")
            if result.stdout:
                print(f"输出: {result.stdout}")
        else:
            print(f"❌ 失败: {description}")
            if result.stderr:
                print(f"错误: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def main():
    """主函数"""
    print("GitHub推送助手")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前目录: {current_dir}")
    
    # 检查是否为Git仓库
    if not os.path.exists('.git'):
        print("❌ 当前目录不是Git仓库")
        return
    
    print("✅ 当前目录是Git仓库")
    
    # 检查Git状态
    if not run_command("git status", "检查Git状态"):
        return
    
    # 添加所有文件
    if not run_command("git add .", "添加所有文件到暂存区"):
        return
    
    # 提交更改
    if not run_command('git commit -m "Update for Railway deployment"', "提交更改"):
        return
    
    print("\n" + "=" * 50)
    print("Git操作完成！")
    print("\n现在请手动执行以下步骤：")
    print("\n1. 在GitHub上创建新仓库:")
    print("   - 访问 https://github.com")
    print("   - 点击 'New repository'")
    print("   - 仓库名: block-trade-dt")
    print("   - 设置为公开仓库")
    print("   - 点击 'Create repository'")
    
    print("\n2. 添加远程仓库并推送:")
    print("   git remote add origin https://github.com/YOUR_USERNAME/block-trade-dt.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    
    print("\n注意: 请将 YOUR_USERNAME 替换为您的GitHub用户名")

if __name__ == "__main__":
    main()

