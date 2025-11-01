"""
数据缓存模块 - 用于加速数据加载
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading
import logging

logger = logging.getLogger(__name__)


class DataCache:
    """简单的内存缓存实现"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._cache_duration = {
            'dzjy_data': timedelta(minutes=5),  # 大宗交易数据缓存5分钟
            'popular_stocks': timedelta(minutes=5),  # 热门股票缓存5分钟
            'market_overview': timedelta(minutes=5),  # 市场概览缓存5分钟
            'daily_statistics': timedelta(minutes=30),  # 每日统计缓存30分钟（历史数据变化少）
            'trends_data': timedelta(minutes=2),  # 趋势数据缓存2分钟
        }
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """获取缓存数据"""
        with self._lock:
            if key not in self._cache:
                return None
            
            cache_item = self._cache[key]
            cached_time = cache_item.get('timestamp')
            duration = self._cache_duration.get(key, timedelta(minutes=5))
            
            if cached_time and datetime.now() - cached_time < duration:
                logger.debug(f"缓存命中: {key}")
                return cache_item.get('data')
            else:
                # 缓存过期，删除
                del self._cache[key]
                logger.debug(f"缓存过期: {key}")
                return None
    
    def set(self, key: str, data: Any) -> None:
        """设置缓存数据"""
        with self._lock:
            self._cache[key] = {
                'data': data,
                'timestamp': datetime.now()
            }
            logger.debug(f"缓存已设置: {key}")
    
    def clear(self, key: Optional[str] = None) -> None:
        """清除缓存"""
        with self._lock:
            if key:
                if key in self._cache:
                    del self._cache[key]
                    logger.debug(f"缓存已清除: {key}")
            else:
                self._cache.clear()
                logger.debug("所有缓存已清除")
    
    def get_or_set(self, key: str, getter_func, *args, **kwargs) -> Any:
        """获取缓存，如果不存在则调用函数获取并缓存"""
        cached_data = self.get(key)
        if cached_data is not None:
            return cached_data
        
        # 缓存未命中，调用函数获取数据
        try:
            data = getter_func(*args, **kwargs)
            if data is not None:
                self.set(key, data)
            return data
        except Exception as e:
            logger.error(f"获取数据失败 ({key}): {e}")
            # 如果获取失败，尝试返回过期缓存
            with self._lock:
                if key in self._cache:
                    logger.warning(f"使用过期缓存: {key}")
                    return self._cache[key].get('data')
            return None


# 全局缓存实例
cache = DataCache()

