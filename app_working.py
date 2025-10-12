"""
大宗交易信息检索平台 - 工作版本
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from pathlib import Path

app = FastAPI(title="大宗线上交易信息检索平台")

# 静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 全局变量
vector_store = None

# Pydantic模型
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10
    use_llm: Optional[bool] = False

class Listing(BaseModel):
    id: str
    title: str
    category: Optional[str] = None
    region: Optional[str] = None
    price: Optional[float] = None
    unit: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    seller: Optional[str] = None
    date: Optional[str] = None

class SearchResult(BaseModel):
    score: float
    listing: Listing

class SearchResponse(BaseModel):
    results: List[SearchResult]
    summary: Optional[str] = None
    used_llm: bool = False

def load_vector_store():
    """加载向量存储"""
    global vector_store
    if vector_store is not None:
        return vector_store
    
    try:
        from app.retriever import VectorStore
        vector_store = VectorStore(
            "artifacts/embeddings.npy",
            "artifacts/metadata.jsonl",
            "artifacts/model_name.txt"
        )
        print("Vector store loaded successfully")
        return vector_store
    except Exception as e:
        print(f"Failed to load vector store: {e}")
        return None

def generate_simple_summary(results: List[Dict[str, Any]], query: str) -> str:
    """生成简单摘要"""
    if not results:
        return f"未找到与'{query}'相关的记录。"
    
    parts = []
    for r in results[:5]:
        l = r["listing"]
        title = l.get("title", "")
        region = l.get("region", "")
        price = l.get("price")
        unit = l.get("unit", "")
        if price is not None:
            parts.append(f"{title}（{region}，{price}{unit}）")
        else:
            parts.append(f"{title}（{region}）")
    
    return "；".join(parts)

@app.on_event("startup")
async def startup_event():
    """启动时加载向量存储"""
    load_vector_store()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health():
    """健康检查"""
    store = load_vector_store()
    status = "ok" if store is not None else "no-index"
    return {"status": status}

@app.post("/api/search", response_model=SearchResponse)
async def api_search(payload: SearchRequest):
    """搜索API"""
    store = load_vector_store()
    
    if store is None:
        return JSONResponse(
            status_code=400,
            content={
                "message": "索引不存在，请先运行: python scripts/build_index_st.py",
            },
        )
    
    try:
        # 执行搜索
        results_raw = store.search(payload.query, top_k=payload.top_k or 10)
        
        # 转换为响应格式
        results = []
        for r in results_raw:
            results.append(
                SearchResult(
                    score=r["score"],
                    listing=Listing(**r["listing"]),
                )
            )
        
        # 生成摘要
        summary = generate_simple_summary(results_raw, payload.query)
        
        return SearchResponse(
            results=results,
            summary=summary,
            used_llm=False
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"搜索失败: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8888))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)

