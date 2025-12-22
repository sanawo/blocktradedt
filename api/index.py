import sys
import os
import logging

# 设置日志（必须在其他初始化之前）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("🚀 正在初始化应用...")

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 安全导入所有依赖
try:
    from fastapi import FastAPI, Request, HTTPException, Depends, status, File, UploadFile, Body
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    logger.info("✅ FastAPI 导入成功")
except ImportError as e:
    logger.error(f"❌ FastAPI 导入失败: {e}")
    raise

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker
    logger.info("✅ SQLAlchemy 导入成功")
except ImportError as e:
    logger.error(f"❌ SQLAlchemy 导入失败: {e}")
    raise

try:
    from app.models import Base, User, SearchHistory, DzjyTrade
    logger.info("✅ Models 导入成功")
except ImportError as e:
    logger.error(f"❌ Models 导入失败: {e}")
    raise

try:
    from app.schemas import UserCreate, UserLogin, SearchRequest, ChatRequest, ChatResponse
    logger.info("✅ Schemas 导入成功")
except ImportError as e:
    logger.error(f"❌ Schemas 导入失败: {e}")
    raise

try:
    from app.retriever import Retriever
    logger.info("✅ Retriever 导入成功")
except ImportError as e:
    logger.error(f"❌ Retriever 导入失败: {e}")
    Retriever = None

try:
    from app.llm import LLM
    logger.info("✅ LLM 导入成功")
except ImportError as e:
    logger.error(f"❌ LLM 导入失败: {e}")
    LLM = None

try:
    from app.config import Config
    logger.info("✅ Config 导入成功")
except ImportError as e:
    logger.error(f"❌ Config 导入失败: {e}")
    raise

try:
    import jwt
    logger.info("✅ PyJWT 导入成功")
except ImportError as e:
    logger.error(f"❌ PyJWT 导入失败: {e}")
    raise

from datetime import datetime, timedelta
from typing import Optional

# 数据库配置 - 使用内存数据库适配Vercel
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./block_trade_dt.db")
try:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # 创建数据库表（包括DzjyTrade表）
    Base.metadata.create_all(bind=engine)
    logger.info("✅ 数据库初始化成功，所有表已创建")
except Exception as e:
    logger.error(f"❌ 数据库初始化失败: {e}")
    # 使用内存数据库作为后备
    try:
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 使用内存数据库作为后备")
    except Exception as e2:
        logger.error(f"❌ 内存数据库初始化也失败: {e2}")
        # 最后的后备方案：创建一个基本的engine
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 初始化智谱AI（延迟初始化以避免启动时错误）
zhipu_ai = None

def get_zhipu_ai():
    """获取智谱AI客户端"""
    global zhipu_ai
    if zhipu_ai is None:
        try:
            api_key = os.getenv('ZHIPU_API_KEY')
            if api_key:
                from zhipuai import ZhipuAI
                zhipu_ai = ZhipuAI(api_key=api_key)
                logger.info("✅ 智谱AI客户端初始化成功")
            else:
                logger.warning("⚠️  ZHIPU_API_KEY未设置，AI功能将不可用")
        except ImportError:
            logger.warning("⚠️  zhipuai包未安装，AI功能将不可用")
        except Exception as e:
            logger.error(f"❌ 智谱AI初始化失败: {e}")
    return zhipu_ai

app = FastAPI(title="Block Trade DT", description="大宗交易数据检索平台")

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
        if Retriever is None:
            logger.warning("⚠️  Retriever类不可用")
            return None
        try:
            retriever = Retriever()
            logger.info("✅ Retriever初始化成功")
        except Exception as e:
            logger.error(f"❌ Retriever初始化失败: {e}")
            retriever = None
    return retriever

def get_llm():
    global llm
    if llm is None:
        if LLM is None:
            logger.warning("⚠️  LLM类不可用")
            return None
        try:
            llm = LLM()
            logger.info("✅ LLM初始化成功")
        except Exception as e:
            logger.error(f"❌ LLM初始化失败: {e}")
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
    """健康检查端点，用于验证服务是否正常运行"""
    try:
        # 检查数据库连接
        db_status = "ok"
        try:
            db = SessionLocal()
            db.close()
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return {
            "status": "healthy",
            "service": "Block Trade DT",
            "database": db_status,
            "retriever_available": Retriever is not None,
            "llm_available": LLM is not None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

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
        import time
        start_time = time.time()
        
        # 获取检索器和LLM
        retriever_instance = get_retriever()
        llm_instance = get_llm()
        
        if retriever_instance is None:
            raise HTTPException(status_code=503, detail="检索服务暂时不可用，请稍后重试")
        
        # 执行搜索（支持top_k参数）
        top_k = getattr(request, 'top_k', 10)
        if hasattr(retriever_instance, 'search'):
            # 检查search方法是否支持top_k参数
            import inspect
            sig = inspect.signature(retriever_instance.search)
            if 'top_k' in sig.parameters:
                results = retriever_instance.search(request.query, top_k=top_k)
            else:
                results = retriever_instance.search(request.query)
                # 如果返回的结果超过top_k，进行截断
                if isinstance(results, list) and len(results) > top_k:
                    results = results[:top_k]
        else:
            results = []
        
        # 如果results是列表但元素格式不对，进行转换
        if results and isinstance(results, list) and len(results) > 0:
            # 检查结果格式，确保统一
            formatted_results = []
            for r in results:
                if isinstance(r, dict):
                    # 如果已经有listing字段，保持原样
                    if 'listing' in r:
                        formatted_results.append(r)
                    else:
                        # 否则包装为listing格式
                        formatted_results.append({
                            "score": r.get("score", 0.0),
                            "listing": r
                        })
                else:
                    formatted_results.append(r)
            results = formatted_results
        
        # 生成摘要
        summary = ""
        if llm_instance and llm_instance.client:
            try:
                summary = llm_instance.generate_summary(request.query, results)
            except Exception as e:
                logger.warning(f"生成摘要失败: {e}")
                summary = f"找到 {len(results)} 条相关结果"
        else:
            # 生成本地摘要
            if results:
                summary = f"为您找到 {len(results)} 条与'{request.query}'相关的记录。"
                if len(results) > 0:
                    first_result = results[0]
                    listing = first_result.get("listing", first_result) if isinstance(first_result, dict) else first_result
                    if isinstance(listing, dict):
                        title = listing.get("title", "")
                        if title:
                            summary += f" 最相关的结果：{title}。"
            else:
                summary = f"未找到与'{request.query}'相关的记录。"
        
        # 计算搜索耗时
        search_time = time.time() - start_time
        
        # 记录搜索历史（如果用户已登录）
        if current_user:
            try:
                search_history = SearchHistory(
                    user_id=current_user.id,
                    query=request.query,
                    results_count=len(results)
                )
                db.add(search_history)
                db.commit()
            except Exception as e:
                logger.warning(f"记录搜索历史失败: {e}")
        
        return {
            "query": request.query,
            "results": results,
            "summary": summary,
            "total": len(results),
            "search_time": f"{search_time:.2f}秒",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索失败: {e}")
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
        # 优先使用LLM实例
        llm_instance = get_llm()
        if llm_instance and llm_instance.client:
            # 使用LLM的chat方法
            system_prompt = chat_request.system_prompt or "你是一个专业的金融分析师，专门分析大宗交易数据。请用中文回答，语言要专业、准确。请始终使用中文回复，不要使用英文。"
            response = llm_instance.chat(
                message=chat_request.message,
                system_prompt=system_prompt,
                context=chat_request.context if hasattr(chat_request, 'context') else None
            )
            return ChatResponse(response=response, timestamp=datetime.now().isoformat(), success=True)
        
        # 回退到智谱AI客户端
        ai_client = get_zhipu_ai()
        if ai_client is None:
            return ChatResponse(
                response="抱歉，AI服务暂时不可用，请检查API密钥配置",
                timestamp=datetime.now().isoformat(),
                success=False
            )
        
        # 使用智谱AI直接调用
        system_prompt = chat_request.system_prompt or "你是一个专业的金融分析师，专门分析大宗交易数据。请用中文回答，语言要专业、准确。请始终使用中文回复，不要使用英文。"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": chat_request.message}
        ]
        
        response = ai_client.chat.completions.create(
            model="glm-4-flash",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return ChatResponse(
            response=response.choices[0].message.content,
            timestamp=datetime.now().isoformat(),
            success=True
        )
    except Exception as e:
        logger.error(f"AI对话失败: {e}")
        return ChatResponse(
            response=f"抱歉，AI服务暂时不可用: {str(e)}",
            timestamp=datetime.now().isoformat(),
            success=False
        )

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

@app.get("/api/dzjy/latest")
async def get_dzjy_latest(db: Session = Depends(get_db), limit: int = 10):
    """
    获取最新大宗交易数据
    
    示例响应:
    {
        "success": true,
        "data": [
            {
                "trade_time": "2025-01-10T10:30:00",
                "stock_code": "000001",
                "stock_name": "平安银行",
                "volume": 100.5,
                "amount": 1500.0,
                "price": 15.0,
                "source_raw": "{...}"
            }
        ],
        "count": 10
    }
    """
    try:
        from sqlalchemy import desc
        
        trades = db.query(DzjyTrade).order_by(desc(DzjyTrade.trade_time)).limit(limit).all()
        
        data = [{
            "trade_time": trade.trade_time.isoformat() if trade.trade_time else None,
            "stock_code": trade.stock_code,
            "stock_name": trade.stock_name,
            "volume": trade.volume,
            "amount": trade.amount,
            "price": trade.price,
            "source_raw": trade.source_raw
        } for trade in trades]
        
        return {
            "success": True,
            "data": data,
            "count": len(data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取最新大宗交易数据失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": [],
            "count": 0
        }

@app.get("/api/dzjy/trends")
async def get_dzjy_trends(db: Session = Depends(get_db), period: str = "24h"):
    """
    获取大宗交易趋势数据
    
    参数:
    - period: 时间周期，可选值: 24h, 7d, 30d
    
    示例响应:
    {
        "success": true,
        "period": "24h",
        "data": [
            {
                "date": "2025-01-10",
                "volume": 1000.5,
                "amount": 15000.0,
                "count": 50
            }
        ]
    }
    """
    try:
        from sqlalchemy import func, and_
        
        # 计算时间范围
        now = datetime.now()
        if period == "24h":
            start_time = now - timedelta(hours=24)
            group_format = "%Y-%m-%d %H:00"
        elif period == "7d":
            start_time = now - timedelta(days=7)
            group_format = "%Y-%m-%d"
        elif period == "30d":
            start_time = now - timedelta(days=30)
            group_format = "%Y-%m-%d"
        else:
            start_time = now - timedelta(hours=24)
            group_format = "%Y-%m-%d %H:00"
        
        # 查询数据并分组统计
        # 获取数据库dialect名称
        dialect_name = db.bind.dialect.name if hasattr(db.bind, 'dialect') else 'sqlite'
        if dialect_name == 'sqlite':
            # SQLite使用strftime
            date_expr = func.strftime(group_format, DzjyTrade.trade_time)
        else:
            # PostgreSQL使用to_char
            date_expr = func.to_char(DzjyTrade.trade_time, group_format.replace('%', ''))
        
        results = db.query(
            date_expr.label('date'),
            func.sum(DzjyTrade.volume).label('volume'),
            func.sum(DzjyTrade.amount).label('amount'),
            func.count(DzjyTrade.id).label('count')
        ).filter(
            DzjyTrade.trade_time >= start_time
        ).group_by('date').order_by('date').all()
        
        data = [{
            "date": r.date,
            "volume": float(r.volume or 0),
            "amount": float(r.amount or 0),
            "count": r.count or 0
        } for r in results]
        
        return {
            "success": True,
            "period": period,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取趋势数据失败: {e}")
        # 返回空数据而不是错误
        return {
            "success": True,
            "period": period,
            "data": [],
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/dzjy/list")
async def get_dzjy_list(db: Session = Depends(get_db), page: int = 1, size: int = 20):
    """
    获取大宗交易列表（分页）
    
    参数:
    - page: 页码，从1开始
    - size: 每页数量，默认20
    
    示例响应:
    {
        "success": true,
        "page": 1,
        "size": 20,
        "total": 100,
        "data": [
            {
                "trade_time": "2025-01-10T10:30:00",
                "stock_code": "000001",
                "stock_name": "平安银行",
                "volume": 100.5,
                "amount": 1500.0,
                "price": 15.0
            }
        ]
    }
    """
    try:
        from sqlalchemy import desc
        
        # 计算总数
        total = db.query(DzjyTrade).count()
        
        # 分页查询
        offset = (page - 1) * size
        trades = db.query(DzjyTrade).order_by(desc(DzjyTrade.trade_time)).offset(offset).limit(size).all()
        
        data = [{
            "trade_time": trade.trade_time.isoformat() if trade.trade_time else None,
            "stock_code": trade.stock_code,
            "stock_name": trade.stock_name,
            "volume": trade.volume,
            "amount": trade.amount,
            "price": trade.price
        } for trade in trades]
        
        return {
            "success": True,
            "page": page,
            "size": size,
            "total": total,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取大宗交易列表失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "page": page,
            "size": size,
            "total": 0,
            "data": []
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
                "source": "新浪财经",
                "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80"
            },
            {
                "title": "钢材价格持续上涨，市场供需关系紧张",
                "summary": "受供应链紧张和需求增长双重影响，近期钢材价格持续上涨，市场预期后续仍有上涨空间。",
                "url": "https://www.eastmoney.com/",
                "source": "东方财富网",
                "image": "https://images.unsplash.com/photo-1565372195458-9de0b320ef04?w=800&q=80"
            },
            {
                "title": "有色金属板块领涨，铜价突破历史新高",
                "summary": "有色金属板块表现强劲，铜价突破历史新高，专家建议关注相关投资机会。",
                "url": "https://finance.qq.com/",
                "source": "腾讯财经",
                "image": "https://images.unsplash.com/photo-1639762681057-408e52192e55?w=800&q=80"
            }
        ],
        "policy": [
            {
                "title": "国家发改委发布大宗商品价格调控新政策",
                "summary": "国家发改委出台新政策，加强大宗商品价格监管，维护市场秩序，促进经济稳定发展。",
                "url": "https://www.ndrc.gov.cn/",
                "source": "国家发改委",
                "image": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=800&q=80"
            },
            {
                "title": "证监会优化大宗交易制度，提升市场效率",
                "summary": "证监会发布通知，进一步优化大宗交易制度，简化交易流程，提升市场效率。",
                "url": "https://www.csrc.gov.cn/",
                "source": "证监会",
                "image": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&q=80"
            }
        ],
        "analysis": [
            {
                "title": "2024年大宗交易市场分析报告出炉",
                "summary": "权威机构发布年度大宗交易市场分析报告，详细解读市场趋势，为投资者提供参考。",
                "url": "https://www.caixin.com/",
                "source": "财新网",
                "image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80"
            },
            {
                "title": "机构：下半年大宗商品市场将迎来结构性机会",
                "summary": "多家研究机构预测，下半年大宗商品市场将呈现结构性分化，能源和有色金属板块值得关注。",
                "url": "https://www.yicai.com/",
                "source": "第一财经",
                "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80"
            }
        ],
        "company": [
            {
                "title": "某龙头企业大宗交易频现，机构资金持续流入",
                "summary": "近期某龙头企业频繁出现大宗交易，机构资金持续流入，市场关注度提升。",
                "url": "https://www.21jingji.com/",
                "source": "21世纪经济报道",
                "image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&q=80"
            }
        ],
        "international": [
            {
                "title": "国际市场动荡，国内大宗商品避险需求上升",
                "summary": "受国际市场不确定性影响，国内投资者避险情绪升温，大宗商品市场受到青睐。",
                "url": "https://wallstreetcn.com/",
                "source": "华尔街见闻",
                "image": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800&q=80"
            },
            {
                "title": "全球供应链重构，大宗商品价格波动加剧",
                "summary": "全球供应链正在经历深度调整，大宗商品价格波动加剧，市场不确定性增加。",
                "url": "https://www.ftchinese.com/",
                "source": "FT中文网",
                "image": "https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?w=800&q=80"
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
            "url": news_item_template["url"],
            "image": news_item_template.get("image", "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80")
        }
        news_list.append(news_item)
    
    return {
        "news": news_list,
        "page": page,
        "limit": limit,
        "total": len(selected_news) * 10,
        "has_more": page * limit < len(selected_news) * 10
    }

# 研报摘要路由
@app.get("/report", response_class=HTMLResponse)
async def report_page(request: Request):
    """研报摘要页面"""
    if templates is None:
        return HTMLResponse("<h1>研报摘要</h1><p>模板系统未加载</p>")
    return templates.TemplateResponse("report_summarizer.html", {"request": request})

@app.post("/api/report/summarize")
async def summarize_report(
    request: Request,
    file: Optional[UploadFile] = File(None)
):
    """
    生成研报摘要
    
    支持：文本上传或文件上传（5000字以内，8秒内完成）
    """
    try:
        from app.report_summarizer import ReportSummarizer
        
        # 初始化研报摘要器
        summarizer = ReportSummarizer()
        
        report_text = None
        
        # 处理文件上传
        if file:
            content = await file.read()
            try:
                report_text = content.decode('utf-8')
            except UnicodeDecodeError:
                # 尝试其他编码
                try:
                    report_text = content.decode('gbk')
                except:
                    raise HTTPException(status_code=400, detail="文件编码不支持，请使用UTF-8编码")
        else:
            # 处理JSON请求体
            try:
                body = await request.json()
                report_text = body.get('report_text')
            except Exception:
                # 如果不是JSON请求，尝试从表单数据读取
                form = await request.form()
                report_text = form.get('report_text')
        
        if not report_text:
            raise HTTPException(status_code=400, detail="未提供研报文本")
        
        # 生成摘要
        start_time = datetime.now()
        summary = summarizer.summarize(report_text)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        
        # 格式化输出
        formatted = summarizer.format_summary(summary)
        
        return {
            "success": True,
            "processing_time": f"{processing_time:.2f}秒",
            "summary": formatted,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成摘要失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成摘要失败: {str(e)}")

# Vercel适配
def handler(request):
    return app(request.scope, request.receive, request.send)

# 应用启动完成日志
logger.info("=" * 50)
logger.info("✅ 应用初始化完成！")
logger.info(f"📊 数据库状态: {'已初始化' if 'engine' in globals() else '未初始化'}")
logger.info(f"🔍 Retriever可用: {Retriever is not None}")
logger.info(f"🤖 LLM可用: {LLM is not None}")
logger.info(f"📁 模板系统: {'已加载' if 'templates' in globals() and templates is not None else '未加载'}")
logger.info("=" * 50)
