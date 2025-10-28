@echo off
echo ========================================
echo 部署到 www.blocktradedt.xyz
echo ========================================
echo.

echo 1. 检查Git状态...
git status
echo.

echo 2. 推送代码到GitHub...
git push origin master

if %errorlevel% equ 0 (
    echo 推送成功！
    echo.
    echo 3. Zeabur将自动检测更新并部署
    echo.
    echo 部署流程：
    echo - 等待Zeabur检测到GitHub更新（约1-2分钟）
    echo - 自动触发构建和部署
    echo - 部署完成时间：约3-5分钟
    echo.
    echo 如果自动部署未触发，请访问Zeabur控制台手动触发重新部署
    echo https://dash.zeabur.com
) else (
    echo 推送失败，请检查：
    echo 1. 网络连接是否正常
    echo 2. GitHub凭据是否正确
    echo 3. 是否配置了代理
    echo.
    echo 手动推送命令：
    echo git push origin master
    echo.
)

pause

