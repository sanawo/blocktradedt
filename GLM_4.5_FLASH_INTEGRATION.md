# GLM-4.5-Flash 集成指南

## 概述

已成功集成智谱AI的GLM-4.5-Flash模型到系统中，这是一个强大的新旗舰模型，具有：

- ✅ **128K上下文窗口** - 处理长文本和理解
- ✅ **深度思考模式** - 自动判断任务复杂度
- ✅ **流式输出支持** - 实时响应体验
- ✅ **工具调用能力** - 扩展应用场景
- ✅ **高性能低成本** - 免费开放使用

## 功能特性

### 1. 智能思考模式

GLM-4.5-Flash会根据任务复杂度自动启用或禁用思考模式：

- **简单任务**（问候、翻译等）：自动禁用思考，快速响应
- **复杂任务**（分析、预测、解释等）：自动启用思考，深度推理

示例：
```python
# 简单任务 - 自动禁用思考
"你好" → thinking.type = "disabled"

# 复杂任务 - 自动启用思考
"分析纸浆市场趋势" → thinking.type = "enabled"
```

### 2. 流式输出支持

支持实时流式响应，提升用户体验：

```python
# 启用流式输出
llm.chat(message, stream=True)
```

### 3. 长上下文处理

支持最长128K的上下文，适合：
- 长文档分析
- 多轮对话
- 结构化内容生成

## 配置方式

### 方法1：环境变量（推荐）

在部署环境中设置：

```bash
export ZHIPU_API_KEY="your-api-key-here"
```

或在Zeabur环境变量中添加：
```
ZHIPU_API_KEY=your-api-key-here
```

### 方法2：代码中配置

```python
from app.llm import LLM

llm = LLM(api_key="your-api-key", model="glm-4.5-flash")
```

## API使用

### 基础对话

```python
POST /api/chat
{
    "message": "分析纸浆市场趋势",
    "enable_thinking": true,  // 可选，默认true
    "stream": false           // 可选，默认false
}
```

### 带系统提示词

```python
POST /api/chat
{
    "message": "纸浆价格预测",
    "system_prompt": "你是一个专业的纸浆市场分析师",
    "enable_thinking": true
}
```

### 多轮对话

```python
POST /api/chat
{
    "message": "具体预测一下价格",
    "conversation_history": [
        {"role": "user", "content": "纸浆价格预测"},
        {"role": "assistant", "content": "根据当前市场..."}
    ]
}
```

## 思考模式说明

### 自动判断规则

系统会自动根据消息内容判断是否需要思考：

**启用思考的关键词：**
- 分析、预测、解释、为什么、如何
- 建议、策略、评估、判断

**禁用思考的关键词：**
- 你好、hello、谢谢、再见

### 手动控制

```python
# 强制启用思考
{"enable_thinking": true}

# 强制禁用思考
{"enable_thinking": false}
```

## 模型优势

### 性能指标

- **全球排名**：第2名（综合评测）
- **国产排名**：第1名
- **开源排名**：第1名

### 成本优势

- 输入：0.8元/百万tokens
- 输出：2元/百万tokens
- **完全免费开放使用**（glm-4.5-flash）

### 速度优势

- 生成速度：>100 tokens/秒
- 低延迟响应
- 支持高并发

## 推荐场景

### 1. 智慧办公

- PPT制作
- 内容创作
- 文档分析

### 2. 智能问答

- 市场分析
- 数据解读
- 趋势预测

### 3. 复杂文本翻译

- 长文档翻译
- 专业术语翻译

### 4. 网页搭建

- 代码生成
- 前端开发

## 代码示例

### Python调用

```python
from app.llm import LLM

# 初始化
llm = LLM(api_key="your-key", model="glm-4.5-flash")

# 基础对话
response = llm.chat("分析纸浆市场")

# 带思考模式
response = llm.chat(
    "详细解释MoE模型的工作原理",
    enable_thinking=True
)

# 流式输出
response = llm.chat(
    "生成一份市场报告",
    stream=True
)
```

### API调用

```bash
# 基础对话
curl -X POST "https://www.blocktradedt.xyz/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析纸浆市场趋势",
    "enable_thinking": true
  }'

# 流式输出（前端实现）
# 使用fetch API的stream模式
```

## 更新内容

### 文件更新

- ✅ `app/llm.py` - 集成GLM-4.5-Flash
- ✅ `app/schemas.py` - 添加思考模式和流式参数
- ✅ `api/index.py` - 更新API端点
- ✅ `requirements.txt` - 添加zai-sdk

### 新功能

- ✅ GLM-4.5-Flash模型支持
- ✅ 智能思考模式切换
- ✅ 流式输出支持
- ✅ 长上下文处理
- ✅ 向后兼容旧SDK

## 依赖安装

```bash
pip install zai-sdk>=0.0.4
```

或安装兼容版本：

```bash
pip install zhipuai>=2.0.0
```

## 向后兼容

系统会自动检测可用的SDK：

1. **优先使用**：zai-sdk（GLM-4.5-Flash）
2. **降级使用**：zhipuai（GLM-4-Flash）
3. **Fallback**：本地回复（无API密钥）

## 性能对比

### GLM-4.5-Flash vs GLM-4-Flash

| 特性 | GLM-4.5-Flash | GLM-4-Flash |
|------|---------------|-------------|
| 上下文窗口 | 128K | 32K |
| 思考模式 | ✅ 支持 | ❌ 不支持 |
| 生成速度 | >100 tokens/秒 | ~50 tokens/秒 |
| 成本 | 免费 | 付费 |
| 推理能力 | 更强 | 标准 |

## 使用建议

### 1. API密钥配置

**重要**：即使GLM-4.5-Flash免费，仍需要API密钥才能使用。

获取方式：
1. 访问智谱AI开放平台
2. 注册账号并获取API密钥
3. 设置环境变量 `ZHIPU_API_KEY`

### 2. 思考模式使用

- **简单查询**：自动禁用，快速响应
- **复杂分析**：自动启用，深度思考
- **手动控制**：通过`enable_thinking`参数

### 3. 流式输出

- 适合长文本生成
- 提升用户体验
- 前端需要处理流式响应

## 故障排除

### 问题1：AI服务不可用

**原因**：
- API密钥未配置
- SDK未安装

**解决**：
```bash
# 安装SDK
pip install zai-sdk

# 设置环境变量
export ZHIPU_API_KEY="your-key"
```

### 问题2：模型调用失败

**原因**：
- API密钥错误
- 网络问题
- SDK版本不兼容

**解决**：
- 检查API密钥格式
- 查看日志错误信息
- 系统会自动fallback到本地回复

### 问题3：思考模式不工作

**原因**：
- 使用的是旧版SDK
- 参数未正确传递

**解决**：
- 确保安装zai-sdk>=0.0.4
- 检查请求参数

## 最佳实践

### 1. 任务分类

```python
# 简单任务 - 快速响应
"你好" → enable_thinking=False

# 中等任务 - 适度思考
"市场趋势分析" → enable_thinking=True (默认)

# 复杂任务 - 深度思考
"根据数据预测未来走势" → enable_thinking=True
```

### 2. 上下文管理

```python
# 利用128K上下文窗口
# 传入完整的历史对话和上下文
llm.chat(
    message,
    context="完整的上下文信息...",
    conversation_history=[...]
)
```

### 3. 错误处理

```python
try:
    response = llm.chat(message)
except Exception as e:
    # 系统会自动fallback到本地回复
    print(f"AI调用失败，使用本地回复: {e}")
```

## 技术细节

### SDK选择

系统按以下顺序尝试：

1. `zai-sdk` - 最新SDK，支持GLM-4.5
2. `zhipuai` - 旧版SDK，兼容GLM-4
3. 本地回复 - 无SDK时的fallback

### 模型标识

- 新模型：`glm-4.5-flash`
- 旧模型：`glm-4-flash`

### 思考模式参数

```python
thinking = {
    "type": "enabled"   # 启用
    "type": "disabled"  # 禁用
}
```

## 更新日志

### 2024-08-XX

- ✅ 集成GLM-4.5-Flash模型
- ✅ 添加智能思考模式
- ✅ 支持流式输出
- ✅ 更新SDK到zai-sdk
- ✅ 保持向后兼容

## 参考资料

- [GLM-4.5-Flash 官方文档](https://open.bigmodel.cn/)
- [zai-sdk 文档](https://github.com/zhipuai/zai-sdk)
- [API接口文档](https://www.blocktradedt.xyz/docs)

---

**享受GLM-4.5-Flash的强大能力！🚀**




