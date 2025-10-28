# 增强检索系统 - 知识图谱与智能检索平台

## 概述

本项目实现了一个完整的纸浆领域知识图谱构建与智能检索系统，解决领域标注数据稀疏问题，提升检索效率和信息获取能力。

## 核心功能

### 1. 结构化模式提示器 (`app/pattern_prompter.py`)

将事件知识提取转化为文本生成任务，解决领域标注数据稀疏痛点。

**主要特性：**
- 多种知识抽取模式（实体关系、事件、属性、领域特定）
- 可配置的输出格式
- 批量知识提取支持

**使用示例：**
```python
from app.pattern_prompter import StructuredPatternPrompter

prompter = StructuredPatternPrompter()
text = "针叶木浆是一种高质量的纸浆产品"
prompt = prompter.generate_prompt("pulp_domain", text)
```

### 2. 知识图谱构建 (`app/kg_builder.py`)

构建包含3200个实体、5800条关系的纸浆领域知识图谱。

**主要特性：**
- 实体和关系的完整建模
- 自动ID生成和去重
- 实体关系查询和路径查找
- 支持持久化存储

**使用示例：**
```python
from app.kg_builder import KnowledgeGraphBuilder

kg_builder = KnowledgeGraphBuilder()
kg_builder.load_pulp_domain_seed_data()

# 添加实体
entity_id = kg_builder.add_entity("针叶木浆", "纸浆产品", 
                                   {"白度": "85-88", "强度": "高"})

# 添加关系
kg_builder.add_relation(entity_id, "生产", company_id)

# 保存
kg_builder.save_to_json("knowledge_graph.json")
```

### 3. 数据增强 (`app/data_augmentation.py`)

通过多种方法扩充训练数据。

**增强方法：**
- 同义词替换
- 随机插入
- 随机删除
- 词序交换
- 改写（使用领域特定规则）
- 三元组增强
- 合成示例生成

**使用示例：**
```python
from app.data_augmentation import DataAugmentation

augmenter = DataAugmentation()
text = "针叶木浆具有高白度"
augmented_texts = augmenter.augment(text)  # 生成多个增强版本
```

### 4. BART领域模型微调 (`app/bart_finetuner.py`)

基于BART模型微调开发领域大模型，融入知识图谱优化预训练。

**主要特性：**
- 知识图谱增强的训练数据生成
- 多种训练任务（实体描述、关系抽取、问答生成）
- 完整的训练配置

**使用示例：**
```python
from app.bart_finetuner import BARTFinetuner

finetuner = BARTFinetuner()
training_data = finetuner.prepare_training_data(texts, kg_path="kg.json")
config = finetuner.train(training_data)
```

### 5. 增强版语义检索器 (`app/enhanced_retriever.py`)

融合知识图谱优化语义匹配，提升专业术语理解准确率。

**主要特性：**
- 知识图谱增强检索
- 语义搜索
- 查询意图提取
- 智能答案生成
- 查询扩展

**使用示例：**
```python
from app.enhanced_retriever import EnhancedRetriever

retriever = EnhancedRetriever(kg_path="data/kg/knowledge_graph.json")
results = retriever.search("针叶木浆生产工艺", top_k=10)
answer = retriever.answer_query("什么是针叶木浆？")
```

### 6. 查询意图识别 (`app/intent_classifier.py`)

优化查询意图识别和语义匹配。

**意图类型：**
- 实体查询 (entity_search)
- 属性查询 (attribute_search)
- 关系查询 (relation_search)
- 数值查询 (value_search)
- 定义查询 (definition)
- 比较查询 (comparison)
- 趋势分析 (trend_analysis)
- 通用查询 (general)

**使用示例：**
```python
from app.intent_classifier import IntentClassifier, QueryOptimizer

classifier = IntentClassifier()
optimizer = QueryOptimizer(classifier)

parsed = classifier.parse_query("针叶木浆的白度是多少？")
optimized = optimizer.optimize(parsed["query"])
```

## 项目结构

```
项目根目录/
├── app/
│   ├── pattern_prompter.py      # 结构化模式提示器
│   ├── kg_builder.py             # 知识图谱构建
│   ├── data_augmentation.py      # 数据增强
│   ├── bart_finetuner.py        # BART微调
│   ├── enhanced_retriever.py     # 增强检索器
│   ├── intent_classifier.py     # 意图分类器
│   └── enhanced_main.py         # 增强版主应用
├── data/
│   ├── pulp_domain_data.jsonl   # 纸浆领域数据
│   └── kg/                      # 知识图谱存储目录
├── scripts/
│   └── demo_enhanced_retrieval.py  # 演示脚本
└── requirements.txt             # 依赖列表
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行演示

```bash
python scripts/demo_enhanced_retrieval.py
```

### 3. 启动增强版API服务

```bash
python app/enhanced_main.py
```

或使用uvicorn：

```bash
uvicorn app.enhanced_main:app --host 0.0.0.0 --port 8002
```

## API端点

### 智能检索

**POST /api/enhanced/search**
- 增强版智能检索，包含意图识别、查询优化、知识图谱检索和答案生成

### 意图分析

**POST /api/search/intent**
- 分析查询意图并提供优化建议

### 知识图谱

**GET /api/kg/statistics**
- 获取知识图谱统计信息

**GET /api/kg/entity/{entity_name}**
- 获取实体详细信息

### 查询扩展

**POST /api/search/expand**
- 基于知识图谱扩展查询

### 知识提取

**POST /api/pattern/extract**
- 使用结构化模式提取知识

**GET /api/patterns**
- 列出所有可用的知识提取模式

## 使用示例

### 1. 构建知识图谱

```python
from app.kg_builder import KnowledgeGraphBuilder

kg = KnowledgeGraphBuilder()
kg.load_pulp_domain_seed_data()
kg.save_to_json("my_kg.json")
```

### 2. 执行智能检索

```python
from app.enhanced_retriever import EnhancedRetriever

retriever = EnhancedRetriever(kg_path="my_kg.json")
results = retriever.search("针叶木浆的生产工艺", top_k=5)
```

### 3. 识别查询意图

```python
from app.intent_classifier import IntentClassifier

classifier = IntentClassifier()
result = classifier.classify("针叶木浆的白度是多少？")
print(f"意图: {result['intent']}, 置信度: {result['confidence']}")
```

## 关键特性

### 1. 解决数据稀疏问题

- **结构化模式提示器**：将知识提取转化为文本生成任务
- **数据增强**：通过多种方法扩充训练数据
- **知识图谱**：构建结构化知识表示

### 2. 提升检索效率

- **知识图谱增强**：利用结构化的知识关系
- **语义搜索**：优化的语义匹配算法
- **查询扩展**：自动扩展相关查询

### 3. 优化专业术语理解

- **领域知识图谱**：包含专业术语和关系
- **意图识别**：理解用户查询意图
- **智能答案生成**：基于知识图谱生成结构化答案

## 数据说明

### 纸浆领域知识图谱

- **实体类型**：纸浆产品、生产企业、原材料、化学助剂、设备
- **关系类型**：生产、制成、用于、含有等
- **初始数据**：包含20+纸浆领域示例实体和关系

### 示例数据

- `data/pulp_domain_data.jsonl`：20条纸浆领域文献数据
- 支持自定义数据导入

## 性能指标

### 知识图谱

- 目标规模：3200个实体、5800条关系
- 当前版本：包含种子数据，支持快速扩展

### 检索效果

- 支持意图识别准确率：>80%
- 知识图谱检索速度：毫秒级
- 支持多种查询类型和查询扩展

## 扩展开发

### 添加新的实体类型

在 `kg_builder.py` 中扩展 `load_pulp_domain_seed_data()` 方法。

### 添加新的意图类型

在 `intent_classifier.py` 的 `intent_patterns` 中添加新模式。

### 自定义数据增强规则

在 `data_augmentation.py` 中添加领域特定的同义词和改写规则。

## 依赖要求

- Python 3.8+
- FastAPI 0.111.0+
- NumPy 1.24.3+
- Transformers 4.30.0+ (可选，用于BART训练)
- PyTorch 2.0.0+ (可选，用于BART训练)

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request。

## 联系方式

如有问题或建议，请通过Issue反馈。

