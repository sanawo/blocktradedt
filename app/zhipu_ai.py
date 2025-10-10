import requests
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class ZhipuAI:
    """智谱AI API集成类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化智谱AI客户端
        
        Args:
            api_key: 智谱AI API密钥，如果不提供则从环境变量获取
        """
        self.api_key = api_key or os.getenv('ZHIPU_API_KEY', '')
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.model = "glm-4.5"
        
    def call_api(self, messages: List[Dict[str, str]], 
                 temperature: float = 0.6, 
                 max_tokens: int = 1024,
                 stream: bool = False) -> Dict[str, Any]:
        """
        调用智谱AI API
        
        Args:
            messages: 对话消息列表
            temperature: 温度参数，控制回答的随机性
            max_tokens: 最大token数
            stream: 是否使用流式响应
            
        Returns:
            API响应结果
        """
        if not self.api_key:
            raise ValueError("API Key未设置，请设置ZHIPU_API_KEY环境变量或传入api_key参数")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                # 检查响应格式
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    print(f"API返回内容: {content}")  # 调试信息
                    return content
                else:
                    print(f"API响应格式异常: {result}")  # 调试信息
                    raise Exception("API响应格式异常")
            elif response.status_code == 401:
                raise Exception("API Key无效或已过期")
            elif response.status_code == 429:
                raise Exception("请求过于频繁，请稍后重试")
            elif response.status_code == 500:
                raise Exception("服务器内部错误，请稍后重试")
            else:
                raise Exception(f"API调用失败: {response.status_code}, {response.text}")
                
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请检查网络连接")
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求错误: {str(e)}")
        except Exception as e:
            print(f"API调用异常: {str(e)}")  # 调试信息
            raise Exception(f"API调用异常: {str(e)}")
    
    def chat(self, user_message: str, 
             system_prompt: str = "你是一个专业的金融分析师，专门分析大宗交易数据。请用中文回答，语言要专业、准确。请始终使用中文回复，不要使用英文。",
             conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        进行对话
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示词
            conversation_history: 对话历史
            
        Returns:
            AI回复内容
        """
        messages = []
        
        # 添加系统提示词
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)
        
        # 添加用户当前消息
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            result = self.call_api(messages)
            if isinstance(result, str):
                return result
            elif isinstance(result, dict) and 'choices' in result:
                return result['choices'][0]['message']['content']
            else:
                return f"抱歉，AI服务响应格式异常: {str(result)}"
        except Exception as e:
            return f"抱歉，AI服务暂时不可用: {str(e)}"
    
    def analyze_market_data(self, market_data: Dict[str, Any]) -> str:
        """
        分析市场数据
        
        Args:
            market_data: 市场数据字典
            
        Returns:
            分析结果
        """
        system_prompt = """你是一个专业的金融分析师，专门分析大宗交易市场数据。
请根据提供的数据进行专业分析，包括：
1. 市场趋势分析
2. 成交量分析
3. 溢价/折价情况分析
4. 投资建议
请用专业、准确的语言回答，并给出具体的数字支持。"""
        
        user_message = f"""请分析以下大宗交易市场数据：
上证指数: {market_data.get('shanghai_index', 'N/A')}
涨跌幅: {market_data.get('shanghai_change', 'N/A')}%
总成交额: {market_data.get('total_volume', 'N/A')}万
溢价成交: {market_data.get('premium_volume', 'N/A')}万
折价成交: {market_data.get('discount_volume', 'N/A')}万

请提供详细的市场分析。"""
        
        return self.chat(user_message, system_prompt)
    
    def get_investment_advice(self, query: str) -> str:
        """
        获取投资建议
        
        Args:
            query: 用户查询
            
        Returns:
            投资建议
        """
        system_prompt = """你是一个专业的投资顾问，专门为大宗交易投资者提供建议。
请注意：
1. 提供客观、专业的分析
2. 基于数据给出建议
3. 提醒投资风险
4. 不提供具体的投资建议，只提供分析参考"""
        
        return self.chat(query, system_prompt)

# 创建全局实例
zhipu_ai = ZhipuAI()
