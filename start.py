#!/usr/bin/env python3
"""
启动脚本 - 用于调试和启动应用
"""
import os
import sys
import uvicorn
from app.main import app

def main():
    """主函数"""
    print("🚀 启动 Block Trade DT 应用...")
    
    # 打印环境信息
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print(f"环境变量:")
    print(f"  - DATABASE_URL: {os.getenv('DATABASE_URL', '未设置')}")
    print(f"  - JWT_SECRET_KEY: {'已设置' if os.getenv('JWT_SECRET_KEY') else '未设置'}")
    print(f"  - ZHIPU_API_KEY: {'已设置' if os.getenv('ZHIPU_API_KEY') else '未设置'}")
    print(f"  - HOST: {os.getenv('HOST', '0.0.0.0')}")
    print(f"  - PORT: {os.getenv('PORT', '8000')}")
    
    # 启动应用
    try:
        uvicorn.run(
            "app.main:app",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8000)),
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
