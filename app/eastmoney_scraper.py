import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time
import re
from bs4 import BeautifulSoup
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EastMoneyScraper:
    """东方财富网大宗交易数据爬虫 - 增强版"""
    
    def __init__(self):
        self.base_url = "https://data.eastmoney.com"
        self.api_base = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://data.eastmoney.com/',
            'Origin': 'https://data.eastmoney.com',
        })
        self.cache = {}
        self.cache_ttl = 300  # 5分钟缓存
        
    def get_market_statistics(self) -> Dict[str, Any]:
        """
        获取市场统计数据
        从 https://data.eastmoney.com/dzjy/dzjy_sctj.html 获取数据
        """
        try:
            url = f"{self.base_url}/dzjy/dzjy_sctj.html"
            logger.info(f"正在获取市场统计数据: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找市场统计表格
            market_data = self._parse_market_statistics_table(soup)
            
            return {
                "success": True,
                "data": market_data,
                "timestamp": datetime.now().isoformat(),
                "source": "东方财富网"
            }
            
        except Exception as e:
            logger.error(f"获取市场统计数据失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_market_statistics_table(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """解析市场统计表格"""
        try:
            # 查找表格
            table = soup.find('table')
            if not table:
                logger.warning("未找到市场统计表格")
                return {}
            
            # 解析表头
            headers = []
            header_row = table.find('thead')
            if header_row:
                header_cells = header_row.find_all('th')
                headers = [cell.get_text(strip=True) for cell in header_cells]
            
            # 解析数据行
            data_rows = []
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    if row_data:
                        data_rows.append(row_data)
            
            # 构建结果
            result = {
                "headers": headers,
                "data": data_rows,
                "total_records": len(data_rows)
            }
            
            # 如果有数据，解析最新记录
            if data_rows:
                latest_record = data_rows[0]  # 假设第一行是最新的
                result["latest_data"] = self._parse_latest_record(headers, latest_record)
            
            return result
            
        except Exception as e:
            logger.error(f"解析市场统计表格失败: {str(e)}")
            return {}
    
    def _parse_latest_record(self, headers: List[str], record: List[str]) -> Dict[str, Any]:
        """解析最新记录"""
        try:
            parsed_record = {}
            for i, header in enumerate(headers):
                if i < len(record):
                    value = record[i]
                    # 尝试转换为数字
                    if re.match(r'^-?\d+\.?\d*$', value.replace(',', '')):
                        try:
                            parsed_record[header] = float(value.replace(',', ''))
                        except ValueError:
                            parsed_record[header] = value
                    else:
                        parsed_record[header] = value
            
            return parsed_record
            
        except Exception as e:
            logger.error(f"解析最新记录失败: {str(e)}")
            return {}
    
    def get_daily_details(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        获取每日明细数据
        """
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            # 构建API URL (需要根据实际API调整)
            api_url = f"{self.base_url}/api/dzjy/dzjy_mx"
            params = {
                'date': date,
                'page': 1,
                'size': 100
            }
            
            logger.info(f"正在获取每日明细数据: {api_url}")
            
            response = self.session.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "data": data,
                "date": date,
                "timestamp": datetime.now().isoformat(),
                "source": "东方财富网"
            }
            
        except Exception as e:
            logger.error(f"获取每日明细数据失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_active_stocks(self) -> Dict[str, Any]:
        """
        获取活跃股票统计
        """
        try:
            url = f"{self.base_url}/dzjy/dzjy_jjgg.html"
            logger.info(f"正在获取活跃股票数据: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 解析活跃股票数据
            active_stocks = self._parse_active_stocks(soup)
            
            return {
                "success": True,
                "data": active_stocks,
                "timestamp": datetime.now().isoformat(),
                "source": "东方财富网"
            }
            
        except Exception as e:
            logger.error(f"获取活跃股票数据失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_active_stocks(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """解析活跃股票数据"""
        try:
            stocks = []
            
            # 查找股票表格
            table = soup.find('table')
            if not table:
                return stocks
            
            rows = table.find_all('tr')[1:]  # 跳过表头
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 6:
                    stock_data = {
                        'code': cells[0].get_text(strip=True),
                        'name': cells[1].get_text(strip=True),
                        'price': cells[2].get_text(strip=True),
                        'change': cells[3].get_text(strip=True),
                        'volume': cells[4].get_text(strip=True),
                        'amount': cells[5].get_text(strip=True)
                    }
                    stocks.append(stock_data)
            
            return stocks
            
        except Exception as e:
            logger.error(f"解析活跃股票数据失败: {str(e)}")
            return []
    
    def get_block_trade_details(self, date: Optional[str] = None, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """
        获取大宗交易明细数据（使用API）
        """
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            cache_key = f"block_trade_{date}_{page}"
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if (datetime.now() - cached_time).seconds < self.cache_ttl:
                    return cached_data
            
            # 尝试使用API获取数据
            params = {
                'sortColumns': 'TRADE_DATE',
                'sortTypes': '-1',
                'pageSize': str(page_size),
                'pageNumber': str(page),
                'reportName': 'RPT_BLOCKTRADE',
                'columns': 'ALL',
                'filter': f'(TRADE_DATE=\'{date}\')'
            }
            
            logger.info(f"正在获取大宗交易明细: {date}")
            response = self.session.get(self.api_base, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            result = {
                "success": True,
                "data": data.get('result', {}).get('data', []),
                "total": data.get('result', {}).get('total', 0),
                "date": date,
                "timestamp": datetime.now().isoformat(),
                "source": "东方财富网API"
            }
            
            # 更新缓存
            self.cache[cache_key] = (result, datetime.now())
            
            return result
            
        except Exception as e:
            logger.error(f"获取大宗交易明细失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_recent_block_trades(self, days: int = 7) -> Dict[str, Any]:
        """
        获取最近N天的大宗交易数据
        """
        try:
            all_trades = []
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                result = self.get_block_trade_details(date, page=1, page_size=100)
                if result.get('success') and result.get('data'):
                    all_trades.extend(result['data'])
            
            return {
                "success": True,
                "data": all_trades,
                "total": len(all_trades),
                "period_days": days,
                "timestamp": datetime.now().isoformat(),
                "source": "东方财富网API"
            }
            
        except Exception as e:
            logger.error(f"获取最近大宗交易数据失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_hot_stocks(self, days: int = 7) -> Dict[str, Any]:
        """
        获取热门股票（最近N天大宗交易最多的股票）
        """
        try:
            recent_trades = self.get_recent_block_trades(days)
            if not recent_trades.get('success'):
                return recent_trades
            
            # 统计股票交易次数
            stock_count = {}
            for trade in recent_trades.get('data', []):
                stock_code = trade.get('SECURITY_CODE', '')
                stock_name = trade.get('SECURITY_NAME', '')
                key = f"{stock_code}_{stock_name}"
                
                if key not in stock_count:
                    stock_count[key] = {
                        'code': stock_code,
                        'name': stock_name,
                        'count': 0,
                        'total_amount': 0
                    }
                
                stock_count[key]['count'] += 1
                # 累加交易金额
                try:
                    amount = float(trade.get('TRADE_PRICE', 0)) * float(trade.get('TRADE_VOL', 0))
                    stock_count[key]['total_amount'] += amount
                except:
                    pass
            
            # 排序
            hot_stocks = sorted(stock_count.values(), key=lambda x: x['count'], reverse=True)[:20]
            
            return {
                "success": True,
                "data": hot_stocks,
                "period_days": days,
                "timestamp": datetime.now().isoformat(),
                "source": "东方财富网API"
            }
            
        except Exception as e:
            logger.error(f"获取热门股票失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_comprehensive_data(self) -> Dict[str, Any]:
        """
        获取综合数据（市场统计 + 活跃股票 + 最近交易 + 热门股票）
        """
        try:
            logger.info("开始获取综合数据...")
            
            # 获取市场统计数据
            market_stats = self.get_market_statistics()
            
            # 获取活跃股票数据
            active_stocks = self.get_active_stocks()
            
            # 获取每日明细（最近一天）
            daily_details = self.get_daily_details()
            
            # 获取最近7天的大宗交易
            recent_trades = self.get_recent_block_trades(days=7)
            
            # 获取热门股票
            hot_stocks = self.get_hot_stocks(days=7)
            
            return {
                "success": True,
                "market_statistics": market_stats,
                "active_stocks": active_stocks,
                "daily_details": daily_details,
                "recent_trades": recent_trades,
                "hot_stocks": hot_stocks,
                "timestamp": datetime.now().isoformat(),
                "source": "东方财富网"
            }
            
        except Exception as e:
            logger.error(f"获取综合数据失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def format_data_for_frontend(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化数据供前端使用
        """
        try:
            if not data.get("success"):
                return data
            
            formatted_data = {
                "market_overview": {
                    "shanghai_index": 3666.44,  # 模拟数据
                    "shanghai_change": -0.46,
                    "total_volume": 4567.89,
                    "premium_volume": 234.56,
                    "discount_volume": 4333.33
                },
                "hot_stocks": [],
                "market_trends": [],
                "news_summary": "基于东方财富网实时数据的大宗交易市场分析"
            }
            
            # 处理市场统计数据
            if "market_statistics" in data and data["market_statistics"].get("success"):
                market_stats = data["market_statistics"]["data"]
                if "latest_data" in market_stats:
                    latest = market_stats["latest_data"]
                    formatted_data["market_overview"].update({
                        "shanghai_index": latest.get("上证指数", 3666.44),
                        "shanghai_change": latest.get("上证指数涨跌幅(%)", -0.46),
                        "total_volume": latest.get("大宗交易成交总额(万)", 4567.89),
                        "premium_volume": latest.get("溢价成交总额(万)", 234.56),
                        "discount_volume": latest.get("折价成交总额(万)", 4333.33)
                    })
            
            # 处理活跃股票数据
            if "active_stocks" in data and data["active_stocks"].get("success"):
                stocks = data["active_stocks"]["data"]
                formatted_data["hot_stocks"] = stocks[:10]  # 取前10只
            
            return {
                "success": True,
                "data": formatted_data,
                "timestamp": datetime.now().isoformat(),
                "source": "东方财富网"
            }
            
        except Exception as e:
            logger.error(f"格式化数据失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 创建全局实例
eastmoney_scraper = EastMoneyScraper()

def get_eastmoney_data():
    """获取东方财富网数据的便捷函数"""
    return eastmoney_scraper.get_comprehensive_data()

def format_eastmoney_data():
    """格式化东方财富网数据的便捷函数"""
    raw_data = get_eastmoney_data()
    return eastmoney_scraper.format_data_for_frontend(raw_data)
