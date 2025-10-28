"""
结构化模式提示器 - 将事件知识提取转化为文本生成任务
解决领域标注数据稀疏痛点
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class KnowledgePattern:
    """知识抽取模式"""
    pattern_name: str
    description: str
    input_template: str
    output_format: Dict[str, str]
    extraction_rules: List[str]


class StructuredPatternPrompter:
    """结构化模式提示器"""
    
    def __init__(self):
        self.patterns = self._init_patterns()
    
    def _init_patterns(self) -> Dict[str, KnowledgePattern]:
        """初始化纸浆领域知识抽取模式"""
        patterns = {}
        
        # 模式1: 实体关系提取
        patterns['entity_relation'] = KnowledgePattern(
            pattern_name="实体关系提取",
            description="从文本中提取实体及其关系",
            input_template="""原文：{text}

请从上述文本中提取以下类型的信息：
1. 实体类型：{entity_types}
2. 关系类型：{relation_types}

输出格式：JSON
""",
            output_format={
                "entities": "list of dict with keys: name, type, attributes",
                "relations": "list of dict with keys: subject, predicate, object, confidence"
            },
            extraction_rules=[
                "识别文本中的所有命名实体",
                "确定实体之间的语义关系",
                "提取关系的置信度分数"
            ]
        )
        
        # 模式2: 事件抽取
        patterns['event_extraction'] = KnowledgePattern(
            pattern_name="事件抽取",
            description="从文本中提取事件信息",
            input_template="""原文：{text}

请从上述文本中提取事件信息：
- 事件类型：{event_types}
- 事件主体：{event_subjects}
- 事件属性：时间、地点、参与者、结果

输出格式：JSON
""",
            output_format={
                "events": "list of dict with keys: type, subject, time, location, participants, result"
            },
            extraction_rules=[
                "识别事件触发词",
                "提取事件参与者",
                "推断事件的时间和地点",
                "确定事件结果"
            ]
        )
        
        # 模式3: 属性值提取
        patterns['attribute_extraction'] = KnowledgePattern(
            pattern_name="属性值提取",
            description="从文本中提取实体的属性值",
            input_template="""原文：{text}

请从上述文本中提取实体的属性值：
- 目标实体：{target_entity}
- 属性类型：{attribute_types}

输出格式：JSON
""",
            output_format={
                "attributes": "dict mapping attribute_name to value"
            },
            extraction_rules=[
                "定位目标实体",
                "提取相关属性值",
                "验证属性值的合理性"
            ]
        )
        
        # 模式4: 纸浆领域特定知识提取
        patterns['pulp_domain'] = KnowledgePattern(
            pattern_name="纸浆领域知识提取",
            description="专门用于纸浆行业的领域知识提取",
            input_template="""原文：{text}

请从上述纸浆行业文本中提取：
1. 产品类型（纸浆种类、等级）
2. 生产企业信息
3. 技术参数（白度、强度、纤维长度等）
4. 价格和市场信息
5. 工艺流程
6. 上下游关系

输出格式：JSON
""",
            output_format={
                "products": "list of dict with keys: name, type, grade, specifications",
                "companies": "list of dict with keys: name, role, location",
                "technical_params": "dict mapping param_name to value",
                "market_info": "dict with keys: price, trend, volume",
                "processes": "list of process steps",
                "relationships": "list of upstream-downstream relations"
            },
            extraction_rules=[
                "识别纸浆产品和技术术语",
                "提取生产流程信息",
                "提取市场数据",
                "建立产业链关系"
            ]
        )
        
        return patterns
    
    def generate_prompt(self, pattern_name: str, text: str, **kwargs) -> str:
        """生成结构化提示"""
        if pattern_name not in self.patterns:
            raise ValueError(f"未知的模式：{pattern_name}")
        
        pattern = self.patterns[pattern_name]
        
        # 填充模板参数
        prompt_params = {
            'text': text,
            **kwargs
        }
        
        # 为纸浆领域填充默认值
        if pattern_name == 'pulp_domain':
            prompt_params.setdefault('entity_types', '["纸浆产品", "生产企业", "设备", "原材料", "化学助剂"]')
            prompt_params.setdefault('relation_types', '["生产", "供应", "应用于", "含有的成分", "工艺步骤"]')
        
        return pattern.input_template.format(**prompt_params)
    
    def parse_output(self, pattern_name: str, output_text: str) -> Dict[str, Any]:
        """解析输出为结构化数据"""
        try:
            # 尝试直接解析JSON
            if output_text.strip().startswith('{') or output_text.strip().startswith('['):
                return json.loads(output_text)
            
            # 尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', output_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # 如果无法解析，返回原始文本
            return {"raw_output": output_text}
        except json.JSONDecodeError:
            return {"raw_output": output_text, "error": "无法解析JSON"}
    
    def extract_knowledge(self, pattern_name: str, text: str, model_output: str) -> Dict[str, Any]:
        """执行知识提取"""
        parsed_output = self.parse_output(pattern_name, model_output)
        
        return {
            "pattern": pattern_name,
            "text": text,
            "extracted_knowledge": parsed_output,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
    
    def batch_extract(self, pattern_name: str, texts: List[str], model_outputs: List[str]) -> List[Dict[str, Any]]:
        """批量提取知识"""
        results = []
        for text, output in zip(texts, model_outputs):
            try:
                result = self.extract_knowledge(pattern_name, text, output)
                results.append(result)
            except Exception as e:
                results.append({
                    "pattern": pattern_name,
                    "text": text,
                    "error": str(e)
                })
        return results
    
    def get_pattern_info(self, pattern_name: str) -> Dict[str, Any]:
        """获取模式信息"""
        if pattern_name not in self.patterns:
            return {"error": f"未知的模式：{pattern_name}"}
        
        pattern = self.patterns[pattern_name]
        return {
            "name": pattern.pattern_name,
            "description": pattern.description,
            "output_format": pattern.output_format,
            "extraction_rules": pattern.extraction_rules
        }
    
    def list_patterns(self) -> List[str]:
        """列出所有可用的模式"""
        return list(self.patterns.keys())

