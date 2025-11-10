# 使用官方Python运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量（提前设置以优化缓存）
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件（利用Docker缓存层）
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口（Zeabur 会动态设置 PORT 环境变量）
EXPOSE 8000

# 健康检查（使用固定端口，Zeabur 会在容器内使用相同端口）
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD sh -c "curl -f http://localhost:${PORT:-8000}/health || exit 1"

# 启动命令 - 使用环境变量 PORT（Zeabur 会自动设置）
# 添加详细的启动日志和错误处理
CMD sh -c "echo '🚀 Starting application...' && \
           echo '📋 Environment:' && \
           echo '  PORT=${PORT:-8000}' && \
           echo '  PYTHONPATH=${PYTHONPATH:-/app}' && \
           echo '  Working directory: $(pwd)' && \
           echo '📁 Checking files...' && \
           ls -la /app/api/index.py 2>&1 && \
           echo '📦 Checking Python imports...' && \
           python -c 'import sys; sys.path.insert(0, \"/app\"); from api.index import app; print(\"✅ App imported successfully\")' 2>&1 && \
           echo '✅ Starting uvicorn...' && \
           python -m uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info --access-log --timeout-keep-alive 30 || \
           (echo '❌ Uvicorn failed, trying alternative...' && \
            python -c 'import uvicorn; from api.index import app; uvicorn.run(app, host=\"0.0.0.0\", port=int(\"${PORT:-8000}\"), log_level=\"info\")')"

