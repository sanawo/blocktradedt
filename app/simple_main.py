"""
简化版FastAPI应用 - 用于调试
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import traceback

# 创建FastAPI应用
app = FastAPI(title="Block Trade DT - Simple", description="大宗交易数据检索平台 - 简化版")

# 静态文件和模板
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
    print("✅ 静态文件和模板加载成功")
except Exception as e:
    print(f"⚠️ 静态文件加载失败: {e}")

@app.get("/")
async def root():
    """根路径 - 返回简单响应"""
    return {"message": "Block Trade DT API is running!", "status": "ok"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "服务运行正常",
        "environment": {
            "python_version": os.sys.version,
            "working_directory": os.getcwd(),
            "database_url": os.getenv("DATABASE_URL", "未设置"),
            "jwt_secret": "已设置" if os.getenv("JWT_SECRET_KEY") else "未设置",
            "zhipu_api_key": "已设置" if os.getenv("ZHIPU_API_KEY") else "未设置"
        }
    }

@app.get("/test")
async def test_endpoint():
    """测试端点"""
    try:
        # 测试导入
        from app.config import Config
        from app.models import Base
        from app.schemas import UserCreate
        
        return {
            "status": "success",
            "message": "所有模块导入成功",
            "config": {
                "database_url": Config.get_database_url(),
                "jwt_secret": "已设置" if Config.get_jwt_secret_key() else "未设置",
                "zhipu_api_key": "已设置" if Config.get_zhipu_api_key() else "未设置"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"模块导入失败: {str(e)}",
            "traceback": traceback.format_exc()
        }

@app.get("/simple", response_class=HTMLResponse)
async def simple_page():
    """简单HTML页面"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Block Trade DT - 简化版</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .error { background: #ffe8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Block Trade DT</h1>
            <div class="status">
                <h3>✅ 应用运行正常</h3>
                <p>简化版应用已成功启动，所有基础功能正常。</p>
            </div>
            <div class="info">
                <h3>📋 可用端点</h3>
                <ul>
                    <li><a href="/">/ - 根路径</a></li>
                    <li><a href="/health">/health - 健康检查</a></li>
                    <li><a href="/test">/test - 模块测试</a></li>
                    <li><a href="/simple">/simple - 此页面</a></li>
                </ul>
            </div>
            <div class="info">
                <h3>🔧 下一步</h3>
                <p>如果此页面正常显示，说明基础环境配置正确。接下来可以：</p>
                <ol>
                    <li>配置环境变量</li>
                    <li>测试数据库连接</li>
                    <li>启用完整功能</li>
                </ol>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
