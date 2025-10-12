# Zeabur 部署指南

## 📋 前提条件

1. 注册 [Zeabur](https://zeabur.com) 账号
2. 将代码推送到 GitHub 仓库
3. 确保以下文件在仓库中：
   - `Dockerfile`
   - `requirements.txt`
   - `app_working.py`
   - `app/` 目录
   - `artifacts/` 目录（包含向量索引）
   - `data/` 目录
   - `templates/` 目录
   - `static/` 目录

## 🚀 部署步骤

### 方法1：通过 GitHub 自动部署（推荐）

#### 步骤 1：准备 GitHub 仓库

```bash
# 初始化 git（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit for Zeabur deployment"

# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 推送到 GitHub
git push -u origin main
```

#### 步骤 2：在 Zeabur 创建项目

1. 登录 [Zeabur Dashboard](https://dash.zeabur.com)
2. 点击 **"New Project"**
3. 选择一个区域（推荐：Hong Kong 或 Singapore）
4. 给项目命名（例如：block-trade-platform）

#### 步骤 3：添加服务

1. 在项目中点击 **"Add Service"**
2. 选择 **"Git"**
3. 授权并选择你的 GitHub 仓库
4. 选择分支（通常是 `main` 或 `master`）

#### 步骤 4：配置服务

Zeabur 会自动检测到 `Dockerfile` 并开始构建。

**重要配置：**

1. **端口设置**：
   - Zeabur 会自动设置 `PORT` 环境变量
   - 我们的 Dockerfile 已配置为使用端口 8000
   - 无需手动配置

2. **环境变量**（可选）：
   - 在服务设置中添加环境变量
   - 例如：`OPENAI_API_KEY`（如果需要 LLM 功能）

#### 步骤 5：等待部署

- 构建过程大约需要 5-10 分钟
- 可以在 **"Build Logs"** 查看构建进度
- 构建成功后，会自动部署

#### 步骤 6：访问应用

1. 部署成功后，Zeabur 会提供一个 URL
2. 格式类似：`https://你的服务名.zeabur.app`
3. 点击 URL 即可访问你的应用！

---

### 方法2：使用 Docker 镜像部署

如果你想先在本地构建镜像：

```bash
# 构建镜像（指定平台为 linux/amd64）
docker buildx build --platform linux/amd64 -t block-trade-platform:latest .

# 测试镜像
docker run -p 8000:8000 block-trade-platform:latest

# 推送到 Docker Hub 或其他镜像仓库
docker tag block-trade-platform:latest 你的用户名/block-trade-platform:latest
docker push 你的用户名/block-trade-platform:latest
```

然后在 Zeabur 中：
1. 选择 **"Prebuilt Image"**
2. 输入镜像地址
3. 部署

---

## 🔧 故障排查

### 问题1：构建失败

**检查 Build Logs：**
- 查看是否有依赖安装失败
- 确认 Python 版本兼容性
- 检查 requirements.txt 是否正确

**解决方案：**
```bash
# 本地测试构建
docker build -t test-build .

# 如果失败，修复后重新推送
git add .
git commit -m "Fix build issues"
git push
```

### 问题2：应用无法启动

**检查 Runtime Logs：**
- 查看应用启动日志
- 确认端口配置正确
- 检查文件路径是否正确

**常见原因：**
- `artifacts/` 目录缺失 → 确保推送到 Git
- 端口配置错误 → 检查 Dockerfile 中的 PORT
- 依赖缺失 → 更新 requirements.txt

### 问题3：向量索引加载失败

**确保以下文件存在：**
```
artifacts/
  ├── embeddings.npy
  ├── metadata.jsonl
  └── model_name.txt
```

**如果缺失：**
```bash
# 本地重新构建索引
python scripts/build_index_st.py

# 提交并推送
git add artifacts/
git commit -m "Add vector index files"
git push
```

### 问题4：镜像拉取失败 (ErrImagePull)

**原因：**
- 镜像不存在
- 权限问题（私有镜像）
- 网络问题

**解决方案：**
1. 确认镜像地址正确
2. 如果是私有镜像，在 Zeabur 中配置 Registry 凭证
3. 使用 GitHub 自动构建（推荐）

---

## 📊 性能优化

### 1. 减小镜像大小

在 Dockerfile 中：
```dockerfile
# 使用多阶段构建
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "-m", "uvicorn", "app_working:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 启用持久化存储

如果需要保存用户数据：
1. 在 Zeabur 中添加 **Volume**
2. 挂载到 `/app/data` 或其他目录

### 3. 配置自动扩展

在 Zeabur 服务设置中：
- 设置最小/最大实例数
- 配置 CPU/内存限制

---

## 🌐 自定义域名

1. 在 Zeabur 服务设置中点击 **"Domains"**
2. 添加自定义域名
3. 按照提示配置 DNS 记录
4. 等待 SSL 证书自动配置

---

## 💰 成本估算

Zeabur 定价（截至2024）：
- **免费套餐**：有限资源，适合测试
- **Developer**：$5/月起
- **Team**：$20/月起

**建议：**
- 开发/测试：使用免费套餐
- 生产环境：至少 Developer 套餐

---

## 📝 部署检查清单

部署前确认：

- [ ] 代码已推送到 GitHub
- [ ] `Dockerfile` 存在且正确
- [ ] `requirements.txt` 包含所有依赖
- [ ] `artifacts/` 目录包含向量索引
- [ ] `templates/` 和 `static/` 目录存在
- [ ] 端口配置正确（8000）
- [ ] 环境变量已设置（如需要）

部署后验证：

- [ ] 访问 `/health` 端点返回 200
- [ ] 首页可以正常加载
- [ ] 搜索功能正常工作
- [ ] 向量索引加载成功

---

## 🆘 获取帮助

- **Zeabur 文档**：https://zeabur.com/docs
- **Zeabur Discord**：https://discord.gg/zeabur
- **GitHub Issues**：在你的仓库创建 issue

---

## ✅ 快速命令参考

```bash
# 1. 准备代码
git add .
git commit -m "Ready for Zeabur deployment"
git push

# 2. 本地测试 Docker
docker build -t test .
docker run -p 8000:8000 test

# 3. 重建索引（如需要）
python scripts/build_index_st.py

# 4. 查看日志
# 在 Zeabur Dashboard 中查看 Build Logs 和 Runtime Logs
```

---

**祝部署顺利！** 🚀

如有问题，请查看 Build Logs 和 Runtime Logs 获取详细错误信息。

