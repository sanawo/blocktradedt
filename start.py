#!/usr/bin/env python3
"""
启动脚本 - 用于调试和启动应用
"""
import os
import sys
import traceback

def main():
    """主函数"""
    print("🚀 启动 Block Trade DT 应用...")
    
    try:
        # 打印环境信息
        print(f"Python版本: {sys.version}")
        print(f"工作目录: {os.getcwd()}")
        print(f"环境变量:")
        print(f"  - DATABASE_URL: {os.getenv('DATABASE_URL', '未设置')}")
        print(f"  - JWT_SECRET_KEY: {'已设置' if os.getenv('JWT_SECRET_KEY') else '未设置'}")
        print(f"  - ZHIPU_API_KEY: {'已设置' if os.getenv('ZHIPU_API_KEY') else '未设置'}")
        print(f"  - HOST: {os.getenv('HOST', '0.0.0.0')}")
        print(f"  - PORT: {os.getenv('PORT', '8000')}")
        
        # 检查依赖
        print("📦 检查依赖...")
        try:
            import fastapi
            print(f"  ✅ FastAPI: {fastapi.__version__}")
        except ImportError as e:
            print(f"  ❌ FastAPI导入失败: {e}")
            return
        
        try:
            import uvicorn
            print(f"  ✅ Uvicorn: {uvicorn.__version__}")
        except ImportError as e:
            print(f"  ❌ Uvicorn导入失败: {e}")
            return
        
        try:
            import sqlalchemy
            print(f"  ✅ SQLAlchemy: {sqlalchemy.__version__}")
        except ImportError as e:
            print(f"  ❌ SQLAlchemy导入失败: {e}")
            return
        
        # 导入应用
        print("📱 导入应用...")
        try:
            from app.main import app
            print("  ✅ 应用导入成功")
        except Exception as e:
            print(f"  ❌ 应用导入失败: {e}")
            print(f"  详细错误: {traceback.format_exc()}")
            return
        
        # 启动应用
        print("🌐 启动服务器...")
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8000)),
            reload=False,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
