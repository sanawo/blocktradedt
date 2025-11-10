# Zeabur 登录问题解决方案

## 🚨 问题描述

无法通过 Zeabur CLI 登录 gateway zeabur。

## ✅ 解决方案

### 方案 1: 使用 Zeabur Dashboard（推荐）

**这个项目主要通过 GitHub 自动部署，不需要 CLI 登录！**

#### 步骤：

1. **访问 Zeabur Dashboard**
   - 打开浏览器访问：https://dash.zeabur.com
   - 使用您的账号登录（支持 GitHub、Google 或邮箱登录）

2. **手动触发部署**
   - 找到您的项目（blocktradedt）
   - 点击服务卡片
   - 点击右上角的 **"Redeploy"** 或 **"重新部署"** 按钮
   - 等待 3-5 分钟完成部署

3. **查看部署状态**
   - 在服务页面查看 "Logs" 标签
   - 确认部署成功

---

### 方案 2: 使用 Token 登录 CLI

如果您确实需要使用 CLI，可以通过 token 方式登录：

#### 步骤 1: 获取 Zeabur Token

1. **访问 Zeabur Dashboard**
   - 打开：https://dash.zeabur.com
   - 登录您的账号

2. **生成 API Token**
   - 点击右上角头像 → **Settings**（设置）
   - 找到 **API Tokens** 或 **Access Tokens** 部分
   - 点击 **"Create Token"** 或 **"生成令牌"**
   - 复制生成的 token（只显示一次，请妥善保存）

#### 步骤 2: 使用 Token 登录 CLI

```bash
# 使用 token 登录（不需要浏览器）
zeabur auth login --token YOUR_TOKEN_HERE
```

**示例：**
```bash
zeabur auth login --token zbr_xxxxxxxxxxxxxxxxxxxxx
```

#### 步骤 3: 验证登录状态

```bash
# 检查登录状态
zeabur auth status
```

#### 步骤 4: 部署项目

```bash
# 部署当前目录的项目
zeabur deploy
```

---

### 方案 3: 解决浏览器登录问题

如果浏览器登录失败，尝试以下方法：

#### 1. 清除浏览器缓存和 Cookie
- Chrome/Edge: `Ctrl + Shift + Delete` → 清除缓存和 Cookie
- 重新访问 https://dash.zeabur.com

#### 2. 尝试不同的登录方式
- **GitHub 登录**（推荐）
- **Google 登录**
- **邮箱登录**

#### 3. 检查网络连接
- 确保可以访问 https://dash.zeabur.com
- 检查防火墙设置
- 尝试使用 VPN（如果在受限网络环境）

#### 4. 使用无痕模式
- 打开浏览器无痕/隐私模式
- 访问 https://dash.zeabur.com
- 尝试登录

---

## 🎯 推荐工作流程

### 对于这个项目，推荐使用以下方式：

1. **代码更改后推送到 GitHub**
   ```bash
   git add .
   git commit -m "your commit message"
   git push origin master
   ```

2. **在 Zeabur Dashboard 手动触发部署**
   - 访问 https://dash.zeabur.com
   - 找到项目 → 点击服务 → 点击 "Redeploy"

3. **等待自动部署完成**
   - 查看部署日志
   - 确认服务状态为 "运行中"

---

## 🔍 故障排查

### 如果 CLI 登录仍然失败

#### 检查 CLI 版本
```bash
zeabur version
```

#### 更新 CLI
```bash
npm install -g @zeabur/cli@latest
```

#### 查看详细错误信息
```bash
zeabur auth login --debug
```

#### 检查网络代理设置
如果使用代理，可能需要配置：
```bash
# Windows PowerShell
$env:HTTP_PROXY="http://proxy.example.com:8080"
$env:HTTPS_PROXY="http://proxy.example.com:8080"
```

---

## 📞 获取帮助

### Zeabur 官方支持
- **Discord**: https://discord.gg/zeabur
- **文档**: https://zeabur.com/docs
- **状态页**: https://status.zeabur.com

### 项目支持
- **GitHub**: https://github.com/sanawo/blocktradedt
- **邮箱**: 2787618474@qq.com

---

## ✅ 快速检查清单

- [ ] 已尝试通过 Dashboard 登录
- [ ] 已尝试使用 Token 登录 CLI
- [ ] 已清除浏览器缓存
- [ ] 已检查网络连接
- [ ] 已更新 CLI 到最新版本
- [ ] 已查看 Zeabur 状态页

---

## 💡 重要提示

1. **这个项目主要通过 GitHub 自动部署**，通常不需要 CLI
2. **如果自动部署未触发**，在 Dashboard 手动点击 "Redeploy" 即可
3. **CLI 主要用于高级操作**，日常部署推荐使用 Dashboard
4. **Token 登录更稳定**，如果必须使用 CLI，推荐使用 token 方式

---

**最后更新**: 2025年1月27日  
**状态**: ✅ 解决方案已提供

