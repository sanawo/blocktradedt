# 高级功能使用指南

## 新增功能概览

✅ **自然语言复杂查询** - 支持"2025年Kruger收购对漂白针叶木浆价格的影响"等复杂查询
✅ **研报摘要生成** - 上传5000字以内行业研报，8秒内输出结构化摘要
✅ **知识图谱可视化** - 查询结果同步展示关联实体与关系链路，支持点击节点查看详情

## 1. 自然语言复杂查询

### 功能说明

支持复杂的自然语言查询，自动识别实体、事件、时间、关系等信息。

### 使用示例

```python
# POST /api/complex/query
{
    "query": "2025年Kruger收购对漂白针叶木浆价格的影响",
    "top_k": 10
}
```

### 返回内容

```json
{
    "success": true,
    "query": "2025年Kruger收购对漂白针叶木浆价格的影响",
    "parsed": {
        "query_type": "impact_analysis",
        "entities": [
            {"name": "Kruger", "type": "company"},
            {"name": "漂白针叶木浆", "type": "product"}
        ],
        "events": [{"type": "收购"}],
        "temporal": {"absolute_time": "2025"},
        "relationships": [...]
    },
    "kg_results": [...],
    "text_results": [...],
    "kg_paths": [...],
    "answer": "..."
}
```

### 特点

- ✅ 自动识别实体（公司、产品、地区）
- ✅ 自动识别事件类型（收购、涨价、停产等）
- ✅ 提取时间信息（年份、月份、相对时间）
- ✅ 识别关系类型（影响、导致、关联）
- ✅ 生成知识图谱查询
- ✅ 构建关联路径

## 2. 研报摘要生成

### 功能说明

上传行业研报文本，8秒内自动生成结构化摘要。

### API端点

#### 文本上传

```bash
# POST /api/report/summarize
curl -X POST "https://www.blocktradedt.xyz/api/report/summarize" \
  -H "Content-Type: application/json" \
  -d '{"report_text": "研报内容..."}'
```

#### 文件上传

```bash
# POST /api/report/summarize
curl -X POST "https://www.blocktradedt.xyz/api/report/summarize" \
  -F "file=@report.txt"
```

#### HTML格式摘要

```bash
# POST /api/report/summarize/html
curl -X POST "https://www.blocktradedt.xyz/api/report/summarize/html" \
  -d '{"report_text": "研报内容..."}'
```

### 返回内容

结构化摘要包含：

1. **标题** - 自动提取报告标题
2. **核心观点** - 提取主要观点和建议
3. **数据支撑** - 提取关键数据和数字
4. **趋势判断** - 提取趋势预测
5. **关键发现** - 提取重要发现
6. **风险分析** - 提取风险提示
7. **投资建议** - 提取建议和推荐
8. **置信度** - 摘要质量评分

示例：

```json
{
    "success": true,
    "processing_time": "1.23秒",
    "summary": {
        "title": "纸浆市场分析报告",
        "core_viewpoints": [
            "预计2025年针叶木浆价格将上涨10%",
            "阔叶木浆供需平衡，价格稳定"
        ],
        "data_support": [
            {"value": "10%", "type": "percentage"},
            {"value": "100万吨", "type": "volume"}
        ],
        "trend_judgment": "市场整体向好，价格稳中有升",
        "key_findings": [...],
        "risk_analysis": [...],
        "recommendations": [...],
        "confidence": 0.85
    }
}
```

### 处理速度

- ⚡ **8秒内**完成处理（5000字以内）
- 📊 自动提取结构化和非结构化信息
- 📈 高置信度摘要

### 文本要求

- 最大长度：5000字
- 格式：中文/英文
- 内容：行业研报、市场分析、政策解读等

## 3. 知识图谱可视化

### 功能说明

将查询结果以知识图谱的形式可视化，展示实体关联和关系链路。

### 使用方式

#### 后端API

```python
# POST /api/kg/visualize
{
    "entities": ["针叶木浆", "晨鸣纸业", "桉木"]
}
```

返回：

```json
{
    "success": true,
    "data": {
        "nodes": [
            {
                "id": "...",
                "label": "针叶木浆",
                "type": "纸浆产品",
                "level": 0
            },
            ...
        ],
        "edges": [
            {
                "from": "...",
                "to": "...",
                "label": "生产"
            },
            ...
        ]
    }
}
```

#### 前端使用

```javascript
// 加载Cytoscape.js
import KnowledgeGraphVisualizer from './kg_visualizer.js';

// 初始化可视化
const visualizer = new KnowledgeGraphVisualizer('kg-container');

// 加载数据
await visualizer.loadData(['针叶木浆', '晨鸣纸业']);

// 导出
visualizer.exportImage();  // 导出PNG
visualizer.exportJSON();  // 导出JSON
```

### 可视化特性

- 🎨 **颜色编码**：不同实体类型使用不同颜色
  - 纸浆产品：橙色
  - 生产企业：黄色
  - 原材料：米色
  - 化学助剂：红色

- 🔗 **关系线**：显示实体间的关系
- 📊 **布局自动优化**：使用力导向布局
- 🖱️ **交互式**：
  - 点击节点查看详情
  - 悬停显示工具提示
  - 拖拽节点

### 获取节点详情

```bash
# GET /api/kg/entity/{entity_id}/detail
curl "https://www.blocktradedt.xyz/api/kg/entity/12345/detail"
```

返回：

```json
{
    "success": true,
    "entity": {
        "id": "12345",
        "name": "针叶木浆",
        "type": "纸浆产品",
        "attributes": {
            "白度": "85-88",
            "强度": "高"
        },
        "relations": [...]
    }
}
```

### 查找路径

```bash
# POST /api/kg/path
curl -X POST "https://www.blocktradedt.xyz/api/kg/path" \
  -d '{"from_entity": "晨鸣纸业", "to_entity": "桉木"}'
```

返回两个实体间的最短路径。

## 完整示例

### 工作流程

1. **复杂查询**
   ```python
   POST /api/complex/query
   Query: "2025年Kruger收购对漂白针叶木浆价格的影响"
   ```

2. **获取知识图谱**
   ```python
   POST /api/kg/visualize
   Entities: ["Kruger", "漂白针叶木浆"]
   ```

3. **查看实体详情**
   ```python
   GET /api/kg/entity/{id}/detail
   ```

4. **上传研报摘要**
   ```python
   POST /api/report/summarize
   Text: "行业研报内容..."
   ```

### JavaScript完整示例

```html
<!DOCTYPE html>
<html>
<head>
    <script src="static/kg_visualizer.js"></script>
</head>
<body>
    <div id="kg-visualization" style="width:100%;height:600px;"></div>
    
    <button onclick="loadKG()">加载知识图谱</button>
    <button onclick="queryComplex()">复杂查询</button>
    <button onclick="uploadReport()">上传研报</button>
    
    <script>
        let visualizer;
        
        async function loadKG() {
            visualizer = new KnowledgeGraphVisualizer('kg-visualization');
            await visualizer.initialize();
            await visualizer.loadData(['针叶木浆', '晨鸣纸业']);
        }
        
        async function queryComplex() {
            const response = await fetch('/api/complex/query', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    query: '2025年Kruger收购对漂白针叶木浆价格的影响',
                    top_k: 10
                })
            });
            const result = await response.json();
            console.log('查询结果:', result);
        }
        
        async function uploadReport() {
            const text = '行业研报内容...';
            const response = await fetch('/api/report/summarize', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({report_text: text})
            });
            const summary = await response.json();
            console.log('摘要:', summary);
        }
    </script>
</body>
</html>
```

## 技术实现

### 复杂查询解析器

- 实体识别：正则 + 关键词
- 事件识别：预定义事件模式
- 时间提取：支持绝对和相对时间
- 关系提取：依赖解析

### 研报摘要生成器

- 分句处理：基于标点符号
- 关键词匹配：特定领域词汇
- 上下文提取：保留上下文信息
- 置信度计算：基于提取质量

### 知识图谱可视化

- 后端：构建节点和边数据
- 前端：Cytoscape.js渲染
- 交互：点击、悬停、拖拽
- 导出：PNG、JSON格式

## 性能指标

- **复杂查询**：<500ms响应时间
- **研报摘要**：8秒内处理5000字
- **可视化渲染**：<1秒加载时间
- **路径查找**：<100ms

## 注意事项

1. **文件大小**：研报摘要限制5000字
2. **处理时间**：复杂查询可能需要几秒
3. **知识图谱**：实体数量影响可视化性能
4. **浏览器**：建议使用现代浏览器（Chrome、Firefox、Edge）

## API端点汇总

```
POST /api/complex/query          # 复杂查询
POST /api/report/summarize       # 研报摘要（JSON）
POST /api/report/summarize/html  # 研报摘要（HTML）
POST /api/kg/visualize           # 可视化KG
GET  /api/kg/entity/{id}/detail  # 实体详情
POST /api/kg/path                # 查找路径
POST /api/kg/export              # 导出KG数据
```

## 下一步

- [ ] 优化可视化性能
- [ ] 支持更多事件类型
- [ ] 增强研报摘要质量
- [ ] 添加导出CSV功能

