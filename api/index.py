from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Base, User, SearchHistory
from app.schemas import UserCreate, UserLogin, SearchRequest, ChatRequest, ChatResponse
from app.retriever import Retriever
from app.llm import LLM
from app.zhipu_ai import ZhipuAI
from app.config import Config
import jwt
from datetime import datetime, timedelta
from typing import Optional

# 数据库配置 - 使用内存数据库适配Vercel
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./block_trade_dt.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 初始化智谱AI（延迟初始化以避免启动时错误）
zhipu_ai = None

def get_zhipu_ai():
    global zhipu_ai
    if zhipu_ai is None:
        try:
            zhipu_ai = ZhipuAI(api_key=Config.get_zhipu_api_key())
        except Exception as e:
            print(f"智谱AI初始化失败: {e}")
            zhipu_ai = None
    return zhipu_ai

app = FastAPI(title="Block Trade DT", description="大宗交易数据检索平台")

# 静态文件和模板
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # 检查目录是否存在
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("✅ 静态文件目录已挂载")
    else:
        logger.warning("⚠️  静态文件目录不存在")
    
    if os.path.exists("templates"):
        templates = Jinja2Templates(directory="templates")
        logger.info("✅ 模板目录已加载")
    else:
        logger.warning("⚠️  模板目录不存在")
        templates = None
except Exception as e:
    logger.error(f"❌ 初始化静态文件或模板失败: {e}")
    templates = None

# 安全配置
security = HTTPBearer()

# 初始化检索器和LLM（延迟初始化以避免启动时错误）
retriever = None
llm = None

def get_retriever():
    global retriever
    if retriever is None:
        try:
            retriever = Retriever()
        except Exception as e:
            print(f"Retriever初始化失败: {e}")
            retriever = None
    return retriever

def get_llm():
    global llm
    if llm is None:
        try:
            llm = LLM()
        except Exception as e:
            print(f"LLM初始化失败: {e}")
            llm = None
    return llm

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, Config.get_jwt_secret_key(), algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)), db: Session = Depends(get_db)):
    """获取当前用户（可选），如果未提供token则返回None"""
    if credentials is None:
        return None
    try:
        payload = jwt.decode(credentials.credentials, Config.get_jwt_secret_key(), algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            return None
    except jwt.PyJWTError:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Block Trade DT"}

# 主页路由
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    if templates is None:
        return HTMLResponse("<h1>Block Trade DT API</h1><p>模板系统未加载，请使用 API 端点</p>")
    return templates.TemplateResponse("index_v2.html", {"request": request})

# 趋势页面（深色模式）
@app.get("/trends", response_class=HTMLResponse)
async def trends_page(request: Request):
    if templates is None:
        return HTMLResponse("<h1>Trends</h1><p>模板系统未加载</p>")
    return templates.TemplateResponse("trends_dark.html", {"request": request})

# 新闻页面
@app.get("/news", response_class=HTMLResponse)
async def news_page(request: Request):
    if templates is None:
        return HTMLResponse("<h1>News</h1><p>模板系统未加载</p>")
    return templates.TemplateResponse("news.html", {"request": request})

# API路由
@app.post("/api/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 检查用户是否已存在
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # 创建新用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name
    )
    user.set_password(user_data.password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "User registered successfully", "user_id": user.id}

@app.post("/api/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not user.check_password(user_data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # 生成JWT token
    access_token_expires = timedelta(hours=24)
    access_token = jwt.encode(
        {"sub": user.username, "exp": datetime.utcnow() + access_token_expires},
        Config.get_jwt_secret_key(),
        algorithm="HS256"
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": {"username": user.username, "email": user.email}}

@app.get("/api/user/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email, "full_name": current_user.full_name}

@app.post("/api/search")
async def search(request: SearchRequest, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user_optional)):
    try:
        # 获取检索器和LLM
        retriever_instance = get_retriever()
        llm_instance = get_llm()
        
        if retriever_instance is None:
            raise HTTPException(status_code=503, detail="检索服务暂时不可用，请稍后重试")
        
        # 执行搜索
        results = retriever_instance.search(request.query)
        
        # 生成摘要
        summary = ""
        if llm_instance:
            try:
                summary = llm_instance.generate_summary(request.query, results)
            except Exception as e:
                print(f"生成摘要失败: {e}")
                summary = f"找到 {len(results)} 条相关结果"
        else:
            summary = f"找到 {len(results)} 条相关结果"
        
        # 记录搜索历史（如果用户已登录）
        if current_user:
            search_history = SearchHistory(
                user_id=current_user.id,
                query=request.query,
                results_count=len(results)
            )
            db.add(search_history)
            db.commit()
        
        return {
            "query": request.query,
            "results": results,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/latest")
async def api_news_latest(limit: int = 6):
    """获取最新新闻API（用于首页展示）"""
    import random
    from datetime import timedelta
    
    news_titles = [
        "A股市场大宗交易活跃度创历史新高",
        "钢材价格持续上涨，市场供需关系紧张",
        "有色金属板块领涨，铜价突破历史新高",
        "国家发改委发布大宗商品价格调控新政策",
        "2024年大宗交易市场分析报告出炉",
        "证监会优化大宗交易制度，提升市场效率"
    ]
    
    news_summaries = [
        "近期A股市场大宗交易活跃度显著提升，单日成交额突破100亿元大关...",
        "受供应链紧张和需求增长双重影响，近期钢材价格持续上涨...",
        "有色金属板块表现强劲，铜价突破历史新高，专家建议关注...",
        "国家发改委出台新政策，加强大宗商品价格监管，维护市场秩序...",
        "权威机构发布年度大宗交易市场分析报告，详细解读市场趋势...",
        "证监会发布通知，进一步优化大宗交易制度，简化交易流程..."
    ]
    
    news_urls = [
        "https://finance.sina.com.cn/stock/marketresearch/",
        "https://www.eastmoney.com/",
        "https://finance.qq.com/",
        "https://www.ndrc.gov.cn/",
        "https://www.caixin.com/",
        "https://www.csrc.gov.cn/"
    ]
    
    sources = ["新浪财经", "东方财富网", "腾讯财经", "国家发改委", "财新网", "证监会"]
    
    news_list = []
    for i in range(min(limit, len(news_titles))):
        time_delta = random.randint(i * 10, i * 30)
        news_time = datetime.now() - timedelta(minutes=time_delta)
        
        news_item = {
            "id": f"latest_{i + 1}",
            "title": news_titles[i],
            "summary": news_summaries[i],
            "source": sources[i],
            "time": news_time.strftime("%Y-%m-%d %H:%M"),
            "url": news_urls[i]
        }
        news_list.append(news_item)
    
    return news_list

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(chat_request: ChatRequest):
    try:
        ai_client = get_zhipu_ai()
        if ai_client is None:
            return ChatResponse(
                response="抱歉，AI服务暂时不可用",
                timestamp=datetime.now().isoformat(),
                success=False
            )
        
        response = ai_client.chat(
            user_message=chat_request.message,
            system_prompt=chat_request.system_prompt,
            conversation_history=chat_request.conversation_history
        )
        return ChatResponse(response=response, timestamp=datetime.now().isoformat(), success=True)
    except Exception as e:
        return ChatResponse(response=f"抱歉，AI服务暂时不可用: {str(e)}", timestamp=datetime.now().isoformat(), success=False)

@app.get("/api/trends/data")
async def get_trends_data():
    # 模拟实时市场数据
    import random
    from datetime import timedelta
    
    # 生成24小时时间标签
    time_labels = []
    current_time = datetime.now()
    for i in range(24):
        time = current_time - timedelta(hours=23-i)
        time_labels.append(time.strftime("%H:%M"))
    
    # 生成模拟的统计数据
    stats = {
        "total_volume": round(random.uniform(50, 100), 2),
        "total_transactions": random.randint(100, 500),
        "avg_price": round(random.uniform(-2, 2), 2),
        "active_sellers": random.randint(50, 150)
    }
    
    # 生成交易量和价格趋势数据
    transaction_volumes = [random.randint(50, 200) for _ in range(24)]
    price_trends = [round(3600 + random.uniform(-50, 50), 2) for _ in range(24)]
    
    # 生成类别排行
    categories = [
        {"name": "钢材", "count": random.randint(100, 300), "change": round(random.uniform(-10, 20), 1)},
        {"name": "有色金属", "count": random.randint(80, 250), "change": round(random.uniform(-10, 20), 1)},
        {"name": "能源化工", "count": random.randint(60, 200), "change": round(random.uniform(-10, 20), 1)},
        {"name": "农产品", "count": random.randint(40, 150), "change": round(random.uniform(-10, 20), 1)},
        {"name": "建材", "count": random.randint(30, 120), "change": round(random.uniform(-10, 20), 1)}
    ]
    
    # 生成地区排行
    regions = [
        {"name": "华东", "count": random.randint(200, 400), "percentage": round(random.uniform(25, 35), 1), "change": round(random.uniform(-5, 15), 1)},
        {"name": "华北", "count": random.randint(150, 350), "percentage": round(random.uniform(20, 30), 1), "change": round(random.uniform(-5, 15), 1)},
        {"name": "华南", "count": random.randint(100, 300), "percentage": round(random.uniform(15, 25), 1), "change": round(random.uniform(-5, 15), 1)},
        {"name": "西南", "count": random.randint(80, 200), "percentage": round(random.uniform(10, 20), 1), "change": round(random.uniform(-5, 15), 1)},
        {"name": "东北", "count": random.randint(50, 150), "percentage": round(random.uniform(5, 15), 1), "change": round(random.uniform(-5, 15), 1)}
    ]
    
    return {
        "stats": stats,
        "time_labels": time_labels,
        "transaction_volumes": transaction_volumes,
        "price_trends": price_trends,
        "categories": categories,
        "regions": regions,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/news")
async def api_news(page: int = 1, category: str = "all", limit: int = 20):
    """获取新闻列表API"""
    import random
    from datetime import timedelta
    
    # 新闻数据源配置
    news_sources = {
        "market": [
            {
                "title": "A股市场大宗交易活跃度创历史新高",
                "summary": "近期A股市场大宗交易活跃度显著提升，单日成交额突破100亿元大关，显示出机构投资者对市场前景的信心增强。",
                "url": "https://finance.sina.com.cn/stock/marketresearch/",
                "source": "新浪财经"
            },
            {
                "title": "钢材价格持续上涨，市场供需关系紧张",
                "summary": "受供应链紧张和需求增长双重影响，近期钢材价格持续上涨，市场预期后续仍有上涨空间。",
                "url": "https://www.eastmoney.com/",
                "source": "东方财富网"
            },
            {
                "title": "有色金属板块领涨，铜价突破历史新高",
                "summary": "有色金属板块表现强劲，铜价突破历史新高，专家建议关注相关投资机会。",
                "url": "https://finance.qq.com/",
                "source": "腾讯财经"
            }
        ],
        "policy": [
            {
                "title": "国家发改委发布大宗商品价格调控新政策",
                "summary": "国家发改委出台新政策，加强大宗商品价格监管，维护市场秩序，促进经济稳定发展。",
                "url": "https://www.ndrc.gov.cn/",
                "source": "国家发改委"
            },
            {
                "title": "证监会优化大宗交易制度，提升市场效率",
                "summary": "证监会发布通知，进一步优化大宗交易制度，简化交易流程，提升市场效率。",
                "url": "https://www.csrc.gov.cn/",
                "source": "证监会"
            }
        ],
        "analysis": [
            {
                "title": "2024年大宗交易市场分析报告出炉",
                "summary": "权威机构发布年度大宗交易市场分析报告，详细解读市场趋势，为投资者提供参考。",
                "url": "https://www.caixin.com/",
                "source": "财新网"
            },
            {
                "title": "机构：下半年大宗商品市场将迎来结构性机会",
                "summary": "多家研究机构预测，下半年大宗商品市场将呈现结构性分化，能源和有色金属板块值得关注。",
                "url": "https://www.yicai.com/",
                "source": "第一财经"
            }
        ],
        "company": [
            {
                "title": "某龙头企业大宗交易频现，机构资金持续流入",
                "summary": "近期某龙头企业频繁出现大宗交易，机构资金持续流入，市场关注度提升。",
                "url": "https://www.21jingji.com/",
                "source": "21世纪经济报道"
            }
        ],
        "international": [
            {
                "title": "国际市场动荡，国内大宗商品避险需求上升",
                "summary": "受国际市场不确定性影响，国内投资者避险情绪升温，大宗商品市场受到青睐。",
                "url": "https://wallstreetcn.com/",
                "source": "华尔街见闻"
            },
            {
                "title": "全球供应链重构，大宗商品价格波动加剧",
                "summary": "全球供应链正在经历深度调整，大宗商品价格波动加剧，市场不确定性增加。",
                "url": "https://www.ftchinese.com/",
                "source": "FT中文网"
            }
        ]
    }
    
    tags_pool = ["市场动态", "价格走势", "政策解读", "行业分析", "投资机会", "风险提示", "数据报告"]
    
    news_list = []
    
    # 根据分类筛选新闻
    if category == "all":
        all_news = []
        for cat_news in news_sources.values():
            all_news.extend(cat_news)
        selected_news = all_news
    else:
        selected_news = news_sources.get(category, [])
    
    # 生成新闻列表
    start_index = (page - 1) * limit
    for i in range(start_index, min(start_index + limit, len(selected_news) * 10)):
        idx = i % len(selected_news)
        news_item_template = selected_news[idx]
        
        time_delta = random.randint(i * 30, (i + 1) * 60)
        news_time = datetime.now() - timedelta(minutes=time_delta)
        
        news_item = {
            "id": f"news_{i + 1}",
            "title": news_item_template["title"],
            "summary": news_item_template["summary"],
            "source": news_item_template["source"],
            "time": news_time.strftime("%Y-%m-%d %H:%M"),
            "category": category if category != "all" else random.choice(list(news_sources.keys())),
            "views": random.randint(100, 10000),
            "tags": random.sample(tags_pool, k=random.randint(2, 4)),
            "url": news_item_template["url"]
        }
        news_list.append(news_item)
    
    return {
        "news": news_list,
        "page": page,
        "limit": limit,
        "total": len(selected_news) * 10,
        "has_more": page * limit < len(selected_news) * 10
    }

# Vercel适配
def handler(request):
    return app(request.scope, request.receive, request.send)
