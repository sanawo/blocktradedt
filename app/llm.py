from __future__ import annotations
from typing import List, Dict, Any, Optional
import os

class LLM:
    """LLM类，支持GLM-4.5-Flash和本地摘要功能"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "glm-4.5-flash"):
        """
        初始化LLM
        
        Args:
            api_key: 智谱AI API密钥，如果不提供则使用环境变量
            model: 使用的模型，默认为glm-4.5-flash
        """
        self.api_key = api_key or os.getenv('ZHIPU_API_KEY')
        self.model = model
        self.client = None
        self.use_old_sdk = False
        
        # 尝试初始化智谱AI客户端
        if self.api_key:
            try:
                from zai import ZhipuAiClient
                self.client = ZhipuAiClient(api_key=self.api_key)
                self.use_old_sdk = False
            except ImportError:
                # 如果zai-sdk未安装，尝试旧版SDK
                try:
                    import zhipuai
                    self.client = zhipuai.ZhipuAI(api_key=self.api_key)
                    self.use_old_sdk = True
                except ImportError:
                    self.client = None
                    self.use_old_sdk = False
            except Exception as e:
                print(f"初始化AI客户端失败: {e}")
                self.client = None
                self.use_old_sdk = False
        else:
            self.client = None
            self.use_old_sdk = False
    
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
        """使用GLM-4.5-Flash生成摘要"""
        # 构建上下文信息
        context = self._build_context(query, results)
        
        try:
            # 检查是否使用新SDK
            if not self.use_old_sdk and hasattr(self.client, 'chat') and hasattr(self.client.chat, 'completions'):
                # 新SDK (zai-sdk) - GLM-4.5-Flash
                response = self.client.chat.completions.create(
                    model=self.model,  # 使用glm-4.5-flash
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
                    thinking={"type": "disabled"},  # 摘要生成禁用思考模式以提高速度
                    temperature=0.7,
                    max_tokens=500
                )
                
                # 处理响应（可能是流式或非流式）
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    return response.choices[0].message.content
                else:
                    # 流式响应处理
                    content = ""
                    for chunk in response:
                        if hasattr(chunk, 'choices') and chunk.choices[0].delta.content:
                            content += chunk.choices[0].delta.content
                    return content
            else:
                # 旧SDK兼容 (zhipuai)
                response = self.client.chat.completions.create(
                    model="glm-4-flash",
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个专业的大宗交易数据分析助手。"
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
        except Exception as e:
            print(f"AI摘要生成失败: {e}")
            import traceback
            print(traceback.format_exc())
            raise
    
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
    
    def chat(self, message: str, context: Optional[str] = None, system_prompt: Optional[str] = None, 
             enable_thinking: bool = True, stream: bool = False) -> str:
        """
        AI助手对话功能 - 支持GLM-4.5-Flash
        
        Args:
            message: 用户消息
            context: 可选的上下文信息
            system_prompt: 可选的系统提示词
            enable_thinking: 是否启用深度思考模式（默认True）
            stream: 是否使用流式输出（默认False）
            
        Returns:
            AI回复
        """
        if not self.client:
            return "AI助手暂时不可用，请检查API密钥配置。请设置环境变量ZHIPU_API_KEY或提供API密钥。"
        
        try:
            # 使用自定义system_prompt或默认提示词
            default_system_prompt = "你是一个专业的大宗交易数据分析助手。你可以帮助用户理解市场趋势、分析交易数据、回答相关问题。请用专业、友好的语气回答，始终使用中文。"
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
            
            # 判断任务复杂度，决定是否启用思考模式
            simple_keywords = ['你好', 'hello', '谢谢', '再见']
            complex_keywords = ['分析', '预测', '解释', '为什么', '如何', '建议', '策略']
            
            is_simple = any(kw in message.lower() for kw in simple_keywords)
            is_complex = any(kw in message.lower() for kw in complex_keywords)
            
            # 设置思考模式
            if enable_thinking:
                thinking_type = "enabled" if is_complex else "disabled"
            else:
                thinking_type = "disabled"
            
            # 检查是否使用新SDK (zai-sdk)
            if not self.use_old_sdk and hasattr(self.client, 'chat') and hasattr(self.client.chat, 'completions'):
                # 使用GLM-4.5-Flash (新SDK)
                call_kwargs = {
                    "model": self.model,  # glm-4.5-flash
                    "messages": messages,
                    "thinking": {"type": thinking_type},
                    "temperature": 0.7,
                    "max_tokens": 4096
                }
                
                if stream:
                    call_kwargs["stream"] = True
                    # 流式输出
                    response = self.client.chat.completions.create(**call_kwargs)
                    content = ""
                    for chunk in response:
                        if hasattr(chunk, 'choices') and chunk.choices[0].delta.content:
                            content += chunk.choices[0].delta.content
                    return content
                else:
                    # 非流式输出
                    response = self.client.chat.completions.create(**call_kwargs)
                    if hasattr(response, 'choices') and len(response.choices) > 0:
                        return response.choices[0].message.content
                    else:
                        return "抱歉，未收到有效回复。"
            else:
                # 旧SDK兼容 (zhipuai)
                response = self.client.chat.completions.create(
                    model="glm-4-flash",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].message.content
                
        except Exception as e:
            print(f"AI chat failed: {e}")
            import traceback
            print(traceback.format_exc())
            return f"抱歉，AI助手遇到了问题：{str(e)}。请检查API密钥是否正确配置。"



