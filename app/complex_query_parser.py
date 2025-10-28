"""
复杂查询解析器
支持自然语言复杂查询，如"2025年Kruger收购对漂白针叶木浆价格的影响"
"""
from typing import List, Dict, Any, Optional, Tuple
import re
from datetime import datetime
from app.intent_classifier import IntentClassifier


class ComplexQueryParser:
    """复杂查询解析器"""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        
        # 时间识别模式
        self.time_patterns = [
            (r'\d{4}年', 'year'),
            (r'\d{4}-\d{2}', 'date'),
            (r'\d{1,2}月', 'month'),
            (r'去年|今年|明年', 'relative_year'),
        ]
        
        # 事件类型识别
        self.event_keywords = {
            '收购': ['收购', '并购', '合并'],
            '涨价': ['价格上涨', '涨价', '提价'],
            '降价': ['价格下跌', '降价', '下调'],
            '停产': ['停产', '关闭', '停产'],
            '扩张': ['扩张', '扩大', '增加产能'],
            '事故': ['事故', '泄漏', '爆炸'],
        }
        
        # 实体类型识别
        self.entity_keywords = {
            '公司': ['公司', '企业', '集团', '股份'],
            '产品': ['纸浆', '浆料', '漂白浆', '针叶木浆', '阔叶木浆'],
            '地区': ['地区', '市场', '国内', '海外'],
            '价格': ['价格', '售价', '报价', '市场价格'],
        }
    
    def parse(self, query: str) -> Dict[str, Any]:
        """
        解析复杂查询
        
        示例："2025年Kruger收购对漂白针叶木浆价格的影响"
        """
        result = {
            'original_query': query,
            'query_type': self._classify_query_type(query),
            'entities': self._extract_entities(query),
            'events': self._extract_events(query),
            'temporal': self._extract_temporal(query),
            'relationships': self._extract_relationships(query),
            'query_structure': self._build_query_structure(query),
            'kg_query': self._build_kg_query(query)
        }
        
        return result
    
    def _classify_query_type(self, query: str) -> str:
        """分类查询类型"""
        if any(kw in query for kw in ['影响', '效应', '导致', '引起']):
            return 'impact_analysis'
        elif any(kw in query for kw in ['影响', '分析', '预测', '趋势']):
            return 'prediction'
        elif any(kw in query for kw in ['是什么', '定义', '介绍']):
            return 'definition'
        elif any(kw in query for kw in ['对比', '比较', '差异']):
            return 'comparison'
        else:
            return 'general'
    
    def _extract_entities(self, query: str) -> List[Dict[str, Any]]:
        """提取实体"""
        entities = []
        
        # 公司名
        company_patterns = [
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',  # 英文公司名
            r'([一-龥]+(?:公司|企业|集团|股份))',  # 中文公司名
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                entities.append({
                    'name': match,
                    'type': 'company',
                    'confidence': 0.8
                })
        
        # 产品名
        product_keywords = ['纸浆', '浆料', '漂白浆', '针叶木浆', '阔叶木浆', '化学浆']
        for keyword in product_keywords:
            if keyword in query:
                # 尝试提取完整产品名
                product_pattern = rf'({keyword}[\w\s]*)'
                matches = re.findall(product_pattern, query)
                for match in matches:
                    entities.append({
                        'name': match.strip(),
                        'type': 'product',
                        'confidence': 0.9
                    })
        
        return entities
    
    def _extract_events(self, query: str) -> List[Dict[str, Any]]:
        """提取事件"""
        events = []
        
        for event_type, keywords in self.event_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    events.append({
                        'type': event_type,
                        'keyword': keyword,
                        'confidence': 0.8
                    })
        
        return events
    
    def _extract_temporal(self, query: str) -> Dict[str, Any]:
        """提取时间信息"""
        temporal = {
            'absolute_time': None,
            'relative_time': None,
            'time_expression': None
        }
        
        # 绝对时间
        year_match = re.search(r'(\d{4})年', query)
        if year_match:
            temporal['absolute_time'] = year_match.group(1)
            temporal['time_expression'] = year_match.group(0)
        
        # 相对时间
        if '今年' in query or '当年' in query:
            temporal['relative_time'] = 'current'
            temporal['absolute_time'] = str(datetime.now().year)
        elif '去年' in query or '上年' in query:
            temporal['relative_time'] = 'previous'
            temporal['absolute_time'] = str(datetime.now().year - 1)
        elif '明年' in query or '次年' in query:
            temporal['relative_time'] = 'next'
            temporal['absolute_time'] = str(datetime.now().year + 1)
        
        return temporal
    
    def _extract_relationships(self, query: str) -> List[Dict[str, Any]]:
        """提取关系"""
        relationships = []
        
        relation_patterns = [
            (r'(.+)对(.+)的影响', 'affects'),
            (r'(.+)导致(.+)', 'causes'),
            (r'(.+)引起(.+)', 'triggers'),
            (r'(.+)和(.+)的关系', 'related_to'),
        ]
        
        for pattern, relation_type in relation_patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                relationships.append({
                    'subject': match[0],
                    'object': match[1],
                    'relation': relation_type,
                    'confidence': 0.8
                })
        
        return relationships
    
    def _build_query_structure(self, query: str) -> Dict[str, Any]:
        """构建查询结构"""
        structure = {
            'main_topic': None,
            'sub_topics': [],
            'focus_area': None,
            'key_questions': []
        }
        
        # 提取主题
        if '影响' in query or '效应' in query:
            structure['focus_area'] = 'impact'
            structure['key_questions'] = ['What is the impact?', 'Who/what is affected?']
        
        if '价格' in query:
            structure['focus_area'] = 'price'
            structure['key_questions'].append('What is the price impact?')
        
        return structure
    
    def _build_kg_query(self, query: str) -> Dict[str, Any]:
        """构建知识图谱查询"""
        entities = self._extract_entities(query)
        events = self._extract_events(query)
        temporal = self._extract_temporal(query)
        relationships = self._extract_relationships(query)
        
        kg_query = {
            'search_entities': [e['name'] for e in entities],
            'filter_events': [e['type'] for e in events],
            'time_constraint': temporal,
            'relationship_paths': [],
        }
        
        # 如果需要查找关联路径
        if relationships:
            for rel in relationships:
                kg_query['relationship_paths'].append({
                    'from': rel['subject'],
                    'to': rel['object'],
                    'relation_type': rel['relation']
                })
        
        return kg_query
    
    def expand_query(self, parsed_query: Dict[str, Any]) -> List[str]:
        """扩展查询"""
        expanded = []
        
        original = parsed_query['original_query']
        
        # 添加同义词扩展
        synonyms = {
            '影响': ['效应', '作用', '冲击'],
            '收购': ['并购', '合并', '整合'],
            '价格': ['售价', '报价', '市场价格'],
            '纸浆': ['浆料', '浆液'],
        }
        
        for original_word, synonyms_list in synonyms.items():
            if original_word in original:
                for synonym in synonyms_list:
                    expanded.append(original.replace(original_word, synonym))
        
        # 添加简化查询
        if '影响' in original:
            expanded.append(original.replace('的影响', ''))
        
        return expanded


class ComplexQueryExecutor:
    """复杂查询执行器"""
    
    def __init__(self, retriever, kg_builder):
        self.retriever = retriever
        self.kg_builder = kg_builder
        self.parser = ComplexQueryParser()
    
    def execute(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """执行复杂查询"""
        # 1. 解析查询
        parsed = self.parser.parse(query)
        
        # 2. 从知识图谱查找相关实体
        kg_results = self._search_knowledge_graph(parsed)
        
        # 3. 扩展查询词
        expanded_queries = self.parser.expand_query(parsed)
        
        # 4. 执行多轮检索
        all_results = []
        for expanded_query in [query] + expanded_queries:
            results = self.retriever.search(expanded_query, top_k=top_k)
            all_results.extend(results)
        
        # 5. 构建关联路径
        kg_paths = self._build_kg_paths(parsed, kg_results)
        
        # 6. 生成答案
        answer = self._generate_answer(parsed, kg_results, all_results)
        
        return {
            'query': query,
            'parsed': parsed,
            'kg_results': kg_results,
            'text_results': all_results,
            'kg_paths': kg_paths,
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        }
    
    def _search_knowledge_graph(self, parsed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从知识图谱搜索"""
        entities = parsed_query.get('entities', [])
        events = parsed_query.get('events', [])
        
        kg_results = []
        
        # 搜索相关实体
        for entity in entities:
            entity_obj = self.kg_builder.get_entity_by_name(entity['name'])
            if entity_obj:
                # 获取实体的关系
                relations = self.kg_builder.get_relations(entity_obj.id)
                
                # 获取相关实体
                related = self.kg_builder.find_related_entities(entity_obj.id, max_depth=2)
                
                kg_results.append({
                    'entity': {
                        'name': entity_obj.name,
                        'type': entity_obj.type,
                        'attributes': entity_obj.attributes
                    },
                    'relations': relations,
                    'related_entities': related,
                    'relevance': 1.0
                })
        
        return kg_results
    
    def _build_kg_paths(self, parsed_query: Dict[str, Any], kg_results: List[Dict]) -> List[Dict]:
        """构建知识图谱路径"""
        paths = []
        
        relationships = parsed_query.get('relationships', [])
        
        for rel in relationships:
            subject = rel.get('subject')
            object = rel.get('object')
            
            # 查找两个实体之间的路径
            subject_entity = self.kg_builder.get_entity_by_name(subject) if subject else None
            object_entity = self.kg_builder.get_entity_by_name(object) if object else None
            
            if subject_entity and object_entity:
                # 查找连接路径
                path = self._find_path(subject_entity.id, object_entity.id)
                if path:
                    paths.append({
                        'from': subject,
                        'to': object,
                        'path': path,
                        'path_length': len(path)
                    })
        
        return paths
    
    def _find_path(self, from_id: str, to_id: str, max_depth: int = 3) -> List[str]:
        """查找两个实体之间的路径"""
        visited = set()
        queue = [([from_id], 0)]
        
        while queue:
            current_path, depth = queue.pop(0)
            current_id = current_path[-1]
            
            if current_id == to_id:
                return current_path
            
            if depth >= max_depth or current_id in visited:
                continue
            
            visited.add(current_id)
            
            # 获取当前实体的所有关系
            relations = self.kg_builder.get_relations(current_id)
            
            for relation in relations:
                neighbor_id = relation.object if relation.subject == current_id else relation.subject
                if neighbor_id not in visited:
                    queue.append((current_path + [neighbor_id], depth + 1))
        
        return []
    
    def _generate_answer(self, parsed_query: Dict, kg_results: List[Dict], text_results: List[Dict]) -> str:
        """生成答案"""
        query_type = parsed_query.get('query_type')
        entities = parsed_query.get('entities', [])
        events = parsed_query.get('events', [])
        
        if not kg_results and not text_results:
            return "未找到相关信息。"
        
        answer_parts = []
        
        # 构建答案
        if entities:
            entity_names = [e['name'] for e in entities]
            answer_parts.append(f"关于{', '.join(entity_names)}的信息：")
        
        if kg_results:
            answer_parts.append("\n知识图谱分析：")
            for kg_result in kg_results[:3]:
                entity = kg_result['entity']
                answer_parts.append(f"- {entity['name']}（{entity['type']}）")
                if entity.get('attributes'):
                    attrs = list(entity['attributes'].items())[:2]
                    answer_parts.append(f"  特征：{', '.join([f'{k}:{v}' for k,v in attrs])}")
        
        if text_results:
            answer_parts.append(f"\n相关文档：找到{len(text_results)}条相关结果。")
        
        if query_type == 'impact_analysis':
            answer_parts.append("\n影响分析：")
            if events:
                for event in events:
                    answer_parts.append(f"- {event['type']}事件可能对相关产品产生影响")
        
        return "\n".join(answer_parts)

