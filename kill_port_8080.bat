@echo off
echo 正在查找占用 8080 端口的进程...
netstat -ano | findstr :8080

echo.
echo 正在关闭占用 8080 端口的进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    echo 关闭进程 PID: %%a
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo 完成！现在可以重新启动服务器了。
pause

