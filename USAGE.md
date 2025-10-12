# Block Trade Information Retrieval Platform - Usage Guide

## ✅ System Status

Your platform is **RUNNING SUCCESSFULLY**! 🎉

- **Server URL**: http://127.0.0.1:8001
- **Status**: ✅ Online
- **Vector Store**: ✅ Loaded (12 listings, 384-dim embeddings)
- **Search Engine**: ✅ Working (Sentence Transformers)

## 🚀 Quick Start

### 1. Start the Server

```bash
python run.py
```

The server will automatically find an available port and start.

### 2. Access the Web Interface

Open your browser and go to:
```
http://127.0.0.1:8001
```

### 3. Search Examples

Try searching for:
- "copper" (铜锭)
- "steel" (钢材)
- "coal" (煤炭)
- "cement" (水泥)
- "chemical" (化工)

## 📡 API Usage

### Health Check
```bash
GET http://127.0.0.1:8001/health
```

### Search API
```bash
POST http://127.0.0.1:8001/api/search
Content-Type: application/json

{
  "query": "copper",
  "top_k": 10,
  "use_llm": false
}
```

### Example with curl:
```bash
curl -X POST http://127.0.0.1:8001/api/search \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"steel\",\"top_k\":5}"
```

### Example with Python:
```python
import requests

response = requests.post(
    "http://127.0.0.1:8001/api/search",
    json={"query": "copper", "top_k": 5}
)

results = response.json()
print(f"Found {len(results['results'])} results")
for result in results['results']:
    print(f"- {result['listing']['title']} (score: {result['score']:.4f})")
```

## 📊 Sample Data

The system includes 12 sample trade listings:
- Copper ingots (山东)
- Steel rebar (江苏)
- Coal (内蒙古)
- Coke (河北)
- ABS resin (广东)
- Aluminum ingots (上海)
- Cement (湖北)
- Methanol (四川)
- Corn (河南)
- Cold-rolled steel (天津)
- PTA (浙江)
- Stainless steel (福建)

## 🔧 Technical Details

- **Framework**: FastAPI
- **Embedding Model**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **Vector Dimension**: 384
- **Search Method**: Cosine similarity
- **Language Support**: Chinese & English

## 🛠️ Troubleshooting

### Server won't start?
```bash
# Stop all Python processes
taskkill /F /IM python.exe

# Restart
python run.py
```

### Port already in use?
The script automatically finds an available port between 8000-9000.

### Vector store not loaded?
```bash
# Rebuild the index
python scripts/build_index_st.py
```

## 📝 Files

- `run.py` - Simple server launcher
- `app_working.py` - Main application
- `artifacts/` - Vector index files
- `data/sample_listings.jsonl` - Sample data
- `templates/index.html` - Web interface
- `static/styles.css` - Styling

## 🎯 Next Steps

1. **Add more data**: Edit `data/sample_listings.jsonl`
2. **Rebuild index**: Run `python scripts/build_index_st.py`
3. **Restart server**: Run `python run.py`

## ✨ Features

- ✅ Semantic search (understands meaning, not just keywords)
- ✅ Multi-language support (Chinese & English)
- ✅ Fast vector similarity search
- ✅ Auto-generated summaries
- ✅ Clean web interface
- ✅ RESTful API

---

**Enjoy your Block Trade Information Retrieval Platform!** 🚀

