@echo off
chcp 65001 >nul
echo ========================================
echo 🔧 修复502错误 - 部署脚本
echo ========================================
echo.

echo 📋 步骤1: 检查Git状态
git status
echo.

echo 📋 步骤2: 添加所有更改
git add .
echo.

echo 📋 步骤3: 提交更改
git commit -m "fix: 简化启动命令，修复502错误

- 简化Dockerfile CMD命令
- 添加.zeaburrc配置文件
- 确保端口配置正确"
echo.

echo 📋 步骤4: 推送到GitHub
git push origin master
echo.

echo ========================================
echo ✅ 代码已推送到GitHub
echo ========================================
echo.
echo 📝 下一步:
echo 1. 访问 https://dash.zeabur.com
echo 2. 进入你的项目
echo 3. 点击 blocktradedt 服务
echo 4. 等待自动部署（2-3分钟）
echo 5. 查看部署日志确认启动成功
echo 6. 访问 https://www.blocktradedt.xyz/health 验证
echo.
echo 如果仍有问题，请查看 ZEABUR_502_FIX.md 文件
echo.
pause

