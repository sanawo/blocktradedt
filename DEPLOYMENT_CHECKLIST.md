# ✅ Zeabur 部署检查清单

## 📋 部署前检查

### 1. 必需文件

- [ ] `Dockerfile` 存在
- [ ] `requirements.txt` 存在且包含所有依赖
- [ ] `app_working.py` 存在
- [ ] `app/` 目录完整
- [ ] `artifacts/embeddings.npy` 存在（约 15KB）
- [ ] `artifacts/metadata.jsonl` 存在
- [ ] `artifacts/model_name.txt` 存在
- [ ] `data/sample_listings.jsonl` 存在
- [ ] `templates/index.html` 存在
- [ ] `static/styles.css` 存在

### 2. Git 仓库

- [ ] Git 已初始化 (`git init`)
- [ ] 所有文件已添加 (`git add .`)
- [ ] 已提交 (`git commit -m "..."`)
- [ ] 已连接远程仓库 (`git remote add origin ...`)
- [ ] 已推送到 GitHub (`git push`)

### 3. 配置检查

- [ ] Dockerfile 端口设置为 8000
- [ ] app_working.py 支持 PORT 环境变量
- [ ] requirements.txt 包含 sentence-transformers
- [ ] .dockerignore 已创建

---

## 🚀 部署步骤

### 步骤 1：推送代码

```bash
git add .
git commit -m "Ready for Zeabur deployment"
git push origin main
```

- [ ] 代码已成功推送到 GitHub

### 步骤 2：创建 Zeabur 项目

1. 访问 https://dash.zeabur.com
2. 点击 "New Project"
3. 选择区域（Hong Kong 或 Singapore）
4. 命名项目

- [ ] Zeabur 项目已创建

### 步骤 3：添加服务

1. 点击 "Add Service"
2. 选择 "Git"
3. 授权 GitHub
4. 选择仓库
5. 选择分支（main）

- [ ] 服务已添加
- [ ] 构建已开始

### 步骤 4：等待构建

预计时间：5-10 分钟

- [ ] Build Logs 显示 "Building..."
- [ ] 依赖安装成功
- [ ] Docker 镜像构建成功
- [ ] 镜像推送成功

### 步骤 5：验证部署

- [ ] 服务状态显示 "Running"
- [ ] 获得部署 URL
- [ ] 访问 `https://你的服务名.zeabur.app/health` 返回 200
- [ ] 访问首页可以正常加载
- [ ] 搜索功能正常工作

---

## 🔍 故障排查检查

### 如果构建失败：

- [ ] 查看 Build Logs 的错误信息
- [ ] 检查 requirements.txt 是否正确
- [ ] 验证 Dockerfile 语法
- [ ] 确认 Python 版本兼容（3.11）
- [ ] 本地测试 `docker build -t test .`

### 如果应用无法启动：

- [ ] 查看 Runtime Logs
- [ ] 确认 artifacts/ 目录已上传
- [ ] 检查端口配置（应为 8000）
- [ ] 验证环境变量设置
- [ ] 确认向量索引文件完整

### 如果搜索不工作：

- [ ] 检查 Runtime Logs 中的错误
- [ ] 确认 "Vector store loaded successfully" 消息
- [ ] 验证 artifacts/ 文件大小正确
- [ ] 测试 API 端点：`/api/search`

---

## 📊 文件大小参考

正常情况下：

```
artifacts/embeddings.npy      ~15 KB  (12 listings × 384 dim)
artifacts/metadata.jsonl      ~2 KB
artifacts/model_name.txt      ~60 B
data/sample_listings.jsonl    ~2 KB
```

如果文件大小差异很大，可能需要重新构建索引：

```bash
python scripts/build_index_st.py
```

---

## 🎯 部署成功标志

✅ **所有以下条件都满足：**

1. Zeabur Dashboard 显示服务 "Running"
2. Build Logs 无错误
3. Runtime Logs 显示 "Uvicorn running on..."
4. Runtime Logs 显示 "Vector store loaded successfully"
5. 健康检查端点返回 `{"status":"ok"}`
6. 首页可以访问
7. 搜索功能返回结果

---

## 📝 部署后任务

- [ ] 记录部署 URL
- [ ] 测试所有功能
- [ ] 配置自定义域名（可选）
- [ ] 设置环境变量（如需要）
- [ ] 配置监控和告警（可选）
- [ ] 文档更新

---

## 🔗 快速命令

```bash
# 查看 Git 状态
git status

# 查看远程仓库
git remote -v

# 重新推送
git push -f origin main

# 本地测试 Docker
docker build -t test .
docker run -p 8000:8000 test

# 重建索引
python scripts/build_index_st.py
```

---

## 📞 获取帮助

如果遇到问题：

1. **查看日志**：Build Logs 和 Runtime Logs
2. **搜索文档**：https://zeabur.com/docs
3. **社区支持**：Zeabur Discord
4. **GitHub Issues**：在仓库创建 issue

---

**祝部署顺利！** 🎉

使用这个检查清单确保每一步都正确完成。

