@echo off
REM 触发 Zeabur 重新构建的脚本
echo ========================================
echo 触发 Zeabur 重新构建
echo ========================================
echo.

REM 检查 git 状态
echo [1/4] 检查 Git 状态...
git status
echo.

REM 添加所有更改
echo [2/4] 添加所有更改...
git add -A
echo.

REM 创建空提交
echo [3/4] 创建触发构建的提交...
git commit -m "chore: trigger Zeabur rebuild - $(date /t)"
echo.

REM 推送到 GitHub
echo [4/4] 推送到 GitHub...
git push origin master
echo.

echo ========================================
echo ✅ 完成！已触发 Zeabur 重新构建
echo ========================================
echo.
echo 📋 下一步：
echo 1. 等待 2-3 分钟让 Zeabur 检测到新提交
echo 2. 访问 Zeabur Dashboard: https://dash.zeabur.com
echo 3. 进入你的项目 → 服务 → Deployments
echo 4. 查看最新的部署状态和构建日志
echo.
pause

