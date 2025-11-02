from __future__ import annotations
from typing import List, Dict, Any, Optional
import os
import logging
import json

# 设置日志
logger = logging.getLogger(__name__)

class LLM:
    """LLM类，支持智谱AI和本地摘要功能"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "glm-4.5-flash"):
        """
        初始化LLM
        
        Args:
            api_key: 智谱AI API密钥，如果不提供则使用环境变量
            model: 使用的模型，默认为glm-4.5-flash
        """
        # 获取API密钥
        self.api_key = api_key or os.getenv('ZHIPU_API_KEY')
        self.model = model
        self.client = None
        self.use_old_sdk = False
        self.init_error = None
        
        # 记录初始化信息
        if self.api_key:
            logger.info(f"检测到API密钥，长度: {len(self.api_key)}")
            # 尝试初始化智谱AI客户端
            try:
                # 使用官方zhipuai SDK
                import zhipuai
                logger.info("正在初始化智谱AI客户端...")
                self.client = zhipuai.ZhipuAI(api_key=self.api_key)
                logger.info("✅ 智谱AI客户端初始化成功")
                self.use_old_sdk = False
            except ImportError:
                # SDK未安装
                error_msg = "zhipuai SDK未安装，AI功能将不可用。请运行: pip install zhipuai"
                logger.error(error_msg)
                self.init_error = error_msg
                self.client = None
                self.use_old_sdk = False
            except Exception as e:
                error_msg = f"初始化AI客户端失败: {str(e)}"
                logger.error(error_msg)
                import traceback
                logger.error(traceback.format_exc())
                self.init_error = error_msg
                self.client = None
                self.use_old_sdk = False
        else:
            logger.warning("未检测到ZHIPU_API_KEY环境变量，AI功能将使用本地回复模式")
            self.init_error = "未配置API密钥"
    
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
        
        try:
            # 选择模型（根据文档使用glm-4-flash或glm-4.6）
            if "4.5" in self.model.lower() or "4.6" in self.model.lower():
                model_name = "glm-4-flash"
            elif "glm-4" in self.model.lower():
                model_name = "glm-4-flash"
            else:
                model_name = self.model
            
            # 使用官方zhipuai SDK（根据文档标准格式）
            response = self.client.chat.completions.create(
                model=model_name,
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
                max_tokens=500,
                stream=False  # 明确指定非流式
            )
            
            # 处理响应（根据文档：response.choices[0].message.content）
            if hasattr(response, 'choices') and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    content = choice.message.content
                    if content:
                        return content
            logger.warning(f"摘要生成响应格式异常: {type(response)}")
            return "摘要生成失败，请稍后重试。"
                
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
             stream: bool = False) -> str:
        """
        AI助手对话功能 - 使用智谱AI SDK
        
        Args:
            message: 用户消息
            context: 可选的上下文信息
            system_prompt: 可选的系统提示词
            stream: 是否使用流式输出（默认False）
            
        Returns:
            AI回复
        """
        if not self.client:
            error_info = self.init_error or "未知错误"
            return f"""❌ AI功能当前不可用

原因：{error_info}

解决方法：
1. 检查环境变量ZHIPU_API_KEY是否正确配置
2. 确认已安装zhipuai SDK：pip install zhipuai
3. 在Zeabur平台的环境变量中添加：ZHIPU_API_KEY=your_api_key
4. 重新部署应用以加载环境变量
5. 获取API密钥：访问 https://open.bigmodel.cn/

当前状态：AI功能已启用本地回复模式，可以提供基础帮助。

调试信息：
- API密钥存在：{'是' if self.api_key else '否'}
- 密钥长度：{len(self.api_key) if self.api_key else 0}
- 初始化错误：{error_info}"""
        
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
            
            # 使用官方zhipuai SDK
            # 模型映射：根据文档，支持glm-4.6, glm-4-flash等
            # 如果指定glm-4.5-flash，使用glm-4-flash（兼容模型）
            if "4.5" in self.model.lower() or "4.6" in self.model.lower():
                model_name = "glm-4-flash"  # 使用兼容的免费模型
            elif "glm-4" in self.model.lower():
                model_name = "glm-4-flash"  # 默认使用flash版本
            else:
                model_name = self.model
            
            try:
                # 尝试使用流式输出（如果支持）
                if stream:
                    response = self.client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=4096,
                        stream=True
                    )
                    content = ""
                    for chunk in response:
                        if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta
                            if hasattr(delta, 'content') and delta.content:
                                content += delta.content
                    return content if content else "抱歉，未收到有效回复。"
                else:
                    # 非流式输出（根据文档标准格式）
                    response = self.client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=4096,
                        stream=False  # 明确指定非流式
                    )
                    # 检查响应格式（根据文档：response.choices[0].message.content）
                    if hasattr(response, 'choices') and len(response.choices) > 0:
                        choice = response.choices[0]
                        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                            content = choice.message.content
                            if content:
                                return content
                    # 如果响应格式不同，记录日志
                    logger.warning(f"响应格式异常: {type(response)}")
                    return "抱歉，未收到有效回复。请检查API响应格式。"
            except AttributeError as e:
                # 如果API接口不同，尝试兼容调用
                logger.warning(f"API接口不兼容，尝试兼容调用: {e}")
                try:
                    response = self.client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=4096
                    )
                    return response.choices[0].message.content
                except Exception as e2:
                    logger.error(f"兼容调用也失败: {e2}")
                    raise e2
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"AI chat failed: {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            
            # 根据错误类型提供更详细的提示
            if "401" in error_msg or "unauthorized" in error_msg.lower() or "invalid" in error_msg.lower():
                return f"""❌ AI功能调用失败

错误类型：API密钥验证失败

可能原因：
1. API密钥无效或已过期
2. API密钥格式不正确
3. 账户余额不足

解决方法：
1. 检查Zeabur环境变量中的ZHIPU_API_KEY是否正确
2. 访问 https://open.bigmodel.cn/ 验证API密钥
3. 确认账户有足够余额
4. 重新部署应用

错误详情：{error_msg}"""
            elif "rate limit" in error_msg.lower() or "429" in error_msg:
                return f"""⚠️ AI功能暂时受限

原因：API调用频率超限

解决方法：
1. 稍后再试
2. 检查API配额限制
3. 升级API套餐

错误详情：{error_msg}"""
            else:
                return f"""❌ AI功能调用失败

错误：{error_msg}

可能原因：
1. 网络连接问题
2. API服务暂时不可用
3. 请求格式错误

解决方法：
1. 检查网络连接
2. 稍后重试
3. 查看Zeabur日志获取详细信息

当前状态：已切换到本地回复模式"""


def summarize_report(self, report_text: str) -> Optional[Dict[str, Any]]:
    """
    使用AI生成研报结构化摘要
    
    Args:
        report_text: 研报文本
        
    Returns:
        结构化摘要字典，或None如果失败
    """
    if not self.client:
        logger.warning("AI客户端不可用，无法生成AI摘要")
        return None
    
    if len(report_text) > 4000:
        report_text = report_text[:4000] + "..."
    
    system_prompt = """你是一个专业的金融研报分析专家。请仔细分析提供的研报内容，提取关键信息，并生成结构化的摘要。
    
    输出必须是有效的JSON格式，不要添加任何额外文本。
    
    JSON结构：
    {
        "title": "研报标题（如果无法提取，使用'行业研报摘要'）",
        "core_viewpoints": ["核心观点1", "核心观点2", ...]  // 最多5个
        "data_support": [
            {"value": "具体数值", "type": "增长率/价格/产量等"}  // 最多10个关键数据
        ],
        "trend_judgment": "对行业/市场的趋势判断（50-100字）",
        "key_findings": ["关键发现1", "关键发现2", ...]  // 最多5个
        "risk_analysis": ["风险因素1", "风险因素2", ...]  // 最多5个
        "recommendations": ["投资建议1", "投资建议2", ...]  // 最多5个
        "confidence": 0.85  // 置信度，0.0-1.0之间
    }
    
    确保：
    - 所有观点和建议基于原文
    - 数据准确引用原文
    - 语言专业、简洁
    - 如果信息不足，使用合理推断但保持客观
    """
    
    user_prompt = f"""请分析以下研报内容并生成结构化摘要：

{report_text}

请严格按照指定的JSON格式输出，不要添加任何解释或额外文本。"""
    
    try:
        response = self.client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # 降低温度以获得更稳定的输出
            max_tokens=1500,
            stream=False
        )
        
        if hasattr(response, 'choices') and len(response.choices) > 0:
            content = response.choices[0].message.content.strip()
            
            # 尝试解析JSON
            try:
                # 清理可能的markdown代码块
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                elif content.startswith('```'):
                    content = content.replace('```', '').strip()
                
                summary_dict = json.loads(content)
                
                # 验证和填充默认值
                if not summary_dict.get('title'):
                    summary_dict['title'] = '行业研报摘要'
                if not summary_dict.get('core_viewpoints'):
                    summary_dict['core_viewpoints'] = []
                if not summary_dict.get('data_support'):
                    summary_dict['data_support'] = []
                if not summary_dict.get('trend_judgment'):
                    summary_dict['trend_judgment'] = '趋势判断不明确'
                if not summary_dict.get('key_findings'):
                    summary_dict['key_findings'] = []
                if not summary_dict.get('risk_analysis'):
                    summary_dict['risk_analysis'] = []
                if not summary_dict.get('recommendations'):
                    summary_dict['recommendations'] = []
                if 'confidence' not in summary_dict or not isinstance(summary_dict['confidence'], (int, float)):
                    summary_dict['confidence'] = 0.7
                
                # 限制列表长度
                summary_dict['core_viewpoints'] = summary_dict['core_viewpoints'][:5]
                summary_dict['data_support'] = summary_dict['data_support'][:10]
                summary_dict['key_findings'] = summary_dict['key_findings'][:5]
                summary_dict['risk_analysis'] = summary_dict['risk_analysis'][:5]
                summary_dict['recommendations'] = summary_dict['recommendations'][:5]
                
                logger.info("AI研报摘要生成成功")
                return summary_dict
                
            except json.JSONDecodeError as e:
                logger.error(f"AI摘要JSON解析失败: {e}, 内容: {content[:500]}")
                return None
        else:
            logger.warning("AI摘要响应格式异常")
            return None
            
    except Exception as e:
        logger.error(f"AI摘要生成失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None



