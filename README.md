## 大宗线上交易信息检索平台（原型）

基于 FastAPI + 本地向量检索（FastEmbed）+ 可选 LLM 总结（OpenAI 兼容）的可运行原型。

- 后端: FastAPI
- 向量: FastEmbed (`BAAI/bge-small-zh-v1.5`，支持中英文)
- 前端: Jinja2 模板 + 少量样式
- 数据: `data/sample_listings.jsonl`（示例）
- 索引: `scripts/build_index.py` 生成 `artifacts/` 下的向量与元数据

### 快速开始（Windows PowerShell）

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
python scripts/build_index.py
uvicorn app.main:app --reload --port 8000
```

访问: `http://127.0.0.1:8000`

### 可选：配置 LLM 总结

- 在根目录创建 `.env`，内容示例：

```
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

未配置时，系统会返回简要的抽取式摘要。

### 目录结构

```
app/
  main.py
  retriever.py
  llm.py
  config.py
  schemas.py
  __init__.py
scripts/
  build_index.py
artifacts/           # 索引输出，会在构建时生成
  embeddings.npy
  metadata.jsonl
  model_name.txt
data/
  sample_listings.jsonl
templates/
  index.html
static/
  styles.css
requirements.txt
README.md
```

### 说明
- 原型以简洁、可运行为目标，向量检索基于余弦相似度的稠密向量检索，适合中小规模数据。
- 后续可替换为更高性能的近似检索（HNSW、FAISS）与更完善的数据管线。



