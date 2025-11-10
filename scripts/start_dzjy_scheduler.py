"""
启动大宗交易数据抓取调度器
每5分钟自动抓取一次数据
"""
import sys
import os
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, DzjyTrade
from app.config import Config
from app.dzjy_scheduler import DzjyScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    try:
        # 初始化数据库
        database_url = Config.get_database_url()
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # 创建表
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表已创建/验证")
        
        # 创建数据库会话
        db = SessionLocal()
        
        # 创建调度器并启动
        scheduler = DzjyScheduler(db)
        logger.info("🚀 启动大宗交易数据抓取调度器...")
        scheduler.start_scheduler(interval_minutes=5)
        
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在退出...")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

