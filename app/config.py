import os
from typing import Optional

class Config:
    """应用配置类"""
    
    # 数据库配置 - 优先使用环境变量
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'block-trade-dt-super-secret-key-2024')
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # 东方财富网配置
    EASTMONEY_BASE_URL = "https://data.eastmoney.com"
    EASTMONEY_TIMEOUT = 30
    
    # 服务器配置
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8001))
    RELOAD = os.getenv('RELOAD', 'False').lower() == 'true'
    
    @classmethod
    def get_jwt_secret_key(cls) -> str:
        """获取JWT密钥"""
        return cls.JWT_SECRET_KEY
    
    @classmethod
    def get_database_url(cls) -> str:
        """获取数据库URL"""
        return cls.DATABASE_URL
    
    @classmethod
    def get_eastmoney_config(cls) -> dict:
        """获取东方财富网配置"""
        return {
            "base_url": cls.EASTMONEY_BASE_URL,
            "timeout": cls.EASTMONEY_TIMEOUT
        }



