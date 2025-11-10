"""
检查并安装项目依赖
"""
import sys
import subprocess
import io

# 设置输出编码（Windows）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REQUIRED_PACKAGES = [
    'fastapi',
    'uvicorn',
    'jinja2',
    'pydantic',
    'requests',
    'beautifulsoup4',
    'lxml',
    'sqlalchemy',
    'bcrypt',
    'python-dotenv',
]

def check_package(package_name):
    """检查包是否已安装"""
    try:
        if package_name == 'beautifulsoup4':
            __import__('bs4')
        else:
            __import__(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """安装包"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("=" * 60)
    print("检查项目依赖")
    print("=" * 60)
    
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        print(f"检查 {package}...", end=" ")
        if check_package(package):
            print("[OK] 已安装")
        else:
            print("[X] 未安装")
            missing_packages.append(package)
    
    if not missing_packages:
        print("\n[SUCCESS] 所有依赖已安装！")
        return
    
    print(f"\n[WARNING] 发现 {len(missing_packages)} 个缺失的包")
    print("\n缺失的包：")
    for pkg in missing_packages:
        print(f"  - {pkg}")
    
    response = input("\n是否自动安装缺失的包？(y/n): ").strip().lower()
    if response == 'y':
        print("\n开始安装...")
        for pkg in missing_packages:
            print(f"\n安装 {pkg}...", end=" ")
            if install_package(pkg):
                print("[OK] 成功")
            else:
                print("[X] 失败")
        
        print("\n" + "=" * 60)
        print("重新检查依赖...")
        print("=" * 60)
        
        still_missing = []
        for package in missing_packages:
            if not check_package(package):
                still_missing.append(package)
        
        if still_missing:
            print("\n[WARNING] 以下包安装失败，请手动安装：")
            for pkg in still_missing:
                print(f"  pip install {pkg}")
        else:
            print("\n[SUCCESS] 所有依赖已成功安装！")
    else:
        print("\n请手动安装缺失的包：")
        print(f"pip install {' '.join(missing_packages)}")
        print("\n或使用：")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()

