#!/bin/bash

echo "🚀 Starting Block Trade DT Application..."
echo "================================"

# 打印环境信息
echo "📋 Environment Information:"
echo "  - Python Version: $(python --version)"
echo "  - Working Directory: $(pwd)"
echo "  - PORT: ${PORT:-8000}"
echo ""

# 检查关键目录
echo "📁 Checking directories:"
for dir in static templates data artifacts app api; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir exists"
    else
        echo "  ⚠️  $dir NOT found"
    fi
done
echo ""

# 检查关键文件
echo "📄 Checking key files:"
for file in data/sample_listings.jsonl; do
    if [ -f "$file" ]; then
        echo "  ✅ $file exists"
    else
        echo "  ⚠️  $file NOT found"
    fi
done
echo ""

# 检查环境变量
echo "🔐 Environment Variables:"
if [ -n "$DATABASE_URL" ]; then
    echo "  ✅ DATABASE_URL is set"
else
    echo "  ℹ️  DATABASE_URL not set (will use default)"
fi

if [ -n "$JWT_SECRET_KEY" ]; then
    echo "  ✅ JWT_SECRET_KEY is set"
else
    echo "  ⚠️  JWT_SECRET_KEY not set (will use default)"
fi

if [ -n "$ZHIPU_API_KEY" ]; then
    echo "  ✅ ZHIPU_API_KEY is set"
else
    echo "  ℹ️  ZHIPU_API_KEY not set (AI features disabled)"
fi
echo ""

# 启动应用
echo "🌐 Starting Uvicorn server..."
echo "================================"
exec python -m uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info



















