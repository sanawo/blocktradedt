from fastapi import FastAPI, Request, HTTPException, Depends, status, UploadFile, File
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
# from app.zhipu_ai import ZhipuAI  # Removed to fix deployment issues
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
    # Disabled to fix deployment issues
    return None

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

# 研报摘要页面
@app.get("/report", response_class=HTMLResponse)
async def report_summarizer_page(request: Request):
    if templates is None:
        return HTMLResponse("<h1>研报摘要生成器</h1><p>模板系统未加载</p>")
    return templates.TemplateResponse("report_summarizer.html", {"request": request})

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
        from app.llm import LLM
        
        # 使用本地LLM
        llm = LLM()
        
        # 获取消息，确保不为空
        message = chat_request.message if chat_request.message else ""
        
        # 如果消息是空的，返回友好的提示
        if not message or not message.strip():
            return ChatResponse(
                response="您好！我是Block Trade DT的AI助手。我可以帮助您：\n1. 查询市场数据\n2. 分析市场趋势\n3. 解答交易相关问题\n4. 生成研报摘要\n\n请输入您的问题，我将为您提供帮助。",
                timestamp=datetime.now().isoformat(),
                success=True
            )
        
        # 使用本地AI回复逻辑（总是可用的fallback）
        try:
            response = generate_local_ai_response(message)
            
            # 如果配置了AI客户端，尝试使用GLM-4.5-Flash（但确保有fallback）
            if llm.client:
                try:
                    ai_response = llm.chat(
                        message,
                        context=chat_request.conversation_history if chat_request.conversation_history else None,
                        system_prompt=chat_request.system_prompt if chat_request.system_prompt else None,
                        enable_thinking=chat_request.enable_thinking if chat_request.enable_thinking is not None else True,
                        stream=chat_request.stream if chat_request.stream is not None else False
                    )
                    # 只有在返回有效内容时才使用AI回复
                    if ai_response and ai_response.strip() and "暂时不可用" not in ai_response and "检查API密钥" not in ai_response:
                        response = ai_response
                except Exception as e:
                    logger.warning(f"AI客户端调用失败，使用本地回复: {e}")
                    import traceback
                    logger.warning(traceback.format_exc())
                    # 继续使用本地回复
        
        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            response = "抱歉，处理您的问题时遇到错误。请稍后重试或尝试其他问题。"
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat(),
            success=True
        )
    except Exception as e:
        import traceback
        logger.error(f"Chat API错误: {e}")
        logger.error(traceback.format_exc())
        # 确保总是返回有效的响应
        try:
            return ChatResponse(
                response=f"抱歉，AI服务遇到问题: {str(e)}。请稍后重试或联系管理员。",
                timestamp=datetime.now().isoformat(),
                success=False
            )
        except:
            # 最后的fallback，确保API不会崩溃
            return JSONResponse(
                content={
                    "response": "AI服务暂时不可用，请稍后重试。",
                    "timestamp": datetime.now().isoformat(),
                    "success": False
                },
                status_code=200
            )

def generate_local_ai_response(message: str) -> str:
    """生成本地AI回复"""
    message_lower = message.lower()
    
    # 关键词匹配回复
    if any(kw in message_lower for kw in ['价格', '报价', '售价']):
        return "根据当前市场数据，大宗商品价格波动较大。建议关注实时行情和市场动态。您可以访问'市场数据'页面查看最新价格信息。"
    
    elif any(kw in message_lower for kw in ['趋势', '走势', '预测']):
        return "市场趋势分析显示，当前大宗交易市场整体保持稳定。建议关注'趋势图表'页面获取详细的趋势分析数据。"
    
    elif any(kw in message_lower for kw in ['新闻', '资讯', '动态']):
        return "最新市场资讯已更新在'实时资讯'页面。您可以查看最新的行业动态和政策解读。"
    
    elif any(kw in message_lower for kw in ['纸浆', '浆料', '纸浆市场']):
        return "纸浆市场方面，根据最新数据显示，针叶木浆和阔叶木浆价格相对稳定。建议关注上游原材料价格变化对市场的影响。您可以访问相关页面查看详细数据。"
    
    elif any(kw in message_lower for kw in ['你好', 'hello', '帮助', 'help']):
        return "您好！我是Block Trade DT的AI助手。我可以帮助您：\n1. 查询市场数据\n2. 分析市场趋势\n3. 解答交易相关问题\n\n请告诉我您需要什么帮助？"
    
    elif any(kw in message_lower for kw in ['研报', '报告', '摘要']):
        return "您可以使用'研报摘要'功能，上传5000字以内的行业研报，系统将在8秒内为您生成结构化摘要，包括核心观点、数据支撑、趋势判断等。访问'研报摘要'页面即可使用。"
    
    else:
        return f"关于'{message}'，这是一个很好的问题。作为大宗交易数据分析平台，我建议您：\n1. 查看'市场数据'页面获取相关数据\n2. 访问'智能分析'页面查看深度分析\n3. 使用'研报摘要'功能分析相关报告\n\n如需更详细的信息，请提供更具体的查询内容。"

@app.post("/api/chat/analyze")
async def analyze_market_with_ai():
    """
    使用AI分析市场数据
    """
    try:
        import random
        
        # 生成市场统计数据（避免循环依赖）
        stats = {
            "total_volume": round(random.uniform(50, 100), 2),
            "total_transactions": random.randint(100, 500),
            "avg_price": round(random.uniform(-2, 2), 2),
            "active_sellers": random.randint(50, 150)
        }
        
        # 使用本地AI生成分析
        analysis_query = f"请分析以下市场数据：{stats}"
        analysis = generate_local_ai_response(analysis_query)
        
        # 生成更具体的市场分析
        analysis_text = f"""📊 **市场数据分析**

根据当前市场统计数据：
- 总交易量: {stats.get('total_volume', 'N/A')}
- 交易次数: {stats.get('total_transactions', 'N/A')}
- 平均价格变化: {stats.get('avg_price', 'N/A')}%
- 活跃卖家: {stats.get('active_sellers', 'N/A')}

**市场分析：**
{analysis}

**建议：**
- 关注实时趋势图表获取更详细的市场动态
- 查看最新市场资讯了解行业动态
- 使用智能分析功能进行深度分析

**风险提示：**
市场数据仅供参考，投资需谨慎。
"""
        
        return {
            "analysis": analysis_text,
            "market_data": stats,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
    except Exception as e:
        logger.error(f"AI市场分析失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "analysis": f"抱歉，AI分析服务暂时不可用: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "success": False
        }

@app.post("/api/chat/advice")
async def get_investment_advice(chat_request: ChatRequest):
    """
    获取投资建议
    """
    try:
        from app.llm import LLM
        
        llm = LLM()
        message = chat_request.message or "请提供投资建议"
        
        # 使用本地AI生成投资建议
        advice = generate_local_ai_response(f"投资建议：{message}")
        
        # 增强投资建议回复
        if "投资" in message or "建议" in message:
            advice = f"""💼 **投资建议**

{advice}

**风险提示：**
投资有风险，建议仅供参考。请在做出投资决策前：
1. 充分了解市场情况
2. 评估自身风险承受能力
3. 咨询专业投资顾问
4. 分散投资，降低风险
"""
        
        return {
            "advice": advice,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
    except Exception as e:
        logger.error(f"投资建议生成失败: {e}")
        return {
            "advice": f"抱歉，投资建议服务暂时不可用: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "success": False
        }

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

# 研报摘要API
@app.post("/api/report/summarize")
async def summarize_report_api(
    request: Request,
    file: Optional[UploadFile] = File(None),
    report_text: Optional[str] = None
):
    """
    生成研报摘要
    支持文本上传或文件上传（5000字以内，8秒内完成）
    """
    try:
        from app.report_summarizer import ReportSummarizer
        
        summarizer = ReportSummarizer()
        
        # 处理文件上传
        if file:
            try:
                content = await file.read()
                # 尝试多种编码
                encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
                report_text = None
                for encoding in encodings:
                    try:
                        report_text = content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if report_text is None:
                    raise HTTPException(status_code=400, detail="无法解码文件内容，请使用UTF-8编码的文件")
            except Exception as e:
                logger.error(f"文件读取失败: {e}")
                raise HTTPException(status_code=400, detail=f"文件读取失败: {str(e)}")
        
        # 处理JSON文本上传
        if not report_text and not file:
            # 尝试从请求体获取JSON数据
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    json_data = await request.json()
                    report_text = json_data.get("report_text") or json_data.get("text")
                except:
                    pass
        
        if not report_text:
            raise HTTPException(status_code=400, detail="未提供研报文本，请上传文件或输入文本内容")
        
        # 限制文本长度
        if len(report_text) > 5000:
            report_text = report_text[:5000]
            logger.warning("文本超过5000字，已截取前5000字")
        
        # 检查文本是否为空
        if not report_text.strip():
            raise HTTPException(status_code=400, detail="研报文本为空")
        
        # 生成摘要
        start_time = datetime.now()
        try:
            summary = summarizer.summarize(report_text)
        except Exception as e:
            logger.error(f"摘要生成失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"摘要生成失败: {str(e)}")
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # 格式化输出
        try:
            formatted = summarizer.format_summary(summary)
        except Exception as e:
            logger.error(f"格式化失败: {e}")
            # 即使格式化失败，也返回基础摘要
            formatted = {
                "title": summary.title if hasattr(summary, 'title') else "未识别标题",
                "core_viewpoints": summary.core_viewpoints if hasattr(summary, 'core_viewpoints') else [],
                "data_support": summary.data_support if hasattr(summary, 'data_support') else [],
                "trend_judgment": summary.trend_judgment if hasattr(summary, 'trend_judgment') else "趋势判断不明确",
                "key_findings": summary.key_findings if hasattr(summary, 'key_findings') else [],
                "risk_analysis": summary.risk_analysis if hasattr(summary, 'risk_analysis') else [],
                "recommendations": summary.recommendations if hasattr(summary, 'recommendations') else [],
                "confidence": summary.confidence if hasattr(summary, 'confidence') else 0.0
            }
        
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
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
    }

# Vercel适配
def handler(request):
    return app(request.scope, request.receive, request.send)
