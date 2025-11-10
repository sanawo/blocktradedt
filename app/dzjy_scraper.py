"""
同花顺大宗交易数据抓取脚本
支持JSON接口和Playwright两种方式
包含重试、限速、错误告警功能
"""
import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
import asyncio
from bs4 import BeautifulSoup

# 尝试导入Playwright（可选）
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright未安装，将仅使用requests方式抓取")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DzjyScraper:
    """大宗交易数据抓取器"""
    
    def __init__(self):
        self.base_url = "https://data.10jqka.com.cn"
        self.dzjy_url = "https://data.10jqka.com.cn/market/dzjy/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://data.10jqka.com.cn/',
            'Origin': 'https://data.10jqka.com.cn',
        })
        
        # 限速配置
        self.min_request_interval = 1.0  # 最小请求间隔（秒）
        self.last_request_time = 0
        
        # 重试配置
        self.max_retries = 3
        self.retry_delay = 2  # 重试延迟（秒）
        
        # 错误告警配置
        self.error_count = 0
        self.max_errors = 5  # 连续错误次数阈值
        
    def _rate_limit(self):
        """限速：确保请求间隔"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _send_alert(self, message: str):
        """发送错误告警（可以扩展为邮件、短信等）"""
        logger.error(f"🚨 告警: {message}")
        # TODO: 实现实际的告警机制（邮件、短信、Webhook等）
    
    def _retry_request(self, func, *args, **kwargs):
        """带重试的请求包装器"""
        last_error = None
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                result = func(*args, **kwargs)
                self.error_count = 0  # 成功则重置错误计数
                return result
            except Exception as e:
                last_error = e
                self.error_count += 1
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    logger.warning(f"请求失败（尝试 {attempt + 1}/{self.max_retries}）: {e}，{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"请求失败，已重试{self.max_retries}次: {e}")
        
        # 连续错误过多时发送告警
        if self.error_count >= self.max_errors:
            self._send_alert(f"连续{self.error_count}次抓取失败，请检查网络或目标网站状态")
            self.error_count = 0  # 重置计数
        
        raise last_error
    
    def find_json_api(self) -> Optional[str]:
        """
        尝试查找JSON API接口
        通过分析常见的数据接口模式来查找
        """
        possible_apis = [
            "https://data.10jqka.com.cn/ajax/dzjy/",
            "https://data.10jqka.com.cn/api/dzjy/list",
            "https://data.10jqka.com.cn/market/dzjy/ajax",
            "https://data.10jqka.com.cn/ifmarket/dzjy/list",
        ]
        
        for api_url in possible_apis:
            try:
                self._rate_limit()
                response = self.session.get(api_url, timeout=10)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict) and ('data' in data or 'list' in data):
                            logger.info(f"✅ 找到JSON API: {api_url}")
                            return api_url
                    except json.JSONDecodeError:
                        continue
            except Exception as e:
                logger.debug(f"尝试API {api_url} 失败: {e}")
                continue
        
        logger.info("⚠️ 未找到JSON API，将使用Playwright方式")
        return None
    
    def fetch_via_json_api(self, api_url: str, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """通过JSON API获取数据"""
        try:
            params = {}
            if date:
                params['date'] = date
            
            response = self._retry_request(
                self.session.get,
                api_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # 解析不同可能的JSON结构
            if isinstance(data, dict):
                records = data.get('data', data.get('list', data.get('records', [])))
            elif isinstance(data, list):
                records = data
            else:
                records = []
            
            return self._parse_json_records(records)
            
        except Exception as e:
            logger.error(f"JSON API获取数据失败: {e}")
            return []
    
    def _parse_json_records(self, records: List[Dict]) -> List[Dict[str, Any]]:
        """解析JSON记录"""
        parsed = []
        for record in records:
            try:
                # 尝试多种可能的字段名
                trade_time_str = record.get('trade_time') or record.get('date') or record.get('time')
                stock_code = record.get('stock_code') or record.get('code') or record.get('stockCode')
                stock_name = record.get('stock_name') or record.get('name') or record.get('stockName')
                volume = float(record.get('volume', 0))
                amount = float(record.get('amount', 0))
                price = float(record.get('price') or record.get('trade_price') or 0)
                
                # 解析交易时间
                if isinstance(trade_time_str, str):
                    try:
                        trade_time = datetime.strptime(trade_time_str, '%Y-%m-%d %H:%M:%S')
                    except:
                        try:
                            trade_time = datetime.strptime(trade_time_str, '%Y-%m-%d')
                        except:
                            trade_time = datetime.now()
                else:
                    trade_time = datetime.now()
                
                parsed.append({
                    'trade_time': trade_time,
                    'stock_code': str(stock_code),
                    'stock_name': str(stock_name),
                    'volume': volume,
                    'amount': amount,
                    'price': price,
                    'source_raw': json.dumps(record, ensure_ascii=False)
                })
            except Exception as e:
                logger.warning(f"解析记录失败: {e}, 记录: {record}")
                continue
        
        return parsed
    
    async def fetch_via_playwright(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """使用Playwright抓取渲染后的数据"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright未安装，无法使用此方式")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # 访问页面
                url = self.dzjy_url
                if date:
                    url += f"?date={date}"
                
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # 等待表格加载
                await page.wait_for_selector('table', timeout=10000)
                
                # 提取数据
                data = await page.evaluate('''() => {
                    const rows = Array.from(document.querySelectorAll('table tbody tr'));
                    return rows.map(row => {
                        const cells = Array.from(row.querySelectorAll('td'));
                        if (cells.length < 5) return null;
                        
                        return {
                            date: cells[0]?.textContent?.trim() || '',
                            code: cells[1]?.textContent?.trim() || '',
                            name: cells[2]?.textContent?.trim() || '',
                            close_price: cells[3]?.textContent?.trim() || '',
                            trade_price: cells[4]?.textContent?.trim() || '',
                            volume: cells[5]?.textContent?.trim() || '',
                            discount_rate: cells[6]?.textContent?.trim() || '',
                            amount: cells[7]?.textContent?.trim() || '',
                            buy_broker: cells[8]?.textContent?.trim() || '',
                            sell_broker: cells[9]?.textContent?.trim() || ''
                        };
                    }).filter(item => item && item.code);
                }''')
                
                await browser.close()
                
                return self._parse_playwright_data(data)
                
        except Exception as e:
            logger.error(f"Playwright抓取失败: {e}")
            return []
    
    def _parse_playwright_data(self, data: List[Dict]) -> List[Dict[str, Any]]:
        """解析Playwright抓取的数据"""
        parsed = []
        for item in data:
            try:
                # 解析日期
                date_str = item.get('date', '')
                try:
                    trade_time = datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    trade_time = datetime.now()
                
                # 解析价格和数量
                try:
                    price = float(item.get('trade_price', '0').replace(',', ''))
                    volume = float(item.get('volume', '0').replace(',', '').replace('万股', '').replace('万', ''))
                    amount = float(item.get('amount', '0').replace(',', '').replace('万元', '').replace('万', ''))
                except:
                    price = 0.0
                    volume = 0.0
                    amount = 0.0
                
                parsed.append({
                    'trade_time': trade_time,
                    'stock_code': item.get('code', ''),
                    'stock_name': item.get('name', ''),
                    'volume': volume,
                    'amount': amount,
                    'price': price,
                    'source_raw': json.dumps(item, ensure_ascii=False)
                })
            except Exception as e:
                logger.warning(f"解析Playwright数据失败: {e}")
                continue
        
        return parsed
    
    def fetch_via_html(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """直接解析HTML页面获取数据"""
        try:
            url = self.dzjy_url
            if date:
                url += f"?date={date}"
            
            response = self._retry_request(
                self.session.get,
                url,
                timeout=30
            )
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找表格
            tables = soup.find_all('table')
            if not tables:
                logger.warning("未找到表格")
                return []
            
            # 查找包含数据的表格（通常tbody中有多行数据）
            data_list = []
            for table in tables:
                tbody = table.find('tbody')
                if not tbody:
                    continue
                
                rows = tbody.find_all('tr')
                if len(rows) < 2:  # 至少要有数据行
                    continue
                
                # 解析每一行
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) < 8:  # 至少需要8列数据
                        continue
                    
                    try:
                        # 解析日期
                        date_str = cells[1].get_text(strip=True)  # 第2列是日期
                        try:
                            trade_time = datetime.strptime(date_str, '%Y-%m-%d')
                        except:
                            trade_time = datetime.now()
                        
                        # 解析股票代码和名称（第3列和第4列）
                        code_link = cells[2].find('a')
                        name_link = cells[3].find('a')
                        stock_code = code_link.get_text(strip=True) if code_link else cells[2].get_text(strip=True)
                        stock_name = name_link.get_text(strip=True) if name_link else cells[3].get_text(strip=True)
                        
                        # 解析价格（第5列和第6列：收盘价和成交价）
                        close_price_str = cells[4].get_text(strip=True)
                        trade_price_str = cells[5].get_text(strip=True)
                        close_price = float(close_price_str.replace(',', '')) if close_price_str else 0.0
                        trade_price = float(trade_price_str.replace(',', '')) if trade_price_str else 0.0
                        
                        # 解析成交量（第7列，单位：万股）
                        volume_str = cells[6].get_text(strip=True).replace(',', '').replace('万股', '').replace('万', '')
                        volume = float(volume_str) if volume_str else 0.0
                        
                        # 解析折价率（第8列）
                        discount_str = cells[7].get_text(strip=True).replace('%', '').replace(',', '')
                        discount_rate = float(discount_str) if discount_str else 0.0
                        
                        # 计算成交金额（成交价 * 成交量）
                        amount = trade_price * volume if trade_price and volume else 0.0
                        
                        # 解析营业部（第9列和第10列）
                        buy_broker = cells[8].get_text(strip=True) if len(cells) > 8 else ''
                        sell_broker = cells[9].get_text(strip=True) if len(cells) > 9 else ''
                        
                        # 构建记录
                        record = {
                            'trade_time': trade_time,
                            'stock_code': stock_code,
                            'stock_name': stock_name,
                            'volume': volume,
                            'amount': amount,
                            'price': trade_price,
                            'close_price': close_price,
                            'discount_rate': discount_rate,
                            'buy_broker': buy_broker,
                            'sell_broker': sell_broker,
                            'source_raw': json.dumps({
                                'date': date_str,
                                'code': stock_code,
                                'name': stock_name,
                                'close_price': close_price_str,
                                'trade_price': trade_price_str,
                                'volume': volume_str,
                                'discount_rate': discount_str,
                                'buy_broker': buy_broker,
                                'sell_broker': sell_broker
                            }, ensure_ascii=False)
                        }
                        
                        data_list.append(record)
                        
                    except Exception as e:
                        logger.warning(f"解析表格行失败: {e}")
                        continue
                
                # 如果找到数据，就使用这个表格
                if data_list:
                    break
            
            if data_list:
                logger.info(f"✅ 通过HTML解析获取到 {len(data_list)} 条记录")
            else:
                logger.warning("⚠️ HTML解析未找到数据")
            
            return data_list
            
        except Exception as e:
            logger.error(f"HTML解析失败: {e}")
            return []
    
    def fetch_data(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        主要的数据获取方法
        优先使用HTML解析（最快），然后尝试JSON API，最后使用Playwright
        """
        # 1. 优先使用HTML解析（最快且不需要额外依赖）
        try:
            logger.info("尝试使用HTML解析抓取数据...")
            data = self.fetch_via_html(date)
            if data:
                logger.info(f"✅ 通过HTML解析获取到 {len(data)} 条记录")
                return data
        except Exception as e:
            logger.warning(f"HTML解析失败: {e}")
        
        # 2. 尝试查找JSON API
        api_url = self.find_json_api()
        if api_url:
            data = self.fetch_via_json_api(api_url, date)
            if data:
                logger.info(f"✅ 通过JSON API获取到 {len(data)} 条记录")
                return data
        
        # 3. 如果JSON API不可用，尝试使用Playwright
        if PLAYWRIGHT_AVAILABLE:
            try:
                logger.info("尝试使用Playwright抓取数据...")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                data = loop.run_until_complete(self.fetch_via_playwright(date))
                loop.close()
                
                if data:
                    logger.info(f"✅ 通过Playwright获取到 {len(data)} 条记录")
                    return data
            except Exception as e:
                logger.warning(f"Playwright抓取失败: {e}")
        
        # 4. 如果都失败，返回空列表
        logger.warning("⚠️ 所有抓取方式都失败，返回空数据")
        return []


# 创建全局实例
dzjy_scraper = DzjyScraper()

def fetch_dzjy_data(date: Optional[str] = None) -> List[Dict[str, Any]]:
    """便捷函数：获取大宗交易数据"""
    return dzjy_scraper.fetch_data(date)

