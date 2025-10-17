@echo off
echo 🚀 东方财富网数据平台部署脚本
echo.

echo 📋 检查git状态...
git status
echo.

echo 📦 添加所有更改...
git add .
echo.

echo 💾 提交更改...
git commit -m "feat: Integrate East Money data scraper and remove Zhipu AI"
echo.

echo 🌐 尝试推送到GitHub...
echo 方法1: 直接推送
git push origin master
if %errorlevel% equ 0 (
    echo ✅ 推送成功！
    goto :success
)

echo.
echo 方法2: 使用HTTPS推送
git push https://github.com/sanawo/blocktradedt.git master
if %errorlevel% equ 0 (
    echo ✅ 推送成功！
    goto :success
)

echo.
echo ❌ 推送失败，请手动推送
echo 💡 您可以：
echo    1. 使用GitHub Desktop
echo    2. 使用VS Code的Git功能
echo    3. 检查网络连接后重试
goto :end

:success
echo.
echo 🎉 部署成功！
echo ⏳ Zeabur将自动检测到更改并开始部署
echo 🌍 部署完成后访问: https://www.blocktradedt.xyz
echo.

:end
echo 📊 部署状态检查：
echo    1. GitHub仓库: https://github.com/sanawo/blocktradedt
echo    2. Zeabur Dashboard: https://dash.zeabur.com
echo    3. 网站地址: https://www.blocktradedt.xyz
echo.
pause
