# Zeabur 部署触发指南

## ✅ 代码已推送成功

Commit: `28315a3 - feat: Add dark mode trends page and clickable news links`

推送到: `https://github.com/sanawo/blocktradedt.git`

---

## 🔍 Zeabur 自动构建检查

### 方法 1: 检查 Zeabur Dashboard

1. 访问 [Zeabur Dashboard](https://dash.zeabur.com)
2. 找到你的项目（应该叫 blocktradedt 或类似名称）
3. 查看服务状态

**检查项：**
- ✅ GitHub 仓库是否正确连接？
- ✅ 分支是否设置为 `master`？
- ✅ 是否有新的构建记录？

---

### 方法 2: 手动触发重新部署

如果自动构建没有触发，可以手动触发：

#### 在 Zeabur Dashboard 中：

1. 进入你的项目
2. 找到 Block Trade DT 服务
3. 点击服务卡片右上角的 **⋯** (三个点)
4. 选择 **"Redeploy"** 或 **"Rebuild"**
5. 等待构建完成（约 3-5 分钟）

#### 或者重新触发部署：

```bash
# 创建一个空提交来触发部署
git commit --allow-empty -m "trigger: Rebuild on Zeabur"
git push origin master
```

---

### 方法 3: 检查 GitHub Webhook

Zeabur 应该已经自动配置了 GitHub Webhook。检查方法：

1. 访问 GitHub 仓库：https://github.com/sanawo/blocktradedt
2. 进入 **Settings** → **Webhooks**
3. 查看是否有 Zeabur 的 webhook
4. 确认 webhook 状态为 ✅ 绿色（成功）

如果 webhook 显示错误：
- 点击 webhook 查看详细日志
- 可能需要在 Zeabur 中重新连接 GitHub

---

## 🚀 快速解决方案

### 立即触发构建（推荐）

在 Zeabur Dashboard 中：

1. **进入项目** → www.blocktradedt.xyz 的项目
2. **找到服务** → 点击服务卡片
3. **点击 Redeploy** → 右上角三个点菜单
4. **等待构建** → 查看 Build Logs

### 验证构建是否开始

构建开始的标志：
- ✅ Build Logs 有新的日志输出
- ✅ 服务状态变为 "Building" 或 "Deploying"
- ✅ 可以看到 Docker 构建过程

---

## 📊 构建预计时间

- **构建阶段**：3-5 分钟
  - 拉取代码
  - 构建 Docker 镜像
  - 安装依赖
  
- **部署阶段**：1-2 分钟
  - 启动容器
  - 健康检查
  - 切换流量

**总计**：约 5-7 分钟

---

## 🔍 查看构建日志

在 Zeabur 服务页面：

1. 点击 **"Logs"** 标签
2. 选择 **"Build Logs"** 查看构建过程
3. 选择 **"Runtime Logs"** 查看运行日志

---

## ✨ 部署后验证

构建成功后，访问以下链接验证新功能：

### 1. 深色模式趋势页面
```
https://www.blocktradedt.xyz/trends
```

**验证点：**
- ✅ 页面是深色背景
- ✅ 图表正常显示
- ✅ 数据自动更新

### 2. 实时新闻页面
```
https://www.blocktradedt.xyz/news
```

**验证点：**
- ✅ 新闻列表显示
- ✅ 点击新闻可以打开链接
- ✅ 分类筛选功能正常
- ✅ 自动刷新（30秒）

### 3. API 端点
```
https://www.blocktradedt.xyz/api/news?limit=5
https://www.blocktradedt.xyz/api/news/latest?limit=3
https://www.blocktradedt.xyz/api/trends/data
```

---

## ⚠️ 常见问题

### Q1: Zeabur 显示 "No new changes"
**原因：** Zeabur 可能缓存了旧的 commit
**解决：** 手动点击 Redeploy 强制重新构建

### Q2: 构建失败
**检查：**
1. Build Logs 中的错误信息
2. 依赖是否缺失
3. Dockerfile 是否正确

**解决：**
```bash
# 本地测试构建
docker build -t test .

# 如果失败，修复后重新推送
git add .
git commit -m "fix: Build issues"
git push origin master
```

### Q3: 部署成功但功能不生效
**原因：** 浏览器缓存
**解决：**
1. 硬刷新页面（Ctrl+Shift+R 或 Cmd+Shift+R）
2. 清除浏览器缓存
3. 使用隐私模式访问

---

## 📞 需要帮助？

如果问题持续：

1. **查看 Zeabur 状态**
   - https://status.zeabur.com
   
2. **检查 GitHub Actions**（如果配置了）
   - https://github.com/sanawo/blocktradedt/actions

3. **Zeabur Discord 支持**
   - https://discord.gg/zeabur

---

## ✅ 确认清单

部署检查：
- [x] 代码已推送到 GitHub ✅
- [ ] Zeabur 开始构建
- [ ] 构建成功完成
- [ ] 新功能可以访问
- [ ] 所有链接正常工作

---

**下一步：**
1. 访问 Zeabur Dashboard 手动触发 Redeploy
2. 等待 5-7 分钟构建完成
3. 访问 https://www.blocktradedt.xyz/trends 和 /news 验证功能

**提示：** 如果自动构建没有触发，手动 Redeploy 是最快的解决方案！






















