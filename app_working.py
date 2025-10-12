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
llm_instance = None

# Pydantic模型
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10
    use_llm: Optional[bool] = False

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

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

def load_llm():
    """加载LLM实例"""
    global llm_instance
    if llm_instance is not None:
        return llm_instance
    
    try:
        from app.llm import LLM
        import os
        api_key = os.getenv('ZHIPU_API_KEY')
        llm_instance = LLM(api_key=api_key)
        print("LLM instance loaded successfully")
        return llm_instance
    except Exception as e:
        print(f"Failed to load LLM: {e}")
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
    """启动时加载向量存储和LLM"""
    load_vector_store()
    load_llm()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/trends", response_class=HTMLResponse)
async def trends(request: Request):
    """实时趋势页面"""
    return templates.TemplateResponse("trends.html", {"request": request})

@app.get("/health")
async def health():
    """健康检查"""
    store = load_vector_store()
    status = "ok" if store is not None else "no-index"
    return {"status": status}

@app.get("/api/trends/data")
async def get_trends_data():
    """获取趋势数据"""
    import random
    from datetime import datetime, timedelta
    
    # 生成模拟的实时趋势数据
    now = datetime.now()
    
    # 生成过去24小时的数据点
    time_labels = []
    transaction_volumes = []
    price_trends = []
    
    for i in range(24, 0, -1):
        time = now - timedelta(hours=i)
        time_labels.append(time.strftime("%H:%M"))
        transaction_volumes.append(random.randint(50, 200))
        price_trends.append(round(random.uniform(95, 105), 2))
    
    # 热门类别
    categories = [
        {"name": "钢材", "count": random.randint(100, 500), "change": round(random.uniform(-10, 10), 1)},
        {"name": "煤炭", "count": random.randint(80, 400), "change": round(random.uniform(-10, 10), 1)},
        {"name": "有色金属", "count": random.randint(60, 300), "change": round(random.uniform(-10, 10), 1)},
        {"name": "化工产品", "count": random.randint(50, 250), "change": round(random.uniform(-10, 10), 1)},
        {"name": "农产品", "count": random.randint(40, 200), "change": round(random.uniform(-10, 10), 1)},
    ]
    
    # 热门地区
    regions = [
        {"name": "华东", "count": random.randint(200, 600), "percentage": round(random.uniform(20, 35), 1)},
        {"name": "华北", "count": random.randint(150, 500), "percentage": round(random.uniform(15, 30), 1)},
        {"name": "华南", "count": random.randint(100, 400), "percentage": round(random.uniform(10, 25), 1)},
        {"name": "西南", "count": random.randint(80, 300), "percentage": round(random.uniform(8, 20), 1)},
        {"name": "东北", "count": random.randint(60, 250), "percentage": round(random.uniform(5, 15), 1)},
    ]
    
    # 实时统计
    stats = {
        "total_transactions": random.randint(1000, 5000),
        "total_volume": round(random.uniform(10000, 50000), 2),
        "avg_price": round(random.uniform(5000, 15000), 2),
        "active_sellers": random.randint(100, 500),
    }
    
    return {
        "time_labels": time_labels,
        "transaction_volumes": transaction_volumes,
        "price_trends": price_trends,
        "categories": categories,
        "regions": regions,
        "stats": stats,
        "last_update": now.strftime("%Y-%m-%d %H:%M:%S")
    }

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
        if payload.use_llm:
            llm = load_llm()
            if llm:
                try:
                    summary = llm.generate_summary(payload.query, results_raw)
                    used_llm = True
                except Exception as e:
                    print(f"LLM summary failed: {e}")
                    summary = generate_simple_summary(results_raw, payload.query)
                    used_llm = False
            else:
                summary = generate_simple_summary(results_raw, payload.query)
                used_llm = False
        else:
            summary = generate_simple_summary(results_raw, payload.query)
            used_llm = False
        
        return SearchResponse(
            results=results,
            summary=summary,
            used_llm=used_llm
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"搜索失败: {str(e)}"}
        )

@app.post("/api/chat")
async def api_chat(payload: ChatRequest):
    """AI助手对话API"""
    llm = load_llm()
    
    if llm is None or llm.client is None:
        return JSONResponse(
            status_code=400,
            content={
                "message": "AI助手不可用，请检查ZHIPU_API_KEY环境变量配置",
                "reply": "AI助手暂时不可用，请检查API密钥配置。"
            }
        )
    
    try:
        reply = llm.chat(payload.message, payload.context)
        return {
            "message": payload.message,
            "reply": reply,
            "status": "success"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": f"AI对话失败: {str(e)}",
                "reply": f"抱歉，AI助手遇到了问题：{str(e)}"
            }
        )

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8888))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)

