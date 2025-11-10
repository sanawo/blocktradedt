from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import bcrypt

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def set_password(self, password: str):
        """设置密码哈希"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    query = Column(Text, nullable=False)
    results_count = Column(Integer, default=0)
    search_time = Column(DateTime(timezone=True), server_default=func.now())
    use_llm = Column(Boolean, default=True)

class DzjyTrade(Base):
    """大宗交易数据模型"""
    __tablename__ = "dzjy_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_time = Column(DateTime(timezone=True), nullable=False, index=True, comment="交易时间")
    stock_code = Column(String(10), nullable=False, index=True, comment="股票代码")
    stock_name = Column(String(50), nullable=False, comment="股票名称")
    volume = Column(Float, nullable=False, comment="成交量（万股）")
    amount = Column(Float, nullable=False, comment="成交金额（万元）")
    price = Column(Float, nullable=False, comment="成交价格")
    source_raw = Column(Text, comment="原始数据来源（JSON格式）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 创建复合索引以提高查询性能
    __table_args__ = (
        Index('idx_trade_time_code', 'trade_time', 'stock_code'),
    )
