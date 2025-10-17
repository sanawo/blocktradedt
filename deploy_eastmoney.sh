#!/bin/bash

# 东方财富网数据平台部署脚本
echo "🚀 开始部署东方财富网数据平台..."

# 检查git状态
echo "📋 检查git状态..."
git status

# 添加所有更改
echo "📦 添加所有更改..."
git add .

# 提交更改
echo "💾 提交更改..."
git commit -m "feat: Integrate East Money data scraper and remove Zhipu AI

- Add East Money data scraper (app/eastmoney_scraper.py)
- Remove all Zhipu AI related code and config
- Update API endpoints for East Money data
- Replace logo with East Money branding
- Update frontend interface and branding
- Add real-time data update functionality
- Update dependencies (beautifulsoup4, pandas, lxml)"

# 推送到GitHub
echo "🌐 推送到GitHub..."
git push origin master

if [ $? -eq 0 ]; then
    echo "✅ 代码已成功推送到GitHub"
    echo "🔄 Zeabur将自动检测到更改并开始部署..."
    echo "⏳ 请等待2-3分钟完成部署"
    echo "🌍 部署完成后访问: https://www.blocktradedt.xyz"
else
    echo "❌ 推送到GitHub失败，请检查网络连接或权限"
    echo "💡 您可以手动执行以下命令："
    echo "   git push origin master"
fi

echo "📊 部署状态检查："
echo "1. 检查GitHub仓库: https://github.com/sanawo/blocktradedt"
echo "2. 检查Zeabur部署状态"
echo "3. 访问网站: https://www.blocktradedt.xyz"

echo "🎉 部署脚本执行完成！"
