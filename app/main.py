from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, SearchHistory
from app.schemas import UserCreate, UserLogin, SearchRequest, ChatRequest, ChatResponse
from app.retriever import Retriever
from app.llm import LLM
from app.eastmoney_scraper import EastMoneyScraper, get_eastmoney_data, format_eastmoney_data
from app.config import Config
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional

# 数据库配置
engine = create_engine(Config.get_database_url(), connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 初始化东方财富网爬虫
eastmoney_scraper = EastMoneyScraper()

app = FastAPI(title="Block Trade DT", description="大宗交易数据检索平台")

# 静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 安全配置
security = HTTPBearer()

# 初始化检索器和LLM
retriever = Retriever()
llm = LLM()

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.get_jwt_secret_key(), algorithm=Config.ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, Config.get_jwt_secret_key(), algorithms=[Config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的认证凭据")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="无效的认证凭据")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index_v2.html", {"request": request})

@app.get("/trends", response_class=HTMLResponse)
async def read_trends(request: Request):
    return templates.TemplateResponse("trends_dark.html", {"request": request})

@app.post("/api/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
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
    
    return {"message": "注册成功"}

@app.post("/api/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not user.check_password(user_data.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    }

@app.get("/api/user/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name
    }

@app.post("/api/search")
async def search(
    search_request: SearchRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 执行搜索
    results = retriever.search(search_request.query, search_request.top_k)
    
    # 生成AI摘要
    summary = None
    if search_request.use_llm and results:
        summary = llm.generate_summary(search_request.query, results)
    
    # 记录搜索历史（如果用户已登录）
    if current_user:
        search_history = SearchHistory(
            user_id=current_user.id,
            query=search_request.query,
            results_count=len(results),
            use_llm=search_request.use_llm
        )
        db.add(search_history)
        db.commit()
    
    return {
        "results": results,
        "summary": summary,
        "total": len(results)
    }

@app.get("/api/search/history")
async def get_search_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).order_by(SearchHistory.search_time.desc()).limit(20).all()
    
    return [
        {
            "id": item.id,
            "query": item.query,
            "results_count": item.results_count,
            "search_time": item.search_time.isoformat(),
            "use_llm": item.use_llm
        }
        for item in history
    ]

@app.get("/api/eastmoney/data")
async def get_eastmoney_market_data():
    """
    获取东方财富网大宗交易数据
    """
    try:
        # 获取原始数据
        raw_data = get_eastmoney_data()
        
        # 格式化数据
        formatted_data = format_eastmoney_data()
        
        return {
            "success": True,
            "data": formatted_data,
            "raw_data": raw_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/eastmoney/statistics")
async def get_eastmoney_statistics():
    """
    获取东方财富网市场统计数据
    """
    try:
        stats = eastmoney_scraper.get_market_statistics()
        return stats
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/eastmoney/stocks")
async def get_eastmoney_active_stocks():
    """
    获取东方财富网活跃股票数据
    """
    try:
        stocks = eastmoney_scraper.get_active_stocks()
        return stocks
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/eastmoney/block-trades")
async def get_block_trades(date: Optional[str] = None, page: int = 1, page_size: int = 50):
    """
    获取大宗交易明细数据
    """
    try:
        result = eastmoney_scraper.get_block_trade_details(date, page, page_size)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/eastmoney/recent-trades")
async def get_recent_trades(days: int = 7):
    """
    获取最近N天的大宗交易数据
    """
    try:
        result = eastmoney_scraper.get_recent_block_trades(days)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/eastmoney/hot-stocks")
async def get_hot_stocks(days: int = 7):
    """
    获取热门股票（最近N天大宗交易最多的股票）
    """
    try:
        result = eastmoney_scraper.get_hot_stocks(days)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/trends/data")
async def get_trends_data():
    """
    获取趋势数据（现在使用东方财富网数据）
    """
    try:
        # 尝试获取东方财富网数据
        eastmoney_data = get_eastmoney_data()
        if eastmoney_data.get("success"):
            formatted_data = format_eastmoney_data()
            if formatted_data.get("success"):
                return formatted_data["data"]
        
        # 如果获取失败，使用模拟数据
        import random
        from datetime import datetime, timedelta
        
        # 生成模拟的市场数据
        market_data = {
            "shanghai_index": round(3600 + random.uniform(-100, 100), 2),
            "shanghai_change": round(random.uniform(-2, 2), 2),
            "total_volume": round(random.uniform(50000, 80000), 2),
            "premium_volume": round(random.uniform(200, 500), 2),
            "discount_volume": round(random.uniform(45000, 75000), 2)
        }
        
        # 生成模拟的每日统计数据
        daily_stats = []
        for i in range(30):
            date = datetime.now() - timedelta(days=29-i)
            daily_stats.append({
                "date": date.strftime("%Y-%m-%d"),
                "index": round(3600 + random.uniform(-150, 150), 2),
                "change": round(random.uniform(-3, 3), 2),
                "total_volume": round(random.uniform(40000, 90000), 2),
                "premium_volume": round(random.uniform(100, 800), 2),
                "premium_ratio": round(random.uniform(0.5, 2.5), 2),
                "discount_volume": round(random.uniform(35000, 85000), 2),
                "discount_ratio": round(random.uniform(97.5, 99.5), 2)
            })
        
        return {
            "market_data": market_data,
            "daily_stats": daily_stats
        }
    except Exception as e:
        # 返回基础模拟数据
        return {
            "market_data": {
                "shanghai_index": 3666.44,
                "shanghai_change": -0.46,
                "total_volume": 4567.89,
                "premium_volume": 234.56,
                "discount_volume": 4333.33
            },
            "daily_stats": [],
            "error": str(e)
        }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(chat_request: ChatRequest):
    """
    与AI进行对话（使用本地LLM）
    """
    try:
        # 使用本地LLM进行对话
        response = llm.generate_summary(chat_request.message, [])
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat(),
            success=True
        )
    except Exception as e:
        return ChatResponse(
            response=f"抱歉，AI服务暂时不可用: {str(e)}",
            timestamp=datetime.now().isoformat(),
            success=False
        )

@app.post("/api/chat/analyze")
async def analyze_market_with_ai():
    """
    使用AI分析市场数据
    """
    try:
        # 获取当前市场数据
        trends_data = await get_trends_data()
        market_data = trends_data["market_data"]
        
        # 使用本地LLM分析
        analysis = llm.generate_summary("请分析以下市场数据", [str(market_data)])
        
        return {
            "analysis": analysis,
            "market_data": market_data,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
    except Exception as e:
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
        advice = llm.generate_summary(f"请提供投资建议: {chat_request.message}", [])
        
        return {
            "advice": advice,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
    except Exception as e:
        return {
            "advice": f"抱歉，投资建议服务暂时不可用: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "success": False
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

