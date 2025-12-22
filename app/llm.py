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
        
        # 初始化智谱AI客户端
        if self.api_key:
            try:
                from zhipuai import ZhipuAI
                self.client = ZhipuAI(api_key=self.api_key)
                print("✅ 智谱AI客户端初始化成功")
            except ImportError:
                print("⚠️  zhipuai包未安装，AI功能将不可用")
            except Exception as e:
                print(f"❌ 智谱AI初始化失败: {e}")
    
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

    def summarize_report(self, report_text: str) -> Optional[Dict[str, Any]]:
        """
        使用AI生成研报摘要
        
        Args:
            report_text: 研报文本内容
            
        Returns:
            结构化摘要字典，如果失败则返回None
        """
        if not self.client:
            return None
        
        try:
            # 限制文本长度
            if len(report_text) > 5000:
                report_text = report_text[:5000] + "..."
            
            prompt = f"""请分析以下行业研报，并提取以下结构化信息：

1. 标题：提取研报标题
2. 核心观点：提取3-5条主要观点和建议
3. 数据支撑：提取关键数据和数字（百分比、数量、价格等）
4. 趋势判断：提取市场趋势预测和判断
5. 关键发现：提取重要发现和创新点
6. 风险分析：提取风险提示和预警信息
7. 投资建议：提取投资建议和操作指引

研报内容：
{report_text}

请以JSON格式返回，格式如下：
{{
    "title": "标题",
    "core_viewpoints": ["观点1", "观点2", ...],
    "data_support": [{{"value": "数值", "type": "类型"}}, ...],
    "trend_judgment": "趋势判断文本",
    "key_findings": ["发现1", "发现2", ...],
    "risk_analysis": ["风险1", "风险2", ...],
    "recommendations": ["建议1", "建议2", ...],
    "confidence": 0.85
}}"""

            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的金融分析师，擅长分析行业研报并提取结构化信息。请用中文回答，返回JSON格式。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # 解析JSON响应
            import json
            import re
            
            content = response.choices[0].message.content
            
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                return result
            else:
                # 如果无法解析JSON，返回None，让系统使用本地方法
                return None
                
        except Exception as e:
            print(f"AI研报摘要生成失败: {e}")
            return None



