# 快速入门指南

## 概述

本指南将帮助您快速开始使用纸浆领域知识图谱与智能检索系统。

## 安装步骤

### 1. 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 验证安装

```bash
python -c "import numpy, fastapi; print('安装成功')"
```

## 快速开始

### 方法1：运行演示脚本（推荐）

演示脚本会自动展示所有核心功能：

```bash
python scripts/demo_enhanced_retrieval.py
```

这将依次演示：
1. 知识图谱构建
2. 结构化模式提示器
3. 数据增强
4. BART微调
5. 增强检索
6. 意图分类
7. 完整工作流程

### 方法2：使用Python API

#### 示例1：构建知识图谱

```python
from app.kg_builder import KnowledgeGraphBuilder

# 创建知识图谱构建器
kg = KnowledgeGraphBuilder()

# 加载种子数据
kg.load_pulp_domain_seed_data()

# 查看统计信息
stats = kg.get_statistics()
print(f"实体数: {stats['total_entities']}")
print(f"关系数: {stats['total_relations']}")

# 保存知识图谱
kg.save_to_json("my_kg.json")
```

#### 示例2：执行智能检索

```python
from app.enhanced_retriever import EnhancedRetriever

# 创建检索器（会自动加载知识图谱）
retriever = EnhancedRetriever()

# 执行搜索
results = retriever.search("针叶木浆的生产工艺", top_k=5)

# 查看结果
for i, result in enumerate(results, 1):
    print(f"{i}. {result['entity_name']} - {result['entity_type']}")
    print(f"   得分: {result['final_score']:.2f}")
```

#### 示例3：识别查询意图

```python
from app.intent_classifier import IntentClassifier

# 创建分类器
classifier = IntentClassifier()

# 分析查询
query = "针叶木浆的白度是多少？"
result = classifier.parse_query(query)

print(f"查询: {query}")
print(f"意图: {result['intent']}")
print(f"置信度: {result['confidence']:.2f}")
print(f"实体: {result['entities']}")
print(f"属性: {result['attributes']}")
```

#### 示例4：生成结构化提示

```python
from app.pattern_prompter import StructuredPatternPrompter

# 创建提示器
prompter = StructuredPatternPrompter()

# 生成提示
text = "针叶木浆是一种高质量纸浆，由松木制成"
prompt = prompter.generate_prompt("pulp_domain", text)

print("生成的提示:")
print(prompt)
```

#### 示例5：数据增强

```python
from app.data_augmentation import DataAugmentation

# 创建增强器
augmenter = DataAugmentation()

# 增强文本
text = "针叶木浆具有高白度和高强度特性"
augmented = augmenter.augment(text)

print(f"原始: {text}")
for i, aug_text in enumerate(augmented, 1):
    print(f"增强{i}: {aug_text}")
```

### 方法3：启动Web API服务

#### 启动服务

```bash
# 使用uvicorn启动
uvicorn app.enhanced_main:app --host 0.0.0.0 --port 8002

# 或直接运行
python app/enhanced_main.py
```

服务启动后，访问：http://localhost:8002/docs 查看API文档

#### 测试API

使用curl测试：

```bash
# 继续检索
curl -X POST "http://localhost:8002/api/enhanced/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "针叶木浆生产工艺", "top_k": 5, "use_llm": true}'

# 意图分析
curl -X POST "http://localhost:8002/api/search/intent?query=针叶木浆的白度是多少"

# 知识图谱统计
curl "http://localhost:8002/api/kg/statistics"
```

使用Python requests：

```python
import requests

# 继续检索
response = requests.post(
    "http://localhost:8002/api/enhanced/search",
    json={"query": "针叶木浆生产工艺", "top_k": 5, "use_llm": True}
)
print(response.json())

# 意图分析
response = requests.post(
    "http://localhost:8002/api/search/intent",
    params={"query": "针叶木浆的白度是多少"}
)
print(response.json())
```

## 主要API端点

### 智能检索

```
POST /api/enhanced/search
Body: {
    "query": "查询文本",
    "top_k": 10,
    "use_llm": true
}
```

### 意图分析

```
POST /api/search/intent?query=查询文本
```

### 知识图谱统计

```
GET /api/kg/statistics
```

### 获取实体信息

```
GET /api/kg/entity/{entity_name}
```

### 查询扩展

```
POST /api/search/expand?query=查询文本
```

### 知识提取

```
POST /api/pattern/extract?pattern_name=pulp_domain&text=文本内容
```

### 列出模式

```
GET /api/patterns
```

## 常见使用场景

### 场景1：快速检索

```python
from app.enhanced_retriever import EnhancedRetriever

retriever = EnhancedRetriever()
results = retriever.search("什么是针叶木浆", top_k=3)
print(results[0]['entity_name'])
```

### 场景2：了解实体关系

```python
from app.kg_builder import KnowledgeGraphBuilder

kg = KnowledgeGraphBuilder()
kg.load_pulp_domain_seed_data()

entity = kg.get_entity_by_name("针叶木浆")
relations = kg.get_relations(entity.id)

for rel in relations:
    print(f"{entity.name} {rel.predicate} ...")
```

### 场景3：批量知识提取

```python
from app.pattern_prompter import StructuredPatternPrompter

prompter = StructuredPatternPrompter()
texts = ["文本1", "文本2", "文本3"]

for text in texts:
    prompt = prompter.generate_prompt("pulp_domain", text)
    # 使用LLM处理prompt...
```

### 场景4：数据增强

```python
from app.data_augmentation import DataAugmentation

augmenter = DataAugmentation()
training_texts = ["原始文本1", "原始文本2"]

enhanced = []
for text in training_texts:
    enhanced.extend(augmenter.augment(text))
```

## 配置说明

### 知识图谱存储位置

默认存储在 `data/kg/` 目录下

### 模型配置

如需使用BART微调，需要：
1. 安装transformers和torch
2. 配置GPU环境（可选）
3. 运行训练脚本

### 自定义领域适配

修改以下文件以适配您的领域：

1. `app/pattern_prompter.py` - 添加新的模式
2. `app/kg_builder.py` - 添加领域实体和关系
3. `app/data_augmentation.py` - 添加领域同义词
4. `app/intent_classifier.py` - 添加意图模式

## 故障排除

### 问题1：导入错误

**症状：** `ModuleNotFoundError`

**解决：**
```bash
pip install -r requirements.txt
```

### 问题2：知识图谱不存在

**症状：** `FileNotFoundError`

**解决：**
系统会自动创建种子数据，或手动运行：
```python
from app.kg_builder import KnowledgeGraphBuilder
kg = KnowledgeGraphBuilder()
kg.load_pulp_domain_seed_data()
kg.save_to_json()
```

### 问题3：API服务无法启动

**症状：** 端口被占用

**解决：**
```bash
# 使用其他端口
uvicorn app.enhanced_main:app --port 8003
```

## 下一步

1. 查看完整文档：`ENHANCED_RETRIEVAL_README.md`
2. 阅读系统设计：`SYSTEM_DESIGN_SUMMARY.md`
3. 探索源代码：`app/` 目录
4. 运行演示：`scripts/demo_enhanced_retrieval.py`

## 支持

如有问题，请：
1. 查看文档
2. 运行演示脚本
3. 提交Issue

祝使用愉快！

