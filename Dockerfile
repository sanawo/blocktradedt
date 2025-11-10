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

# 暴露端口（Zeabur 会动态设置 PORT 环境变量，通常是 8080）
# EXPOSE 只是文档性的，实际端口由 PORT 环境变量决定
EXPOSE 8080

# 健康检查（使用 PORT 环境变量，Zeabur 会自动设置）
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD sh -c "curl -f http://localhost:${PORT:-8080}/health || exit 1"

# 启动命令 - 使用环境变量 PORT（Zeabur 会自动设置为 8080）
# 简化启动命令，确保可靠启动
CMD python -m uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8080} --log-level info

