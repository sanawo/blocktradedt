"""
大宗交易信息检索平台 - 工作版本
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
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
    system_prompt: Optional[str] = None

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

@app.get("/")
async def index():
    """首页 - 重定向到新版"""
    return RedirectResponse(url="/v2", status_code=302)

@app.get("/v1", response_class=HTMLResponse)
async def index_v1(request: Request):
    """原版首页（保留访问）"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/trends", response_class=HTMLResponse)
async def trends(request: Request):
    """实时趋势页面（深色模式）"""
    return templates.TemplateResponse("trends_dark.html", {"request": request})

@app.get("/v2", response_class=HTMLResponse)
async def index_v2(request: Request):
    """新版首页"""
    return templates.TemplateResponse("index_v2.html", {"request": request})

@app.get("/news", response_class=HTMLResponse)
async def news_page(request: Request):
    """实时新闻页面"""
    return templates.TemplateResponse("news.html", {"request": request})

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
                "response": "AI助手暂时不可用，请检查API密钥配置。"
            }
        )
    
    try:
        reply = llm.chat(payload.message, payload.context, payload.system_prompt)
        return {
            "message": payload.message,
            "response": reply,
            "status": "success"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": f"AI对话失败: {str(e)}",
                "response": f"抱歉，AI助手遇到了问题：{str(e)}"
            }
        )

@app.get("/api/news")
async def api_news(page: int = 1, category: str = "all", limit: int = 20):
    """获取新闻列表API"""
    import random
    from datetime import datetime, timedelta
    
    # 生成模拟新闻数据
    categories_map = {
        "market": "市场动态",
        "policy": "政策法规",
        "analysis": "行业分析",
        "company": "公司新闻",
        "international": "国际资讯"
    }
    
    news_titles = [
        "钢材价格持续上涨，市场供需关系紧张",
        "国家发改委发布大宗商品价格调控新政策",
        "2024年大宗交易市场分析报告出炉",
        "A股市场大宗交易活跃度创新高",
        "有色金属板块领涨，铜价突破历史新高",
        "煤炭供应紧张，冬季保供压力加大",
        "原油期货价格波动加剧，市场观望情绪浓厚",
        "化工产品市场调整，部分品种价格回落",
        "大宗商品ETF受到投资者青睐",
        "国际市场动荡，国内大宗商品避险需求上升"
    ]
    
    news_summaries = [
        "受供应链紧张和需求增长双重影响，近期钢材价格持续上涨，市场预期后续仍有上涨空间。",
        "国家发改委出台新政策，加强大宗商品价格监管，维护市场秩序，保障民生需求。",
        "权威机构发布年度大宗交易市场分析报告，详细解读市场趋势和投资机会。",
        "A股市场大宗交易活跃度创历史新高，显示出机构投资者对市场的信心增强。",
        "有色金属板块表现强劲，铜价突破历史新高，专家建议关注相关投资机会。",
        "随着冬季来临，煤炭供应紧张情况加剧，各地加强保供稳价措施。",
        "国际原油价格波动加剧，市场观望情绪浓厚，投资者需谨慎应对。",
        "化工产品市场出现调整，部分品种价格回落，行业洗牌加速。",
        "大宗商品ETF成为投资者新宠，资金流入持续增加。",
        "国际市场动荡不安，国内大宗商品避险需求上升，黄金等避险资产受追捧。"
    ]
    
    sources = ["财经网", "新浪财经", "财新网", "证券时报", "第一财经", "财联社"]
    tags_pool = ["钢材", "煤炭", "有色金属", "原油", "化工", "政策", "分析", "市场"]
    
    news_list = []
    start_index = (page - 1) * limit
    
    for i in range(start_index, start_index + limit):
        idx = i % len(news_titles)
        time_delta = random.randint(i * 30, i * 60)
        news_time = datetime.now() - timedelta(minutes=time_delta)
        
        cat = random.choice(list(categories_map.keys())) if category == "all" else category
        
        news_item = {
            "id": f"news_{i + 1}",
            "title": news_titles[idx],
            "summary": news_summaries[idx],
            "source": random.choice(sources),
            "time": news_time.strftime("%Y-%m-%d %H:%M"),
            "category": cat,
            "category_name": categories_map.get(cat, "未分类"),
            "views": random.randint(100, 10000),
            "tags": random.sample(tags_pool, k=random.randint(2, 4)),
            "url": f"https://example.com/news/{i + 1}",
            "image": f"https://images.unsplash.com/photo-{1611974789855 + i}?w=400&q=80"
        }
        news_list.append(news_item)
    
    return {
        "news": news_list,
        "page": page,
        "limit": limit,
        "total": 100,
        "has_more": page * limit < 100
    }

@app.get("/api/news/latest")
async def api_news_latest(limit: int = 6):
    """获取最新新闻API"""
    import random
    from datetime import datetime, timedelta
    
    news_titles = [
        "钢材价格持续上涨，市场供需关系紧张",
        "国家发改委发布大宗商品价格调控新政策",
        "2024年大宗交易市场分析报告出炉",
        "A股市场大宗交易活跃度创新高",
        "有色金属板块领涨，铜价突破历史新高",
        "煤炭供应紧张，冬季保供压力加大"
    ]
    
    news_summaries = [
        "受供应链紧张和需求增长双重影响，近期钢材价格持续上涨...",
        "国家发改委出台新政策，加强大宗商品价格监管，维护市场秩序...",
        "权威机构发布年度大宗交易市场分析报告，详细解读市场趋势...",
        "A股市场大宗交易活跃度创历史新高，显示出机构投资者信心...",
        "有色金属板块表现强劲，铜价突破历史新高，专家建议关注...",
        "随着冬季来临，煤炭供应紧张情况加剧，各地加强保供措施..."
    ]
    
    sources = ["财经网", "新浪财经", "财新网", "证券时报", "第一财经", "财联社"]
    
    news_list = []
    for i in range(min(limit, len(news_titles))):
        time_delta = random.randint(i * 10, i * 30)
        news_time = datetime.now() - timedelta(minutes=time_delta)
        
        news_item = {
            "id": f"latest_{i + 1}",
            "title": news_titles[i],
            "summary": news_summaries[i],
            "source": random.choice(sources),
            "time": news_time.strftime("%Y-%m-%d %H:%M"),
            "image": f"https://images.unsplash.com/photo-{1611974789855 + i * 1000}?w=400&q=80"
        }
        news_list.append(news_item)
    
    return news_list

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8888))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)

