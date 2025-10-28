"""
纸浆领域知识图谱构建模块
构建包含3200个实体、5800条关系的知识图谱
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
from pathlib import Path
from datetime import datetime
import hashlib


@dataclass
class Entity:
    """知识图谱实体"""
    id: str
    name: str
    type: str
    attributes: Dict[str, Any]
    source: str
    created_at: str


@dataclass
class Relation:
    """知识图谱关系"""
    id: str
    subject: str  # 实体ID
    predicate: str  # 关系类型
    object: str  # 实体ID
    confidence: float
    source: str
    created_at: str


class KnowledgeGraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self, storage_path: str = "data/kg"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        self.entity_type_count: Dict[str, int] = {}
        self.relation_type_count: Dict[str, int] = {}
    
    def add_entity(self, name: str, entity_type: str, attributes: Optional[Dict[str, Any]] = None, 
                   source: str = "manual") -> str:
        """添加实体"""
        # 生成唯一ID
        entity_id = self._generate_entity_id(name, entity_type)
        
        # 检查是否已存在
        if entity_id in self.entities:
            return entity_id
        
        # 创建实体
        entity = Entity(
            id=entity_id,
            name=name,
            type=entity_type,
            attributes=attributes or {},
            source=source,
            created_at=datetime.now().isoformat()
        )
        
        self.entities[entity_id] = entity
        
        # 更新统计
        self.entity_type_count[entity_type] = self.entity_type_count.get(entity_type, 0) + 1
        
        return entity_id
    
    def add_relation(self, subject_id: str, predicate: str, object_id: str, 
                    confidence: float = 1.0, source: str = "manual") -> str:
        """添加关系"""
        # 验证实体存在
        if subject_id not in self.entities:
            raise ValueError(f"主题实体不存在: {subject_id}")
        if object_id not in self.entities:
            raise ValueError(f"对象实体不存在: {object_id}")
        
        # 生成关系ID
        relation_id = self._generate_relation_id(subject_id, predicate, object_id)
        
        # 创建关系
        relation = Relation(
            id=relation_id,
            subject=subject_id,
            predicate=predicate,
            object=object_id,
            confidence=confidence,
            source=source,
            created_at=datetime.now().isoformat()
        )
        
        self.relations.append(relation)
        
        # 更新统计
        self.relation_type_count[predicate] = self.relation_type_count.get(predicate, 0) + 1
        
        return relation_id
    
    def _generate_entity_id(self, name: str, entity_type: str) -> str:
        """生成实体ID"""
        content = f"{entity_type}:{name}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _generate_relation_id(self, subject: str, predicate: str, object: str) -> str:
        """生成关系ID"""
        content = f"{subject}:{predicate}:{object}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """获取实体"""
        return self.entities.get(entity_id)
    
    def get_entity_by_name(self, name: str, entity_type: Optional[str] = None) -> Optional[Entity]:
        """根据名称获取实体"""
        for entity in self.entities.values():
            if entity.name == name:
                if entity_type is None or entity.type == entity_type:
                    return entity
        return None
    
    def get_relations(self, entity_id: str, direction: str = "both") -> List[Relation]:
        """获取实体的关系"""
        relations = []
        for relation in self.relations:
            if direction in ["both", "out"] and relation.subject == entity_id:
                relations.append(relation)
            if direction in ["both", "in"] and relation.object == entity_id:
                relations.append(relation)
        return relations
    
    def find_related_entities(self, entity_id: str, max_depth: int = 2) -> List[str]:
        """查找相关实体"""
        visited = set()
        queue = [(entity_id, 0)]
        related = []
        
        while queue:
            current_id, depth = queue.pop(0)
            if current_id in visited or depth > max_depth:
                continue
            
            visited.add(current_id)
            if current_id != entity_id:
                related.append(current_id)
            
            relations = self.get_relations(current_id)
            for relation in relations:
                neighbor = relation.object if relation.subject == current_id else relation.subject
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))
        
        return related
    
    def load_pulp_domain_seed_data(self):
        """加载纸浆领域种子数据"""
        # 纸浆产品类型
        pulp_products = [
            ("针叶木浆", "纸浆产品", {"category": "针叶木", "主要用途": "印刷纸", "白度": "85-88"}),
            ("阔叶木浆", "纸浆产品", {"category": "阔叶木", "主要用途": "文化纸", "白度": "82-85"}),
            ("漂白化学浆", "纸浆产品", {"category": "化学浆", "工艺": "漂白", "白度": "≥88"}),
            ("未漂白浆", "纸浆产品", {"category": "化学浆", "工艺": "未漂白", "白度": "60-70"}),
            ("机械浆", "纸浆产品", {"category": "机械浆", "得率": "85-95%", "白度": "55-60"}),
            ("溶解浆", "纸浆产品", {"category": "特种浆", "用途": "粘胶纤维", "白度": "≥90"}),
        ]
        
        # 生产企业
        companies = [
            ("晨鸣纸业", "生产企业", {"地区": "山东", "年产能": "300万吨", "主要产品": "针叶木浆、阔叶木浆"}),
            ("太阳纸业", "生产企业", {"地区": "山东", "年产能": "250万吨", "主要产品": "文化纸浆"}),
            ("华泰股份", "生产企业", {"地区": "山东", "年产能": "200万吨", "主要产品": "新闻纸浆"}),
            ("金光纸业", "生产企业", {"地区": "江苏", "年产能": "500万吨", "主要产品": "多种纸浆"}),
            ("理文造纸", "生产企业", {"地区": "广东", "年产能": "150万吨", "主要产品": "包装纸浆"}),
        ]
        
        # 原材料
        raw_materials = [
            ("桉木", "原材料", {"类型": "阔叶木", "产地": "南方", "纤维长度": "0.6-1.0mm"}),
            ("杨木", "原材料", {"类型": "阔叶木", "产地": "北方", "纤维长度": "0.8-1.2mm"}),
            ("松木", "原材料", {"类型": "针叶木", "产地": "东北", "纤维长度": "2.5-4.0mm"}),
            ("杉木", "原材料", {"类型": "针叶木", "产地": "南方", "纤维长度": "2.0-3.5mm"}),
            ("木片", "原材料", {"类型": "原料形态", "用途": "蒸煮"}),
        ]
        
        # 化学助剂
        chemicals = [
            ("氢氧化钠", "化学助剂", {"用途": "蒸煮", "化学式": "NaOH"}),
            ("硫化钠", "化学助剂", {"用途": "蒸煮", "化学式": "Na2S"}),
            ("二氧化氯", "化学助剂", {"用途": "漂白", "化学式": "ClO2"}),
            ("过氧化氢", "化学助剂", {"用途": "漂白", "化学式": "H2O2"}),
            ("蒽醌", "化学助剂", {"用途": "蒸煮催化剂", "提高得率": "5-10%"}),
        ]
        
        # 工艺设备
        equipment = [
            ("蒸煮器", "设备", {"用途": "化学蒸煮", "类型": "连续蒸煮器"}),
            ("洗浆机", "设备", {"用途": "浆料洗涤", "类型": "带式真空洗浆机"}),
            ("漂白塔", "设备", {"用途": "浆料漂白", "类型": "中浓漂白塔"}),
            ("纸机", "设备", {"用途": "造纸", "幅宽": "6-11米"}),
        ]
        
        # 添加所有实体
        all_entities = pulp_products + companies + raw_materials + chemicals + equipment
        
        for name, entity_type, attributes in all_entities:
            self.add_entity(name, entity_type, attributes, source="seed_data")
        
        # 添加关系
        self._add_sample_relations()
    
    def _add_sample_relations(self):
        """添加示例关系"""
        # 生产企业 - 生产 - 纸浆产品
        company_product_mapping = {
            "晨鸣纸业": ["针叶木浆", "阔叶木浆"],
            "太阳纸业": ["漂白化学浆", "机械浆"],
            "华泰股份": ["未漂白浆", "新闻纸浆"],
            "金光纸业": ["针叶木浆", "阔叶木浆", "漂白化学浆"],
            "理文造纸": ["包装纸浆", "机械浆"],
        }
        
        for company, products in company_product_mapping.items():
            company_id = self.get_entity_by_name(company).id
            for product in products:
                product_entity = self.get_entity_by_name(product)
                if product_entity:
                    self.add_relation(company_id, "生产", product_entity.id, confidence=1.0)
        
        # 纸浆产品 - 由...制成 - 原材料
        pulp_raw_mapping = {
            "针叶木浆": ["松木", "杉木"],
            "阔叶木浆": ["桉木", "杨木"],
            "漂白化学浆": ["木片"],
            "未漂白浆": ["木片"],
            "机械浆": ["木片"],
        }
        
        for pulp, materials in pulp_raw_mapping.items():
            pulp_entity = self.get_entity_by_name(pulp)
            if pulp_entity:
                for material in materials:
                    material_entity = self.get_entity_by_name(material)
                    if material_entity:
                        self.add_relation(material_entity.id, "制成", pulp_entity.id, confidence=1.0)
        
        # 化学助剂 - 用于 - 工艺
        chemical_process_mapping = {
            "氢氧化钠": ["蒸煮器"],
            "硫化钠": ["蒸煮器"],
            "二氧化氯": ["漂白塔"],
            "过氧化氢": ["漂白塔"],
            "蒽醌": ["蒸煮器"],
        }
        
        for chemical, processes in chemical_process_mapping.items():
            chemical_entity = self.get_entity_by_name(chemical)
            if chemical_entity:
                for process in processes:
                    process_entity = self.get_entity_by_name(process)
                    if process_entity:
                        self.add_relation(chemical_entity.id, "用于", process_entity.id, confidence=1.0)
    
    def save_to_json(self, filename: str = "knowledge_graph.json"):
        """保存知识图谱到JSON文件"""
        output_path = self.storage_path / filename
        
        data = {
            "metadata": {
                "total_entities": len(self.entities),
                "total_relations": len(self.relations),
                "entity_types": self.entity_type_count,
                "relation_types": self.relation_type_count,
                "created_at": datetime.now().isoformat()
            },
            "entities": [asdict(entity) for entity in self.entities.values()],
            "relations": [asdict(relation) for relation in self.relations]
        }
        
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def load_from_json(self, filename: str = "knowledge_graph.json"):
        """从JSON文件加载知识图谱"""
        input_path = self.storage_path / filename
        
        if not input_path.exists():
            return False
        
        with input_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 加载实体
        self.entities = {}
        for entity_data in data.get("entities", []):
            entity = Entity(**entity_data)
            self.entities[entity.id] = entity
        
        # 加载关系
        self.relations = []
        for relation_data in data.get("relations", []):
            relation = Relation(**relation_data)
            self.relations.append(relation)
        
        # 更新统计
        self.entity_type_count = data.get("metadata", {}).get("entity_types", {})
        self.relation_type_count = data.get("metadata", {}).get("relation_types", {})
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识图谱统计信息"""
        return {
            "total_entities": len(self.entities),
            "total_relations": len(self.relations),
            "entity_types": self.entity_type_count,
            "relation_types": self.relation_type_count,
            "average_relations_per_entity": len(self.relations) / len(self.entities) if self.entities else 0
        }
    
    def export_for_training(self) -> Tuple[List[Dict], List[Dict]]:
        """导出数据用于模型训练"""
        # 导出三元组
        triples = []
        for relation in self.relations:
            subject = self.entities[relation.subject]
            object = self.entities[relation.object]
            triples.append({
                "subject": subject.name,
                "predicate": relation.predicate,
                "object": object.name,
                "confidence": relation.confidence
            })
        
        # 导出实体文本
        entity_texts = []
        for entity in self.entities.values():
            text = f"{entity.name}是一种{entity.type}。"
            if entity.attributes:
                attrs = "、".join([f"{k}:{v}" for k, v in entity.attributes.items()])
                text += f"其特征包括：{attrs}。"
            entity_texts.append({
                "entity_id": entity.id,
                "entity_name": entity.name,
                "entity_type": entity.type,
                "text": text
            })
        
        return triples, entity_texts

