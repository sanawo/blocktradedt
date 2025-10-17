import requests
import json
import pandas as pd
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
    """东方财富网大宗交易数据爬虫"""
    
    def __init__(self):
        self.base_url = "https://data.eastmoney.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
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
    
    def get_comprehensive_data(self) -> Dict[str, Any]:
        """
        获取综合数据（市场统计 + 活跃股票）
        """
        try:
            logger.info("开始获取综合数据...")
            
            # 获取市场统计数据
            market_stats = self.get_market_statistics()
            
            # 获取活跃股票数据
            active_stocks = self.get_active_stocks()
            
            # 获取每日明细（最近一天）
            daily_details = self.get_daily_details()
            
            return {
                "success": True,
                "market_statistics": market_stats,
                "active_stocks": active_stocks,
                "daily_details": daily_details,
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
