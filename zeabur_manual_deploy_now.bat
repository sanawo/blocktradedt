@echo off
echo 🚨 Zeabur 手动部署紧急指南
echo.

echo 📊 当前状态:
echo ✅ GitHub推送成功 (GitHub Desktop显示无本地更改)
echo ✅ 代码已同步到GitHub
echo ❌ Zeabur未自动检测到更改
echo 🔧 需要手动触发重新部署
echo.

echo 🚀 立即解决方案:
echo.
echo 步骤1: 访问Zeabur Dashboard
echo 1. 打开浏览器
echo 2. 访问: https://dash.zeabur.com
echo 3. 登录您的账户
echo.

echo 步骤2: 找到项目
echo 1. 在项目列表中找到: blocktradedt
echo 2. 点击项目名称进入详情页
echo.

echo 步骤3: 手动触发重新部署
echo 1. 找到服务名称 (通常是项目名)
echo 2. 查找 "重新部署" 或 "Redeploy" 按钮
echo 3. 点击重新部署按钮
echo 4. 确认操作
echo.

echo 步骤4: 监控部署过程
echo 1. 查看部署日志
echo 2. 等待3-5分钟完成
echo 3. 确保状态变为 "运行中"
echo.

echo 📊 部署验证:
echo 部署完成后访问: https://www.blocktradedt.xyz
echo 检查内容:
echo - ✅ 网站正常加载
echo - ✅ 新logo显示正确
echo - ✅ 邮箱联系方式显示
echo - ✅ 无崩溃错误
echo - ✅ 所有功能正常
echo.

echo 🔧 修复内容:
echo - 降级 numpy: 1.24.3 → 1.21.6
echo - 降级 pandas: 2.0.3 → 1.5.3
echo - 降级 sentence-transformers: 5.1.1 → 2.2.2
echo - 解决二进制不兼容问题
echo.

echo 🐛 如果部署失败:
echo 1. 检查Zeabur部署日志
echo 2. 查看错误信息
echo 3. 尝试进一步降级版本
echo 4. 联系技术支持
echo.

echo 📞 技术支持:
echo 📧 邮箱: 2787618474@qq.com
echo 🐛 GitHub: https://github.com/sanawo/blocktradedt/issues
echo 💬 Zeabur Discord: https://discord.gg/zeabur
echo.

echo ⏳ 预计部署时间: 3-5分钟
echo 🌍 部署后访问: https://www.blocktradedt.xyz
echo.

echo 💡 重要提示: 必须手动触发Zeabur重新部署！
echo.

pause
