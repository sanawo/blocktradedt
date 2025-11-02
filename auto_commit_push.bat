@echo off
chcp 65001 >nul
echo ========================================
echo 自动提交并推送到 GitHub
echo ========================================
echo.

echo [1/3] 检查 Git 状态...
git status --short
echo.

echo [2/3] 添加所有更改...
git add .
if %errorlevel% neq 0 (
    echo 错误: git add 失败
    pause
    exit /b 1
)
echo.

echo [3/3] 提交更改...
set /p commit_msg="请输入提交信息 (直接回车使用默认): "
if "%commit_msg%"=="" set commit_msg=Auto commit: %date% %time%
git commit -m "%commit_msg%"
if %errorlevel% neq 0 (
    echo 错误: git commit 失败
    pause
    exit /b 1
)
echo.

echo [4/4] 推送到 GitHub...
git push origin master
if %errorlevel% neq 0 (
    echo 错误: git push 失败
    pause
    exit /b 1
)
echo.

echo ========================================
echo ✅ 完成！代码已推送到 GitHub
echo ========================================
pause

