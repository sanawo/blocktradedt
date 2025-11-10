"""
大宗交易数据定时抓取调度器
每5分钟执行一次数据抓取
"""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.dzjy_scraper import dzjy_scraper, fetch_dzjy_data
from app.models import DzjyTrade
from app.config import Config

logger = logging.getLogger(__name__)


class DzjyScheduler:
    """大宗交易数据调度器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.is_running = False
        self.last_fetch_time = None
        
    def save_trades(self, trades: List[Dict[str, Any]]) -> int:
        """保存交易数据到数据库"""
        saved_count = 0
        for trade_data in trades:
            try:
                # 检查是否已存在（避免重复）
                existing = self.db.query(DzjyTrade).filter(
                    and_(
                        DzjyTrade.trade_time == trade_data['trade_time'],
                        DzjyTrade.stock_code == trade_data['stock_code']
                    )
                ).first()
                
                if existing:
                    # 更新现有记录
                    existing.volume = trade_data['volume']
                    existing.amount = trade_data['amount']
                    existing.price = trade_data['price']
                    existing.stock_name = trade_data['stock_name']
                    existing.source_raw = trade_data.get('source_raw', existing.source_raw)
                else:
                    # 创建新记录
                    trade = DzjyTrade(
                        trade_time=trade_data['trade_time'],
                        stock_code=trade_data['stock_code'],
                        stock_name=trade_data['stock_name'],
                        volume=trade_data['volume'],
                        amount=trade_data['amount'],
                        price=trade_data['price'],
                        source_raw=trade_data.get('source_raw', '')
                    )
                    self.db.add(trade)
                    saved_count += 1
                    
            except Exception as e:
                logger.error(f"保存交易数据失败: {e}, 数据: {trade_data}")
                continue
        
        try:
            self.db.commit()
            logger.info(f"✅ 成功保存 {saved_count} 条新交易记录")
        except Exception as e:
            logger.error(f"提交数据库失败: {e}")
            self.db.rollback()
        
        return saved_count
    
    def fetch_and_save(self, date: str = None) -> Dict[str, Any]:
        """抓取并保存数据"""
        try:
            logger.info(f"开始抓取大宗交易数据，日期: {date or '今天'}")
            start_time = time.time()
            
            # 抓取数据
            trades = fetch_dzjy_data(date)
            
            if not trades:
                logger.warning("⚠️ 未获取到任何数据")
                return {
                    'success': False,
                    'message': '未获取到数据',
                    'count': 0
                }
            
            # 保存到数据库
            saved_count = self.save_trades(trades)
            
            elapsed = time.time() - start_time
            self.last_fetch_time = datetime.now()
            
            result = {
                'success': True,
                'message': f'成功抓取并保存 {saved_count} 条记录',
                'count': saved_count,
                'total_fetched': len(trades),
                'elapsed_time': round(elapsed, 2)
            }
            
            logger.info(f"✅ 数据抓取完成: {result['message']}, 耗时 {elapsed:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"❌ 抓取数据失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'message': f'抓取失败: {str(e)}',
                'count': 0
            }
    
    def start_scheduler(self, interval_minutes: int = 5):
        """启动定时调度器"""
        if self.is_running:
            logger.warning("调度器已在运行中")
            return
        
        self.is_running = True
        interval_seconds = interval_minutes * 60
        
        logger.info(f"🚀 启动大宗交易数据调度器，抓取间隔: {interval_minutes}分钟")
        
        # 立即执行一次
        self.fetch_and_save()
        
        # 定时执行
        while self.is_running:
            try:
                time.sleep(interval_seconds)
                if self.is_running:
                    self.fetch_and_save()
            except KeyboardInterrupt:
                logger.info("收到停止信号，正在停止调度器...")
                self.stop()
                break
            except Exception as e:
                logger.error(f"调度器执行出错: {e}")
                # 继续运行，不中断
                continue
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        logger.info("调度器已停止")


def run_scheduler(db: Session, interval_minutes: int = 5):
    """运行调度器的便捷函数"""
    scheduler = DzjyScheduler(db)
    scheduler.start_scheduler(interval_minutes)

