"""
查询意图识别模块
优化查询意图识别和语义匹配
"""
from typing import List, Dict, Any, Optional
import re
from enum import Enum


class QueryIntent(Enum):
    """查询意图类型"""
    ENTITY_SEARCH = "entity_search"  # 实体查询
    ATTRIBUTE_SEARCH = "attribute_search"  # 属性查询
    RELATION_SEARCH = "relation_search"  # 关系查询
    VALUE_SEARCH = "value_search"  # 数值查询
    DEFINITION = "definition"  # 定义查询
    COMPARISON = "comparison"  # 比较查询
    TREND_ANALYSIS = "trend_analysis"  # 趋势分析
    GENERAL = "general"  # 通用查询


class IntentClassifier:
    """查询意图分类器"""
    
    def __init__(self):
        # 意图关键词模式
        self.intent_patterns = {
            QueryIntent.ENTITY_SEARCH: [
                r"什么是(.+)",
                r"(.+)是什么",
                r"介绍(.+)",
                r"(.+)的详细信息",
                r"查找(.+)",
            ],
            QueryIntent.ATTRIBUTE_SEARCH: [
                r"(.+)的(.+)是多少",
                r"(.+)有哪些(.+)",
                r"(.+)的(.+)特性",
                r"(.+)的(.+)参数",
            ],
            QueryIntent.RELATION_SEARCH: [
                r"(.+)和(.+)的关系",
                r"(.+)用于(.+)",
                r"(.+)能生产(.+)",
                r"(.+)由(.+)制成",
            ],
            QueryIntent.VALUE_SEARCH: [
                r"(.+)的价格",
                r"(.+)的成本",
                r"(.+)数量",
                r"(.+)销量",
            ],
            QueryIntent.DEFINITION: [
                r"定义(.+)",
                r"(.+)的含义",
                r"解释(.+)",
                r"(.+)的概念",
            ],
            QueryIntent.COMPARISON: [
                r"(.+)和(.+)哪个好",
                r"(.+)与(.+)的区别",
                r"(.+)对比(.+)",
                r"比较(.+)和(.+)",
            ],
            QueryIntent.TREND_ANALYSIS: [
                r"(.+)趋势",
                r"(.+)变化",
                r"(.+)走势",
                r"(.+)未来",
            ],
        }
        
        # 纸浆领域特定意图词
        self.domain_keywords = {
            "产品": ["纸浆", "浆料", "纤维", "浆液"],
            "属性": ["白度", "强度", "纤维长度", "得率", "水分"],
            "关系": ["生产", "制成", "应用于", "含有", "工艺流程"],
            "企业": ["生产企业", "供应商", "制造商"],
            "工艺": ["蒸煮", "漂白", "洗涤", "精制"],
        }
    
    def classify(self, query: str) -> Dict[str, Any]:
        """分类查询意图"""
        intent_scores = {}
        
        # 对每种意图类型评分
        for intent_type, patterns in self.intent_patterns.items():
            score = 0.0
            
            # 匹配模式
            for pattern in patterns:
                if re.search(pattern, query):
                    score += 1.0
            
            intent_scores[intent_type] = score
        
        # 领域关键词加分
        for category, keywords in self.domain_keywords.items():
            if any(keyword in query for keyword in keywords):
                if category == "产品":
                    intent_scores[QueryIntent.ENTITY_SEARCH] = intent_scores.get(QueryIntent.ENTITY_SEARCH, 0) + 0.5
                elif category == "属性":
                    intent_scores[QueryIntent.ATTRIBUTE_SEARCH] = intent_scores.get(QueryIntent.ATTRIBUTE_SEARCH, 0) + 0.5
                elif category == "关系":
                    intent_scores[QueryIntent.RELATION_SEARCH] = intent_scores.get(QueryIntent.RELATION_SEARCH, 0) + 0.5
        
        # 找到最高分的意图
        if intent_scores:
            primary_intent = max(intent_scores.items(), key=lambda x: x[1])
            confidence = primary_intent[1] / (sum(intent_scores.values()) + 1e-10)
            
            return {
                "intent": primary_intent[0].value,
                "confidence": confidence,
                "all_scores": {k.value: v for k, v in intent_scores.items()},
                "query": query
            }
        else:
            return {
                "intent": QueryIntent.GENERAL.value,
                "confidence": 0.5,
                "all_scores": {},
                "query": query
            }
    
    def extract_entities(self, query: str) -> List[str]:
        """从查询中提取实体"""
        entities = []
        
        # 查找领域关键词中的实体
        for category, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    entities.append(keyword)
        
        # 查找名词短语（简单模式）
        noun_patterns = [
            r"([A-Za-z]+\s+)?[\u4e00-\u9fa5]{2,8}",
        ]
        
        for pattern in noun_patterns:
            matches = re.findall(pattern, query)
            entities.extend([m.strip() if isinstance(m, tuple) else m for m in matches])
        
        return list(set(entities))
    
    def extract_attributes(self, query: str) -> List[str]:
        """从查询中提取属性"""
        attributes = []
        
        # 查找属性关键词
        attr_keywords = self.domain_keywords.get("属性", [])
        for keyword in attr_keywords:
            if keyword in query:
                attributes.append(keyword)
        
        # 查找疑问词后的词
        question_patterns = [
            r"(.+)是多少",
            r"(.+)有哪些",
            r"(.+)的(.+)特性",
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, query)
            if matches:
                attributes.extend([m for m in matches if isinstance(m, str)])
        
        return list(set(attributes))
    
    def extract_comparison_items(self, query: str) -> List[str]:
        """提取比较查询中的对比项"""
        items = []
        
        # 查找"和"、"与"、"对比"等连接词
        comparison_patterns = [
            r"(.+)和(.+)",
            r"(.+)与(.+)",
            r"(.+)对比(.+)",
        ]
        
        for pattern in comparison_patterns:
            matches = re.findall(pattern, query)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        items.extend([m.strip() for m in match])
                    else:
                        items.append(match.strip())
        
        return list(set(items))
    
    def get_query_type(self, query: str) -> str:
        """获取查询类型"""
        intent_result = self.classify(query)
        return intent_result["intent"]
    
    def suggest_query_improvements(self, query: str) -> List[str]:
        """建议查询改进"""
        suggestions = []
        
        intent_result = self.classify(query)
        confidence = intent_result["confidence"]
        
        if confidence < 0.5:
            suggestions.append("查询意图不够明确，请尝试添加更具体的领域关键词")
        
        entities = self.extract_entities(query)
        if not entities:
            suggestions.append("未检测到具体实体，请指定要查询的产品、企业或概念")
        elif len(entities) > 3:
            suggestions.append("查询包含过多实体，建议简化为1-2个核心实体")
        
        # 检查是否为属性查询但没有指定属性
        if intent_result["intent"] == QueryIntent.ATTRIBUTE_SEARCH.value:
            attributes = self.extract_attributes(query)
            if not attributes:
                suggestions.append("属性查询建议明确指定要查询的属性（如白度、强度等）")
        
        return suggestions
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """完整解析查询"""
        intent_result = self.classify(query)
        
        return {
            "original_query": query,
            "intent": intent_result["intent"],
            "confidence": intent_result["confidence"],
            "entities": self.extract_entities(query),
            "attributes": self.extract_attributes(query),
            "comparison_items": self.extract_comparison_items(query),
            "suggestions": self.suggest_query_improvements(query),
            "all_intent_scores": intent_result["all_scores"]
        }


class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self, intent_classifier: IntentClassifier):
        self.intent_classifier = intent_classifier
    
    def optimize(self, query: str) -> Dict[str, Any]:
        """优化查询"""
        parsed = self.intent_classifier.parse_query(query)
        
        # 根据意图优化查询
        optimized_query = query
        
        if parsed["intent"] == QueryIntent.ENTITY_SEARCH.value:
            # 实体查询：添加同义词
            optimized_query = self._add_synonyms(query, parsed["entities"])
        
        elif parsed["intent"] == QueryIntent.ATTRIBUTE_SEARCH.value:
            # 属性查询：规范化属性名称
            optimized_query = self._normalize_attributes(query, parsed["attributes"])
        
        elif parsed["intent"] == QueryIntent.RELATION_SEARCH.value:
            # 关系查询：扩展关系词
            optimized_query = self._expand_relations(query)
        
        return {
            "original_query": query,
            "optimized_query": optimized_query,
            "parsed": parsed,
            "improvements": parsed["suggestions"]
        }
    
    def _add_synonyms(self, query: str, entities: List[str]) -> str:
        """添加同义词"""
        synonym_map = {
            "纸浆": "浆料",
            "浆料": "纸浆",
            "白度": "亮度",
            "强度": "抗张强度",
        }
        
        optimized = query
        for entity in entities:
            if entity in synonym_map:
                synonym = synonym_map[entity]
                if synonym not in query:
                    optimized += f" {synonym}"
        
        return optimized
    
    def _normalize_attributes(self, query: str, attributes: List[str]) -> str:
        """规范化属性名称"""
        attr_map = {
            "白值": "白度",
            "亮度": "白度",
            "抗张强度": "强度",
            "断裂强度": "强度",
        }
        
        optimized = query
        for attr in attributes:
            if attr in attr_map:
                normalized = attr_map[attr]
                optimized = optimized.replace(attr, normalized)
        
        return optimized
    
    def _expand_relations(self, query: str) -> str:
        """扩展关系词"""
        relation_synonyms = {
            "制成": ["生产", "制作", "加工"],
            "用于": ["应用于", "适用于", "用在"],
            "含有": ["包含", "包括", "具有"],
        }
        
        optimized = query
        for relation, synonyms in relation_synonyms.items():
            if relation in query:
                optimized += " " + " ".join(synonyms)
        
        return optimized

