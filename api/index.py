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

# 初始化智谱AI
zhipu_ai = ZhipuAI(api_key=Config.get_zhipu_api_key())

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

# 主页路由
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 趋势页面
@app.get("/trends", response_class=HTMLResponse)
async def trends_page(request: Request):
    return templates.TemplateResponse("trends.html", {"request": request})

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
async def search(request: SearchRequest, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    try:
        # 执行搜索
        results = retriever.search(request.query)
        
        # 生成摘要
        summary = llm.generate_summary(request.query, results)
        
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(chat_request: ChatRequest):
    try:
        response = zhipu_ai.chat(
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
    return {
        "market_data": [
            {"symbol": "AAPL", "price": round(random.uniform(150, 200), 2), "change": round(random.uniform(-5, 5), 2)},
            {"symbol": "GOOGL", "price": round(random.uniform(2500, 3000), 2), "change": round(random.uniform(-50, 50), 2)},
            {"symbol": "MSFT", "price": round(random.uniform(300, 400), 2), "change": round(random.uniform(-10, 10), 2)},
            {"symbol": "TSLA", "price": round(random.uniform(200, 300), 2), "change": round(random.uniform(-20, 20), 2)},
        ],
        "timestamp": datetime.now().isoformat()
    }

# Vercel适配
def handler(request):
    return app(request.scope, request.receive, request.send)
