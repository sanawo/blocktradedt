# 部署到 www.blocktradedt.xyz 指南

## 快速部署步骤

### 方法1：使用部署脚本（推荐）

```bash
# 双击运行或在命令行执行
deploy_to_website.bat
```

### 方法2：手动部署

#### 步骤1：推送到GitHub

打开命令行（PowerShell或CMD），在项目目录下执行：

```bash
# 进入项目目录
cd "C:\Users\ruoha\Desktop\共享"

# 推送到GitHub
git push origin master
```

**如果遇到网络问题，可以尝试：**

1. **配置代理（如果需要）：**
```bash
git config --global http.proxy http://127.0.0.1:1080
git config --global https.proxy http://127.0.0.1:1080
```

2. **使用SSH（如果已配置）：**
```bash
git remote set-url origin git@github.com:sanawo/blocktradedt.git
git push origin master
```

#### 步骤2：在Zeabur上触发部署

1. **访问Zeabur控制台**
   - 网址：https://dash.zeabur.com
   - 登录您的账户

2. **选择项目**
   - 找到并点击 `blocktradedt` 项目

3. **触发重新部署**
   - 点击 "Redeploy" 或 "重新部署" 按钮
   - 等待构建完成（约3-5分钟）

4. **查看部署状态**
   - 在 "Deployments" 页面查看构建日志
   - 确认部署成功

5. **验证部署**
   - 访问：https://www.blocktradedt.xyz
   - 测试新增功能

## 新增功能验证

部署完成后，您可以在网站上测试以下新功能：

### 1. 增强版搜索API

访问API文档：https://www.blocktradedt.xyz/docs

测试端点：
- `POST /api/enhanced/search` - 智能检索
- `POST /api/search/intent` - 查询意图分析
- `GET /api/kg/statistics` - 知识图谱统计

### 2. 使用curl测试

```bash
# 测试增强检索
curl -X POST "https://www.blocktradedt.xyz/api/enhanced/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "针叶木浆生产工艺", "top_k": 5, "use_llm": true}'

# 测试意图识别
curl -X POST "https://www.blocktradedt.xyz/api/search/intent?query=针叶木浆的白度是多少"

# 查看知识图谱统计
curl "https://www.blocktradedt.xyz/api/kg/statistics"
```

### 3. 使用Python测试

```python
import requests

# 测试增强检索
response = requests.post(
    "https://www.blocktradedt.xyz/api/enhanced/search",
    json={"query": "针叶木浆生产工艺", "top_k": 5, "use_llm": True}
)
print(response.json())
```

## 部署内容

本次更新包含：

### 核心模块
- ✅ 知识图谱构建系统
- ✅ 结构化模式提示器
- ✅ 数据增强模块
- ✅ BART模型微调器
- ✅ 增强版检索器
- ✅ 查询意图分类器

### 数据文件
- ✅ 纸浆领域知识图谱（20+实体，30+关系）
- ✅ 纸浆领域示例数据（20条）

### 文档
- ✅ ENHANCED_RETRIEVAL_README.md
- ✅ SYSTEM_DESIGN_SUMMARY.md
- ✅ QUICK_START_GUIDE.md

### API端点
- ✅ `/api/enhanced/search` - 增强检索
- ✅ `/api/search/intent` - 意图分析
- ✅ `/api/kg/statistics` - KG统计
- ✅ `/api/kg/entity/{name}` - 实体信息
- ✅ `/api/search/expand` - 查询扩展
- ✅ `/api/pattern/extract` - 知识提取
- ✅ `/api/patterns` - 模式列表

## 故障排除

### 问题1：推送失败

**症状：** `fatal: unable to access 'https://github.com/...'`

**解决方案：**
1. 检查网络连接
2. 配置代理
3. 使用SSH协议
4. 使用GitHub Desktop等图形工具

### 问题2：Zeabur未自动部署

**症状：** 推送成功但Zeabur未触发部署

**解决方案：**
1. 在Zeabur控制台手动点击 "Redeploy"
2. 检查项目的Git连接设置
3. 查看 "Settings" > "Git" 确认连接正常

### 问题3：部署失败

**症状：** 构建失败或应用无法启动

**查看日志：**
1. 在Zeabur控制台查看 "Build Logs"
2. 检查错误信息

**常见问题：**
- 依赖安装失败 → 检查 `requirements.txt`
- 端口配置错误 → 检查 `zbpack.json`
- 应用启动失败 → 检查 `startup.sh`

### 问题4：新功能不可用

**症状：** 部署成功但新API端点404

**解决方案：**
1. 确认使用的是 `app/enhanced_main.py` 而不是 `app/main.py`
2. 检查 `startup.sh` 中的启动命令
3. 重新部署

## 回滚操作

如果需要回滚到之前的版本：

### 方法1：在GitHub上回滚

```bash
# 回退到之前的commit
git reset --hard HEAD~1
git push origin master --force
```

### 方法2：在Zeabur上回滚

1. 访问Zeabur控制台
2. 找到之前的成功部署
3. 点击 "Redeploy"
4. 等待部署完成

## 最佳实践

### 1. 版本控制
- 每次部署前创建tag
- 保留重要版本的备份

### 2. 测试流程
- 本地测试后再推送
- 在测试环境验证
- 生产环境小规模测试

### 3. 监控
- 关注Zeabur的构建日志
- 监控网站运行状态
- 设置错误通知

## 联系支持

如遇到问题：
1. 查看Zeabur文档：https://zeabur.com/docs
2. 提交Issue到GitHub仓库
3. 联系技术支持

## 更新日志

### 2024-08-XX 重大更新

新增功能：
- 知识图谱构建与查询系统
- 增强版语义检索
- 查询意图识别
- 数据增强模块
- BART模型微调框架
- 完整的API文档

技术改进：
- 添加专业术语理解
- 优化检索算法
- 提升检索效率
- 改进答案生成质量

文档：
- 新增3篇详细文档
- 更新快速入门指南
- 添加API使用示例

