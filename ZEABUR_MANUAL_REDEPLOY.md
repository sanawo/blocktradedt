# Zeabur 手动重新部署指南

## 🚨 问题诊断
Zeabur未检测到GitHub推送的更改，需要手动触发重新部署。

## 🔧 解决方案

### 方法1: Zeabur Dashboard 手动重新部署

1. **访问Zeabur Dashboard**
   - 打开: https://dash.zeabur.com
   - 登录您的账户

2. **找到项目**
   - 在项目列表中找到 `blocktradedt` 项目
   - 点击进入项目详情

3. **手动触发重新部署**
   - 点击服务名称
   - 找到 "重新部署" 或 "Redeploy" 按钮
   - 点击触发重新部署

4. **监控部署状态**
   - 查看部署日志
   - 等待2-3分钟完成部署

### 方法2: 检查GitHub Webhook

1. **检查GitHub仓库设置**
   - 访问: https://github.com/sanawo/blocktradedt/settings/hooks
   - 确认有Zeabur的webhook配置

2. **重新配置Webhook**
   - 删除现有webhook
   - 在Zeabur中重新连接GitHub仓库

### 方法3: 强制推送触发

```bash
# 创建一个空commit来触发部署
git commit --allow-empty -m "trigger: Force redeploy"
git push origin master
```

## 📊 部署状态检查

### 1. GitHub状态
- ✅ 最新commit: `9637c32 fix: Fix numpy compatibility and update logo`
- ✅ 推送时间: 刚刚完成
- ✅ 仓库地址: https://github.com/sanawo/blocktradedt

### 2. Zeabur状态检查
访问: https://dash.zeabur.com
- 检查项目状态
- 查看部署历史
- 确认webhook连接

### 3. 服务状态
访问: https://www.blocktradedt.xyz
- 检查网站是否正常运行
- 验证新logo是否显示
- 测试功能是否正常

## 🐛 故障排查

### 常见问题

#### 1. Webhook未配置
**症状**: Zeabur不检测GitHub推送
**解决**: 在Zeabur中重新连接GitHub仓库

#### 2. 权限问题
**症状**: 无法访问私有仓库
**解决**: 确认GitHub token权限

#### 3. 分支配置错误
**症状**: 监听错误的分支
**解决**: 确认监听master分支

#### 4. 服务配置问题
**症状**: 部署失败
**解决**: 检查服务配置和依赖

## 🚀 快速修复步骤

### 步骤1: 立即检查
1. 访问 https://dash.zeabur.com
2. 找到blocktradedt项目
3. 点击"重新部署"

### 步骤2: 如果重新部署失败
1. 检查部署日志
2. 确认requirements.txt正确
3. 验证服务配置

### 步骤3: 验证部署
1. 等待2-3分钟
2. 访问 https://www.blocktradedt.xyz
3. 检查新logo和功能

## 📞 技术支持

### Zeabur支持
- Discord: https://discord.gg/zeabur
- 文档: https://zeabur.com/docs
- 状态页: https://status.zeabur.com

### 项目支持
- GitHub Issues: https://github.com/sanawo/blocktradedt/issues
- 部署日志: Zeabur Dashboard

---

## 🎯 预期结果

部署成功后，您应该看到：
- ✅ 网站正常访问
- ✅ 新logo显示正确
- ✅ numpy兼容性问题解决
- ✅ 所有功能正常运行

**预计部署时间**: 2-3分钟  
**部署完成后访问**: https://www.blocktradedt.xyz
