from __future__ import annotations
from typing import List, Dict, Any, Optional
import os

class LLM:
    """LLM类，支持智谱AI和本地摘要功能"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化LLM
        
        Args:
            api_key: 智谱AI API密钥，如果不提供则使用环境变量或本地模式
        """
        self.api_key = api_key or os.getenv('ZHIPU_API_KEY')
        self.client = None
        
        # Disabled to fix deployment issues
        self.client = None
    
    def generate_summary(self, query: str, results: List[Dict[str, Any]]) -> str:
        """生成搜索结果摘要"""
        if not results:
            return f"未找到与'{query}'相关的记录。"
        
        # 如果有智谱AI客户端，使用AI生成摘要
        if self.client:
            try:
                return self._generate_ai_summary(query, results)
            except Exception as e:
                print(f"AI summary failed, falling back to local: {e}")
                return self._generate_local_summary(query, results)
        else:
            return self._generate_local_summary(query, results)
    
    def _generate_local_summary(self, query: str, results: List[Dict[str, Any]]) -> str:
        """生成本地摘要"""
        parts = []
        for r in results[:5]:  # 只取前5个结果
            l = r["listing"]
            title = l.get("title", "")
            region = l.get("region", "")
            price = l.get("price")
            unit = l.get("unit", "")
            
            if price is not None:
                parts.append(f"{title}（{region}，{price}{unit}）")
            else:
                parts.append(f"{title}（{region}）")
        
        if not parts:
            return f"未找到与'{query}'相关的记录。"
        
        summary = "；".join(parts)
        return f"为您找到以下相关记录：{summary}。这些数据来源于大宗交易市场，仅供参考。"
    
    def _generate_ai_summary(self, query: str, results: List[Dict[str, Any]]) -> str:
        """使用智谱AI生成摘要"""
        # 构建上下文信息
        context = self._build_context(query, results)
        
        # 调用智谱AI
        response = self.client.chat.completions.create(
            model="glm-4-flash",  # 使用快速模型
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的大宗交易数据分析助手。请根据用户的查询和搜索结果，生成简洁、专业的摘要。摘要应该突出关键信息，如价格趋势、地区分布、交易量等。"
                },
                {
                    "role": "user",
                    "content": f"用户查询：{query}\n\n搜索结果：\n{context}\n\n请生成一个简洁的摘要（100字以内）。"
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def _build_context(self, query: str, results: List[Dict[str, Any]]) -> str:
        """构建上下文信息"""
        context_parts = []
        for i, r in enumerate(results[:5], 1):
            l = r["listing"]
            title = l.get("title", "")
            region = l.get("region", "")
            price = l.get("price")
            unit = l.get("unit", "")
            category = l.get("category", "")
            description = l.get("description", "")
            
            part = f"{i}. {title}"
            if category:
                part += f" | 类别：{category}"
            if region:
                part += f" | 地区：{region}"
            if price is not None:
                part += f" | 价格：{price}{unit}"
            if description:
                part += f" | 描述：{description[:100]}"
            
            context_parts.append(part)
        
        return "\n".join(context_parts)
    
    def chat(self, message: str, context: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
        """
        AI助手对话功能
        
        Args:
            message: 用户消息
            context: 可选的上下文信息
            system_prompt: 可选的系统提示词，如果提供则使用此提示词替代默认提示词
            
        Returns:
            AI回复
        """
        if not self.client:
            return "AI助手暂时不可用，请检查API密钥配置。"
        
        try:
            # 使用自定义system_prompt或默认提示词
            default_system_prompt = "你是一个专业的大宗交易数据分析助手。你可以帮助用户理解市场趋势、分析交易数据、回答相关问题。请用专业、友好的语气回答。"
            messages = [
                {
                    "role": "system",
                    "content": system_prompt if system_prompt else default_system_prompt
                }
            ]
            
            # 如果有上下文，添加到消息中
            if context:
                messages.append({
                    "role": "system",
                    "content": f"当前上下文信息：\n{context}"
                })
            
            messages.append({
                "role": "user",
                "content": message
            })
            
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI chat failed: {e}")
            return f"抱歉，AI助手遇到了问题：{str(e)}"



