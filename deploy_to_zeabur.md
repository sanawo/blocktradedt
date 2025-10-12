# 🚀 快速部署到 Zeabur

## 第一步：准备 Git 仓库

```bash
# 1. 初始化 Git（如果还没有）
git init

# 2. 添加所有文件
git add .

# 3. 提交
git commit -m "Ready for Zeabur deployment"

# 4. 创建 GitHub 仓库
# 访问 https://github.com/new 创建新仓库

# 5. 连接远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 6. 推送代码
git push -u origin main
```

## 第二步：在 Zeabur 部署

### 选项 A：通过网页界面（最简单）

1. 访问 https://dash.zeabur.com
2. 点击 **"New Project"**
3. 选择区域（推荐 Hong Kong）
4. 点击 **"Add Service"** → **"Git"**
5. 选择你的 GitHub 仓库
6. 等待构建完成（5-10分钟）
7. 获取部署 URL，访问你的应用！

### 选项 B：使用 Zeabur CLI

```bash
# 1. 安装 Zeabur CLI
npm install -g @zeabur/cli

# 2. 登录
zeabur auth login

# 3. 部署
zeabur deploy

# 4. 按照提示选择项目和服务
```

## 第三步：验证部署

访问你的应用 URL：
- `https://你的服务名.zeabur.app/health` - 检查健康状态
- `https://你的服务名.zeabur.app/` - 访问主页

## 🎯 重要提示

### ✅ 确保这些文件已提交到 Git：

```
✓ Dockerfile
✓ requirements.txt  
✓ app_working.py
✓ app/ (整个目录)
✓ artifacts/ (向量索引文件)
✓ data/
✓ templates/
✓ static/
```

### ⚠️ 常见问题

**问题：构建失败**
```bash
# 查看 Build Logs 找到错误
# 修复后重新推送
git add .
git commit -m "Fix build issue"
git push
```

**问题：artifacts/ 目录太大**
```bash
# 如果 Git 提示文件太大，使用 Git LFS
git lfs install
git lfs track "artifacts/*.npy"
git add .gitattributes
git commit -m "Use Git LFS for large files"
git push
```

**问题：应用启动失败**
- 检查 Runtime Logs
- 确认 artifacts/ 目录已上传
- 验证所有依赖都在 requirements.txt 中

## 📊 部署配置

Zeabur 会自动：
- ✅ 检测 Dockerfile
- ✅ 构建镜像
- ✅ 设置端口（8000）
- ✅ 分配域名
- ✅ 配置 SSL

你需要：
- ✅ 推送代码到 GitHub
- ✅ 在 Zeabur 连接仓库
- ✅ 等待部署完成

## 💡 优化建议

### 1. 加速构建

在 Dockerfile 中使用缓存：
```dockerfile
# 先复制依赖文件
COPY requirements.txt .
RUN pip install -r requirements.txt

# 再复制代码（代码改动不会重新安装依赖）
COPY . .
```

### 2. 减小镜像大小

```dockerfile
# 使用 slim 版本
FROM python:3.11-slim

# 清理缓存
RUN pip install --no-cache-dir -r requirements.txt
```

### 3. 健康检查

Zeabur 会自动检查你的应用：
- 访问根路径 `/`
- 检查 HTTP 200 响应

## 🔗 有用的链接

- Zeabur 文档: https://zeabur.com/docs
- Zeabur Dashboard: https://dash.zeabur.com
- GitHub: https://github.com

---

**就这么简单！** 🎉

你的大宗交易信息检索平台将在几分钟内上线！

