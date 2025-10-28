"""
知识图谱可视化模块
支持查询结果的可视化展示，包含关联实体和关系链路
"""
from typing import List, Dict, Any, Optional
from app.kg_builder import KnowledgeGraphBuilder
import json


class KnowledgeGraphVisualizer:
    """知识图谱可视化器"""
    
    def __init__(self, kg_builder: KnowledgeGraphBuilder):
        self.kg_builder = kg_builder
    
    def visualize_query_results(self, entities: List[str], max_depth: int = 2) -> Dict[str, Any]:
        """
        可视化查询结果
        
        Args:
            entities: 实体名称列表
            max_depth: 最大搜索深度
        
        Returns:
            包含节点和边的可视化数据
        """
        nodes = []
        edges = []
        node_ids = {}  # 名称到ID的映射
        
        # 添加实体节点
        for entity_name in entities:
            entity = self.kg_builder.get_entity_by_name(entity_name)
            if entity:
                node_id = entity.id
                if node_id not in node_ids:
                    nodes.append({
                        'id': node_id,
                        'label': entity.name,
                        'type': entity.type,
                        'attributes': entity.attributes,
                        'group': entity.type,
                        'level': 0
                    })
                    node_ids[entity_name] = node_id
                
                # 查找关联实体
                self._add_related_entities(entity, nodes, edges, node_ids, max_depth, current_level=0)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'central_entities': entities
            }
        }
    
    def _add_related_entities(self, entity, nodes, edges, node_ids, max_depth, current_level):
        """递归添加关联实体"""
        if current_level >= max_depth:
            return
        
        entity_id = entity.id
        relations = self.kg_builder.get_relations(entity_id)
        
        for relation in relations:
            # 获取关联实体
            other_id = relation.object if relation.subject == entity_id else relation.subject
            other_entity = self.kg_builder.get_entity(other_id)
            
            if not other_entity:
                continue
            
            # 如果节点未添加，则添加
            if other_id not in node_ids:
                nodes.append({
                    'id': other_id,
                    'label': other_entity.name,
                    'type': other_entity.type,
                    'attributes': other_entity.attributes,
                    'group': other_entity.type,
                    'level': current_level + 1
                })
                node_ids[other_entity.name] = other_id
            
            # 添加边
            if (entity_id, other_id) not in [(e['from'], e['to']) for e in edges]:
                edges.append({
                    'from': entity_id,
                    'to': other_id,
                    'label': relation.predicate,
                    'type': relation.predicate,
                    'confidence': relation.confidence
                })
            
            # 递归添加（限制深度避免无限递归）
            if current_level < max_depth - 1:
                self._add_related_entities(other_entity, nodes, edges, node_ids, max_depth, current_level + 1)
    
    def get_entity_detail(self, entity_id: str) -> Dict[str, Any]:
        """获取实体详细信息"""
        entity = self.kg_builder.get_entity(entity_id)
        if not entity:
            return {}
        
        relations = self.kg_builder.get_relations(entity_id)
        
        return {
            'id': entity.id,
            'name': entity.name,
            'type': entity.type,
            'attributes': entity.attributes,
            'relations': [{
                'id': r.id,
                'predicate': r.predicate,
                'target': self.kg_builder.get_entity(r.object).name if self.kg_builder.get_entity(r.object) else r.object,
                'confidence': r.confidence
            } for r in relations],
            'source': entity.source,
            'created_at': entity.created_at
        }
    
    def find_shortest_path(self, from_entity: str, to_entity: str) -> Dict[str, Any]:
        """查找两个实体之间的最短路径"""
        from_obj = self.kg_builder.get_entity_by_name(from_entity)
        to_obj = self.kg_builder.get_entity_by_name(to_entity)
        
        if not from_obj or not to_obj:
            return {'path': [], 'exists': False}
        
        path = self._bfs_shortest_path(from_obj.id, to_obj.id)
        
        return {
            'from': from_entity,
            'to': to_entity,
            'path': path,
            'exists': len(path) > 0,
            'distance': len(path) - 1 if path else 0
        }
    
    def _bfs_shortest_path(self, start_id: str, end_id: str) -> List[str]:
        """广度优先搜索最短路径"""
        from collections import deque
        
        visited = set()
        queue = deque([(start_id, [start_id])])
        
        while queue:
            current_id, path = queue.popleft()
            
            if current_id == end_id:
                return path
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            # 获取当前实体的所有关系
            relations = self.kg_builder.get_relations(current_id)
            
            for relation in relations:
                neighbor_id = relation.object if relation.subject == current_id else relation.subject
                if neighbor_id not in visited:
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return []
    
    def generate_cytoscape_data(self, entities: List[str], max_depth: int = 2) -> Dict[str, Any]:
        """生成Cytoscape.js兼容的数据格式"""
        vis_data = self.visualize_query_results(entities, max_depth)
        
        elements = []
        
        # 添加节点
        for node in vis_data['nodes']:
            elements.append({
                'data': {
                    'id': node['id'],
                    'label': node['label'],
                    'type': node['type'],
                    'group': node['group'],
                    'level': node['level'],
                    'attributes': node.get('attributes', {})
                }
            })
        
        # 添加边
        for edge in vis_data['edges']:
            elements.append({
                'data': {
                    'id': f"{edge['from']}-{edge['to']}",
                    'source': edge['from'],
                    'target': edge['to'],
                    'label': edge['label'],
                    'type': edge['type']
                }
            })
        
        return {
            'elements': elements,
            'metadata': vis_data['metadata']
        }
    
    def export_network_json(self, entities: List[str], max_depth: int = 2, format: str = 'cytoscape') -> str:
        """导出网络JSON"""
        if format == 'cytoscape':
            data = self.generate_cytoscape_data(entities, max_depth)
        else:
            data = self.visualize_query_results(entities, max_depth)
        
        return json.dumps(data, ensure_ascii=False, indent=2)


class KGVisualizationHTML:
    """知识图谱可视化HTML生成器"""
    
    @staticmethod
    def generate_cytoscape_html(nodes: List[Dict], edges: List[Dict], div_id: str = 'cy') -> str:
        """生成Cytoscape.js可视化HTML"""
        nodes_json = json.dumps(nodes, ensure_ascii=False)
        edges_json = json.dumps(edges, ensure_ascii=False)
        
        html = f"""
        <div id="{div_id}" style="width:100%;height:600px;border:1px solid #ccc;"></div>
        
        <script src="https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js"></script>
        <script>
        var cy = cytoscape({{
            container: document.getElementById('{div_id}'),
            elements: {nodes_json}.concat({edges_json}),
            style: [
                {{
                    selector: 'node',
                    style: {{
                        'background-color': '#619B8A',
                        'label': 'data(label)',
                        'width': 40,
                        'height': 40,
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'color': '#fff',
                        'font-size': '10px'
                    }}
                }},
                {{
                    selector: 'edge',
                    style: {{
                        'width': 2,
                        'line-color': '#ccc',
                        'target-arrow-color': '#ccc',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '8px'
                    }}
                }}
            ],
            layout: {{
                name: 'cose',
                padding: 10
            }}
        }});
        </script>
        """
        
        return html
    
    @staticmethod
    def generate_d3_html(nodes: List[Dict], edges: List[Dict]) -> str:
        """生成D3.js可视化HTML"""
        # D3.js可视化HTML
        html = """
        <div id="kg-visualization"></div>
        
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <script>
        // D3.js visualization code
        var nodes = {{nodes}};
        var links = {{edges}};
        // ... D3.js implementation
        </script>
        """
        
        return html.replace('{{nodes}}', json.dumps(nodes)).replace('{{edges}}', json.dumps(edges))

