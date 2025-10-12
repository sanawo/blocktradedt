#!/usr/bin/env python3
"""
Railway部署助手脚本
"""
import os
import subprocess
import sys

def check_git():
    """检查Git是否已安装"""
    try:
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        print("✅ Git已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git未安装，请先安装Git")
        return False

def check_git_repo():
    """检查是否为Git仓库"""
    if os.path.exists('.git'):
        print("✅ 当前目录是Git仓库")
        return True
    else:
        print("❌ 当前目录不是Git仓库")
        return False

def init_git_repo():
    """初始化Git仓库"""
    try:
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit for Railway deployment'], check=True)
        print("✅ Git仓库初始化完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git仓库初始化失败: {e}")
        return False

def create_gitignore():
    """创建.gitignore文件"""
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# Database
*.db
*.sqlite
*.sqlite3

# Environment variables
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content.strip())
    print("✅ .gitignore文件已创建")

def main():
    """主函数"""
    print("Railway部署助手")
    print("=" * 50)
    
    # 检查Git
    if not check_git():
        print("\n请先安装Git: https://git-scm.com/downloads")
        return
    
    # 创建.gitignore
    if not os.path.exists('.gitignore'):
        create_gitignore()
    
    # 检查Git仓库
    if not check_git_repo():
        print("\n正在初始化Git仓库...")
        if not init_git_repo():
            return
    
    print("\n部署准备完成！")
    print("\n下一步操作：")
    print("1. 访问 https://railway.app")
    print("2. 使用GitHub账户登录")
    print("3. 点击 'New Project' -> 'Deploy from GitHub repo'")
    print("4. 选择您的仓库")
    print("5. 在环境变量中设置：")
    print("   - ZHIPU_API_KEY=7aee1f12feb24b5f8c298d445ddc6923.IphCkMRMDt0l0aAV")
    print("   - JWT_SECRET_KEY=your-super-secret-jwt-key-here")
    print("   - DATABASE_URL=sqlite:///./block_trade_dt.db")
    print("\n部署完成后，您将获得一个公网URL！")

if __name__ == "__main__":
    main()
