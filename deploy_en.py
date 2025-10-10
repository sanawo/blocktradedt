#!/usr/bin/env python3
"""
Railway Deployment Helper Script
"""
import os
import subprocess
import sys

def check_git():
    """Check if Git is installed"""
    try:
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        print("Git is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Git is not installed. Please install Git first.")
        return False

def check_git_repo():
    """Check if current directory is a Git repository"""
    if os.path.exists('.git'):
        print("Current directory is a Git repository")
        return True
    else:
        print("Current directory is not a Git repository")
        return False

def init_git_repo():
    """Initialize Git repository"""
    try:
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit for Railway deployment'], check=True)
        print("Git repository initialized successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to initialize Git repository: {e}")
        return False

def create_gitignore():
    """Create .gitignore file"""
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
    print(".gitignore file created")

def main():
    """Main function"""
    print("Railway Deployment Helper")
    print("=" * 50)
    
    # Check Git
    if not check_git():
        print("\nPlease install Git first: https://git-scm.com/downloads")
        return
    
    # Create .gitignore
    if not os.path.exists('.gitignore'):
        create_gitignore()
    
    # Check Git repository
    if not check_git_repo():
        print("\nInitializing Git repository...")
        if not init_git_repo():
            return
    
    print("\nDeployment preparation completed!")
    print("\nNext steps:")
    print("1. Visit https://railway.app")
    print("2. Login with your GitHub account")
    print("3. Click 'New Project' -> 'Deploy from GitHub repo'")
    print("4. Select your repository")
    print("5. Set environment variables:")
    print("   - ZHIPU_API_KEY=7aee1f12feb24b5f8c298d445ddc6923.IphCkMRMDt0l0aAV")
    print("   - JWT_SECRET_KEY=your-super-secret-jwt-key-here")
    print("   - DATABASE_URL=sqlite:///./block_trade_dt.db")
    print("\nAfter deployment, you will get a public URL!")

if __name__ == "__main__":
    main()
