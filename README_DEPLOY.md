# Block Trade Information Retrieval Platform

大宗交易信息检索平台 - 基于语义搜索的智能检索系统

## 🚀 快速部署到 Zeabur

### 3步部署：

```bash
# 1. 推送到 GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main

# 2. 访问 Zeabur
# https://dash.zeabur.com

# 3. 连接 GitHub 仓库并部署
# 选择 "Add Service" → "Git" → 选择你的仓库
```

**就这么简单！** 5-10分钟后你的应用就上线了。

详细步骤请查看：[deploy_to_zeabur.md](deploy_to_zeabur.md)

---

## 📦 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 构建向量索引
python scripts/build_index_st.py

# 启动服务器
python run.py
```

访问：http://127.0.0.1:8001

---

## 🏗️ 项目结构

```
.
├── Dockerfile              # Docker 配置
├── requirements.txt        # Python 依赖
├── app_working.py         # 主应用
├── app/                   # 应用模块
│   ├── retriever.py       # 检索引擎
│   └── ...
├── artifacts/             # 向量索引（必需）
│   ├── embeddings.npy
│   ├── metadata.jsonl
│   └── model_name.txt
├── data/                  # 数据文件
├── templates/             # HTML 模板
└── static/               # 静态文件
```

---

## ✨ 功能特性

- ✅ 语义搜索（理解查询含义）
- ✅ 多语言支持（中文/英文）
- ✅ 向量相似度检索
- ✅ 自动摘要生成
- ✅ RESTful API
- ✅ 现代化 Web 界面

---

## 🔧 技术栈

- **框架**: FastAPI + Uvicorn
- **嵌入模型**: Sentence Transformers
- **向量维度**: 384
- **搜索方法**: 余弦相似度

---

## 📝 API 文档

### 健康检查
```bash
GET /health
```

### 搜索
```bash
POST /api/search
Content-Type: application/json

{
  "query": "copper",
  "top_k": 10
}
```

---

## 🌐 部署平台

- ✅ Zeabur（推荐）
- ✅ Railway
- ✅ Render
- ✅ Fly.io
- ✅ 任何支持 Docker 的平台

---

## 📚 文档

- [Zeabur 部署指南](ZEABUR_DEPLOYMENT.md) - 详细部署文档
- [快速部署](deploy_to_zeabur.md) - 3步快速部署
- [使用指南](USAGE.md) - 本地使用说明

---

## 🆘 故障排查

### 部署失败？

1. 检查 **Build Logs** 查看构建错误
2. 确认所有文件已推送到 Git
3. 验证 `artifacts/` 目录存在

### 应用无法启动？

1. 检查 **Runtime Logs**
2. 确认向量索引文件存在
3. 验证依赖安装成功

详细排查请看：[ZEABUR_DEPLOYMENT.md](ZEABUR_DEPLOYMENT.md)

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**立即部署到 Zeabur！** 🚀

