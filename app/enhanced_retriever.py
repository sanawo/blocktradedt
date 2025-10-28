"""
增强版语义检索器
融合知识图谱优化语义匹配
提升专业术语理解准确率
"""
from typing import List, Dict, Any, Optional, Tuple
import json
from pathlib import Path
import numpy as np
from app.kg_builder import KnowledgeGraphBuilder
from app.pattern_prompter import StructuredPatternPrompter


class EnhancedRetriever:
    """增强版检索器 - 融合知识图谱和语义检索"""
    
    def __init__(self, kg_path: Optional[str] = None):
        self.kg_builder = KnowledgeGraphBuilder()
        self.pattern_prompter = StructuredPatternPrompter()
        
        # 加载知识图谱
        if kg_path and Path(kg_path).exists():
            self.kg_builder.load_from_json(kg_path)
        else:
            # 初始化种子数据
            self.kg_builder.load_pulp_domain_seed_data()
        
        # 术语词典（从知识图谱中提取）
        self.term_dict = self._build_term_dictionary()
        
        # 简单的向量空间（可以使用更高级的embedding）
        self.entity_vectors = self._build_entity_vectors()
    
    def _build_term_dictionary(self) -> Dict[str, str]:
        """构建术语词典"""
        term_dict = {}
        
        for entity in self.kg_builder.entities.values():
            # 添加实体名称
            term_dict[entity.name] = entity.type
            
            # 添加属性作为相关术语
            for key, value in entity.attributes.items():
                if isinstance(value, str):
                    term_dict[key] = entity.type
        
        return term_dict
    
    def _build_entity_vectors(self) -> Dict[str, np.ndarray]:
        """构建实体向量表示"""
        vectors = {}
        
        for entity_id, entity in self.kg_builder.entities.items():
            # 简单的one-hot编码（可以使用更高级的embedding）
            vector = np.zeros(len(self.kg_builder.entity_type_count))
            
            # 基于实体类型和属性构建向量
            type_idx = list(self.kg_builder.entity_type_count.keys()).index(entity.type) if entity.type in self.kg_builder.entity_type_count else 0
            vector[type_idx] = 1.0
            
            # 添加属性特征
            if entity.attributes:
                attr_hash = hash(str(entity.attributes)) % 100
                vector = np.append(vector, attr_hash)
            
            vectors[entity_id] = vector
        
        return vectors
    
    def search(self, query: str, top_k: int = 10, use_kg: bool = True) -> List[Dict[str, Any]]:
        """执行增强检索"""
        results = []
        
        # 1. 知识图谱增强检索
        if use_kg:
            kg_results = self._kg_search(query, top_k)
            results.extend(kg_results)
        
        # 2. 语义匹配检索
        semantic_results = self._semantic_search(query, top_k)
        results.extend(semantic_results)
        
        # 3. 合并和排序结果
        merged_results = self._merge_and_rank(query, results, top_k)
        
        return merged_results
    
    def _kg_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """基于知识图谱的检索"""
        results = []
        
        # 1. 实体匹配
        matched_entities = []
        for entity_id, time in self.kg_builder.entities.items():
            entity = time
            # 简单的关键词匹配
            if any(keyword in entity.name for keyword in query.split()):
                matched_entities.append(entity)
            
            # 匹配属性
            for attr_key, attr_value in entity.attributes.items():
                if isinstance(attr_value, str) and any(keyword in attr_value for keyword in query.split()):
                    matched_entities.append(entity)
                    break
        
        # 2. 为每个匹配的实体查找相关信息
        for entity in matched_entities[:top_k]:
            # 获取实体的关系
            relations = self.kg_builder.get_relations(entity.id)
            
            # 查找相关实体
            related_entities = self.kg_builder.find_related_entities(entity.id, max_depth=2)
            
            result = {
                "entity_id": entity.id,
                "entity_name": entity.name,
                "entity_type": entity.type,
                "attributes": entity.attributes,
                "relations": [{"predicate": r.predicate, "object": self.kg_builder.get_entity(r.object).name if self.kg_builder.get_entity(r.object) else r.object} for r in relations[:5]],
                "related_entities": [self.kg_builder.get_entity(eid).name if self.kg_builder.get_entity(eid) else eid for eid in related_entities[:5]],
                "score": 1.0,  # KG结果的高置信度
                "source": "knowledge_graph"
            }
            results.append(result)
        
        return results
    
    def _semantic_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """语义搜索"""
        results = []
        
        # 简单的TF-IDF风格的评分
        query_terms = set(query.lower().split())
        
        for entity_id, entity in self.kg_builder.entities.items():
            score = 0.0
            
            # 计算匹配分数
            entity_text = f"{entity.name} {entity.type} {str(entity.attributes)}"
            entity_terms = set(entity_text.lower().split())
            
            # TF得分
            common_terms = query_terms & entity_terms
            score += len(common_terms) * 0.5
            
            # 考虑同义词
            for term in query_terms:
                if term in self.term_dict:
                    score += 0.3
            
            if score > 0:
                results.append({
                    "entity_id": entity.id,
                    "entity_name": entity.name,
                    "entity_type": entity.type,
                    "attributes": entity.attributes,
                    "score": score,
                    "source": "semantic_search"
                })
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]
    
    def _merge_and_rank(self, query: str, results: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """合并和排序结果"""
        # 去重
        seen_ids = set()
        unique_results = []
        
        for result in results:
            entity_id = result.get('entity_id')
            if entity_id not in seen_ids:
                seen_ids.add(entity_id)
                unique_results.append(result)
        
        # 重新排序（考虑多个因素）
        for result in unique_results:
            score = result.get('score', 0.0)
            
            # KG结果加权
            if result.get('source') == 'knowledge_graph':
                score *= 1.5
            
            # 相关实体数量加权
            related_count = len(result.get('related_entities', []))
            score += related_count * 0.1
            
            result['final_score'] = score
        
        # 按最终分数排序
        unique_results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        return unique_results[:top_k]
    
    def extract_query_intent(self, query: str) -> Dict[str, Any]:
        """提取查询意图"""
        intent = {
            "type": "general",
            "entities": [],
            "attributes": [],
            "relations": []
        }
        
        # 检查是否为实体查询
        for entity_id, entity in self.kg_builder.entities.items():
            if entity.name in query:
                intent["entities"].append({
                    "id": entity_id,
                    "name": entity.name,
                    "type": entity.type
                })
                intent["type"] = "entity_query"
        
        # 检查是否为属性查询
        for attr_key in self.term_dict.keys():
            if attr_key in query:
                intent["attributes"].append(attr_key)
                intent["type"] = "attribute_query"
        
        # 检查是否为关系查询
        relation_keywords = ["生产", "制成", "用于", "含有", "包含"]
        for keyword in relation_keywords:
            if keyword in query:
                intent["relations"].append(keyword)
                intent["type"] = "relation_query"
        
        return intent
    
    def answer_query(self, query: str) -> Dict[str, Any]:
        """回答查询"""
        # 1. 提取查询意图
        intent = self.extract_query_intent(query)
        
        # 2. 执行检索
        results = self.search(query, top_k=5)
        
        # 3. 生成答案
        answer = self._generate_answer(query, intent, results)
        
        return {
            "query": query,
            "intent": intent,
            "results": results,
            "answer": answer
        }
    
    def _generate_answer(self, query: str, intent: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
        """生成答案文本"""
        if not results:
            return f"抱歉，未找到与'{query}'相关的信息。"
        
        if intent["type"] == "entity_query" and intent["entities"]:
            entity = intent["entities"][0]
            entity_data = next((r for r in results if r.get('entity_id') == entity['id']), None)
            
            if entity_data:
                answer = f"{entity['name']}是一种{entity['type']}。"
                
                if entity_data.get('attributes'):
                    attrs = "、".join([f"{k}:{v}" for k, v in list(entity_data['attributes'].items())[:3]])
                    answer += f"其特征包括：{attrs}。"
                
                if entity_data.get('relations'):
                    rels = "、".join([f"{r['predicate']}{r['object']}" for r in entity_data['relations'][:3]])
                    answer += f"相关关系：{rels}。"
                
                return answer
        
        # 通用答案
        top_result = results[0]
        answer = f"根据知识图谱，找到了以下信息：{top_result.get('entity_name', '未知')}，"
        answer += f"类型为{top_result.get('entity_type', '未知')}。"
        
        return answer
    
    def get_kg_statistics(self) -> Dict[str, Any]:
        """获取知识图谱统计信息"""
        return self.kg_builder.get_statistics()
    
    def expand_query(self, query: str) -> List[str]:
        """查询扩展（使用知识图谱）"""
        expanded_queries = [query]
        
        # 查找相关的同义词和术语
        for term, term_type in self.term_dict.items():
            if term in query:
                # 查找同类型的其他术语
                similar_terms = [t for t, ty in self.term_dict.items() if ty == term_type and t != term]
                if similar_terms:
                    for similar_term in similar_terms[:2]:
                        expanded_query = query.replace(term, similar_term)
                        expanded_queries.append(expanded_query)
        
        return expanded_queries[:5]

