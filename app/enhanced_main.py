"""
增强版主应用 - 集成知识图谱和智能检索
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
from datetime import datetime, timedelta
from typing import Optional

# 数据库配置
engine = create_engine(Config.get_database_url(), connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 初始化增强组件
enhanced_retriever = EnhancedRetriever()
intent_classifier = IntentClassifier()
query_optimizer = QueryOptimizer(intent_classifier)
pattern_prompter = StructuredPatternPrompter()
kg_builder = KnowledgeGraphBuilder()

app = FastAPI(title="Enhanced Block Trade DT", description="增强版大宗交易数据检索平台 - 融入知识图谱")

# 静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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

@app.post("/api/enhanced/search")
async def enhanced_search(
    search_request: SearchRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    增强版智能检索API
    """
    try:
        # 1. 查询意图识别
        intent_result = intent_classifier.classify(search_request.query)
        
        # 2. 查询优化
        optimized = query_optimizer.optimize(search_request.query)
        
        # 3. 执行增强检索
        results = enhanced_retriever.search(search_request.query, top_k=search_request.top_k)
        
        # 4. 生成答案
        answer_result = enhanced_retriever.answer_query(search_request.query)
        
        # 记录搜索历史
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
            "query": search_request.query,
            "optimized_query": optimized["optimized_query"],
            "intent": intent_result,
            "results": results,
            "answer": answer_result["answer"],
            "total": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")

@app.post("/api/search/intent")
async def analyze_intent(query: str):
    """
    查询意图分析API
    """
    try:
        parsed = intent_classifier.parse_query(query)
        optimized = query_optimizer.optimize(query)
        
        return {
            "query": query,
            "intent": parsed["intent"],
            "confidence": parsed["confidence"],
            "entities": parsed["entities"],
            "attributes": parsed["attributes"],
            "optimized_query": optimized["optimized_query"],
            "suggestions": parsed["suggestions"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"意图分析失败: {str(e)}")

@app.get("/api/kg/statistics")
async def get_kg_statistics():
    """
    获取知识图谱统计信息
    """
    try:
        stats = enhanced_retriever.get_kg_statistics()
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

@app.get("/api/kg/entity/{entity_name}")
async def get_entity_info(entity_name: str):
    """
    获取实体详细信息
    """
    try:
        entity = kg_builder.get_entity_by_name(entity_name)
        if not entity:
            raise HTTPException(status_code=404, detail="实体不存在")
        
        relations = kg_builder.get_relations(entity.id)
        related_entities = kg_builder.find_related_entities(entity.id, max_depth=2)
        
        return {
            "success": True,
            "entity": {
                "id": entity.id,
                "name": entity.name,
                "type": entity.type,
                "attributes": entity.attributes,
                "relations": [{"predicate": r.predicate, "object": kg_builder.get_entity(r.object).name if kg_builder.get_entity(r.object) else r.object} for r in relations],
                "related_entities": [kg_builder.get_entity(eid).name if kg_builder.get_entity(eid) else eid for eid in related_entities]
            },
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取实体信息失败: {str(e)}")

@app.post("/api/search/expand")
async def expand_query(query: str):
    """
    查询扩展API
    """
    try:
        expanded_queries = enhanced_retriever.expand_query(query)
        
        return {
            "original_query": query,
            "expanded_queries": expanded_queries,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询扩展失败: {str(e)}")

@app.post("/api/pattern/extract")
async def extract_knowledge(pattern_name: str, text: str):
    """
    知识提取API
    """
    try:
        if pattern_name not in pattern_prompter.list_patterns():
            raise HTTPException(status_code=400, detail=f"未知的模式: {pattern_name}")
        
        prompt = pattern_prompter.generate_prompt(pattern_name, text)
        
        return {
            "pattern": pattern_name,
            "text": text,
            "prompt": prompt,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识提取失败: {str(e)}")

@app.get("/api/patterns")
async def list_patterns():
    """
    列出所有可用的知识提取模式
    """
    try:
        patterns = pattern_prompter.list_patterns()
        pattern_infos = {}
        
        for pattern_name in patterns:
            pattern_infos[pattern_name] = pattern_prompter.get_pattern_info(pattern_name)
        
        return {
            "success": True,
            "patterns": pattern_infos,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模式列表失败: {str(e)}")

@app.post("/api/chat/enhanced")
async def enhanced_chat(chat_request: ChatRequest):
    """
    增强版AI对话API
    """
    try:
        # 识别意图
        intent = intent_classifier.classify(chat_request.message)
        
        # 如果与知识图谱相关，执行检索
        if intent["intent"] in ["entity_search", "attribute_search", "relation_search"]:
            answer_result = enhanced_retriever.answer_query(chat_request.message)
            answer = answer_result["answer"]
        else:
            # 通用对话
            answer = f"基于您的查询意图({intent['intent']})，为您提供相关信息。"
        
        return ChatResponse(
            response=answer,
            timestamp=datetime.now().isoformat(),
            success=True
        )
    except Exception as e:
        return ChatResponse(
            response=f"抱歉，AI服务暂时不可用: {str(e)}",
            timestamp=datetime.now().isoformat(),
            success=False
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

