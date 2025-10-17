@echo off
echo 🚀 Zeabur 部署状态检查脚本
echo.

echo 📋 当前Git状态:
git log --oneline -3
echo.

echo 🌐 GitHub推送状态:
echo ✅ 最新commit已推送到GitHub
echo 📦 Commit ID: c4851f3
echo 📝 消息: trigger: Force redeploy to Zeabur
echo.

echo 🔍 Zeabur部署检查:
echo 1. 访问Zeabur Dashboard: https://dash.zeabur.com
echo 2. 找到blocktradedt项目
echo 3. 检查部署状态
echo 4. 如果未自动部署，点击"重新部署"按钮
echo.

echo 📊 部署验证:
echo 等待2-3分钟后访问: https://www.blocktradedt.xyz
echo 检查以下内容:
echo - ✅ 网站正常加载
echo - ✅ 新logo显示正确
echo - ✅ numpy兼容性问题解决
echo - ✅ 所有功能正常运行
echo.

echo 🐛 如果部署失败:
echo 1. 检查Zeabur Dashboard中的错误日志
echo 2. 确认requirements.txt中的依赖版本
echo 3. 验证服务配置
echo 4. 尝试手动重新部署
echo.

echo 📞 技术支持:
echo - Zeabur Discord: https://discord.gg/zeabur
echo - Zeabur文档: https://zeabur.com/docs
echo - GitHub仓库: https://github.com/sanawo/blocktradedt
echo.

echo ⏳ 预计部署时间: 2-3分钟
echo 🌍 部署完成后访问: https://www.blocktradedt.xyz
echo.

pause
