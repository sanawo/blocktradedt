"""
增强版API入口 - 集成知识图谱和智能检索功能
"""
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
from app.config import Config
from app.enhanced_retriever import EnhancedRetriever
from app.intent_classifier import IntentClassifier, QueryOptimizer
from app.pattern_prompter import StructuredPatternPrompter
from app.kg_builder import KnowledgeGraphBuilder
import jwt
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./block_trade_dt.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 初始化增强组件
logger.info("正在初始化增强检索组件...")
enhanced_retriever = None
intent_classifier = None
query_optimizer = None
pattern_prompter = None
kg_builder = None

def init_enhanced_components():
    """延迟初始化增强组件"""
    global enhanced_retriever, intent_classifier, query_optimizer, pattern_prompter, kg_builder
    
    try:
        if enhanced_retriever is None:
            logger.info("初始化增强检索器...")
            enhanced_retriever = EnhancedRetriever()
        if intent_classifier is None:
            logger.info("初始化意图分类器...")
            intent_classifier = IntentClassifier()
            query_optimizer = QueryOptimizer(intent_classifier)
        if pattern_prompter is None:
            logger.info("初始化模式提示器...")
            pattern_prompter = StructuredPatternPrompter()
        if kg_builder is None:
            logger.info("初始化知识图谱构建器...")
            kg_builder = KnowledgeGraphBuilder()
            kg_builder.load_pulp_domain_seed_data()
        logger.info("✅ 增强组件初始化完成")
    except Exception as e:
        logger.error(f"❌ 初始化增强组件失败: {e}")

# 创建应用
app = FastAPI(title="Enhanced Block Trade DT", description="增强版大宗交易数据检索平台 - 融入知识图谱")

# 静态文件和模板
try:
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("✅ 静态文件目录已挂载")
    if os.path.exists("templates"):
        templates = Jinja2Templates(directory="templates")
        logger.info("✅ 模板目录已加载")
    else:
        templates = None
except Exception as e:
    logger.error(f"❌ 初始化静态文件或模板失败: {e}")
    templates = None

# 安全配置
security = HTTPBearer()

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
    encoded_jwt = jwt.encode(to_encode, Config.get_jwt_secret_key(), algorithm="HS256")
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, Config.get_jwt_secret_key(), algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的认证凭据")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="无效的认证凭据")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user

# 主页
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    if templates is None:
        return HTMLResponse("<h1>Enhanced Block Trade DT</h1><p>增强版大宗交易数据检索平台</p>")
    return templates.TemplateResponse("index_v2.html", {"request": request})

# 增强检索API
@app.post("/api/enhanced/search")
async def enhanced_search(
    search_request: SearchRequest,
    current_user: Optional[User] = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    """增强版智能检索API"""
    try:
        init_enhanced_components()
        
        # 1. 查询意图识别
        intent_result = intent_classifier.classify(search_request.query) if intent_classifier else {}
        
        # 2. 查询优化
        optimized = query_optimizer.optimize(search_request.query) if query_optimizer else {"optimized_query": search_request.query}
        
        # 3. 执行增强检索
        results = enhanced_retriever.search(search_request.query, top_k=search_request.top_k) if enhanced_retriever else []
        
        # 4. 生成答案
        answer_result = enhanced_retriever.answer_query(search_request.query) if enhanced_retriever else {"answer": ""}
        
        return {
            "query": search_request.query,
            "optimized_query": optimized.get("optimized_query", search_request.query),
            "intent": intent_result,
            "results": results,
            "answer": answer_result.get("answer", ""),
            "total": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"检索失败: {e}")
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")

# 意图分析API
@app.post("/api/search/intent")
async def analyze_intent(query: str):
    """查询意图分析API"""
    try:
        init_enhanced_components()
        parsed = intent_classifier.parse_query(query) if intent_classifier else {"intent": "general", "confidence": 0}
        optimized = query_optimizer.optimize(query) if query_optimizer else {"optimized_query": query}
        
        return {
            "query": query,
            "intent": parsed.get("intent", "general"),
            "confidence": parsed.get("confidence", 0),
            "entities": parsed.get("entities", []),
            "attributes": parsed.get("attributes", []),
            "optimized_query": optimized.get("optimized_query", query),
            "suggestions": parsed.get("suggestions", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"意图分析失败: {str(e)}")

# 知识图谱统计API
@app.get("/api/kg/statistics")
async def get_kg_statistics():
    """获取知识图谱统计信息"""
    try:
        init_enhanced_components()
        stats = enhanced_retriever.get_kg_statistics() if enhanced_retriever else {}
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# 健康检查
@app.get("/health")
async def health_check():
    init_enhanced_components()
    return {
        "status": "healthy",
        "service": "Enhanced Block Trade DT",
        "components": {
            "enhanced_retriever": enhanced_retriever is not None,
            "intent_classifier": intent_classifier is not None,
            "pattern_prompter": pattern_prompter is not None,
            "kg_builder": kg_builder is not None
        }
    }

# Vercel适配
def handler(request):
    return app(request.scope, request.receive, request.send)

