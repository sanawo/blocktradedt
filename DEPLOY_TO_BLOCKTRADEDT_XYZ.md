# 部署到 www.blocktradedt.xyz

## 当前状态

✅ 本地代码已提交（commit hash: 1b23be0）
- 27个文件已更新
- 4130行新代码
- 包含知识图谱、增强检索等功能

## 部署步骤

### 步骤1：推送到GitHub

打开PowerShell或CMD，在项目目录下执行：

```bash
cd "C:\Users\ruoha\Desktop\共享"
git push origin master
```

**如果遇到网络问题，可以尝试：**

1. **检查网络连接**
   ```bash
   ping github.com
   ```

2. **使用GitHub Desktop（推荐）**
   - 下载安装：https://desktop.github.com/
   - 打开应用，找到blocktradedt项目
   - 点击"Push origin"按钮

3. **或者手动配置代理**
   ```bash
   git config --global http.proxy http://127.0.0.1:端口
   git config --global https.proxy http://127.0.0.1:端口
   ```

### 步骤2：在Zeabur上触发部署

#### 方法A：自动部署（推荐）

推送到GitHub后，Zeabur会自动检测到更新并开始部署。等待3-5分钟即可。

#### 方法B：手动触发部署

1. **访问Zeabur控制台**
   - 网址：https://dash.zeabur.com
   - 登录您的账户

2. **选择项目**
   - 找到并点击 `blocktradedt` 或相关项目

3. **触发重新部署**
   - 点击 "Redeploy" 或 "重新部署" 按钮
   - 等待构建完成

4. **查看日志**
   - 在 "Deployments" 页面查看构建日志
   - 确认部署成功

### 步骤3：验证部署

访问：https://www.blocktradedt.xyz

**测试新增功能：**

```bash
# 测试增强检索
curl -X POST "https://www.blocktradedt.xyz/api/enhanced/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "针叶木浆生产工艺", "top_k": 5, "use_llm": true}'

# 查看知识图谱统计
curl "https://www.blocktradedt.xyz/api/kg/statistics"

# 测试意图识别
curl -X POST "https://www.blocktradedt.xyz/api/search/intent?query=针叶木浆的白度是多少"
```

## 快速操作脚本

我已经创建了以下脚本帮助您：

### deploy_to_website.bat

双击运行此批处理文件，它会：
1. 检查Git状态
2. 推送到GitHub
3. 显示部署说明

## 部署内容

本次更新包含以下新功能：

### 新增模块
- ✅ `app/pattern_prompter.py` - 结构化模式提示器
- ✅ `app/kg_builder.py` - 知识图谱构建器
- ✅ `app/data_augmentation.py` - 数据增强模块
- ✅ `app/bart_finetuner.py` - BART微调器
- ✅ `app/enhanced_retriever.py` - 增强检索器
- ✅ `app/intent_classifier.py` - 意图分类器
- ✅ `app/enhanced_main.py` - 增强版主应用
- ✅ `api/enhanced_index.py` - 增强版API入口

### 新增数据
- ✅ `data/pulp_domain_data.jsonl` - 纸浆领域数据（20条）
- ✅ 知识图谱种子数据（20+实体，30+关系）

### 新增文档
- ✅ `ENHANCED_RETRIEVAL_README.md` - 完整使用文档
- ✅ `SYSTEM_DESIGN_SUMMARY.md` - 系统设计文档
- ✅ `QUICK_START_GUIDE.md` - 快速入门指南
- ✅ `WEBSITE_DEPLOYMENT_GUIDE.md` - 部署指南
- ✅ `DEPLOY_TO_BLOCKTRADEDT_XYZ.md` - 本文档

### 新增端点（如果使用增强版API）

如果使用 `api/enhanced_index.py`：

- `POST /api/enhanced/search` - 增强检索
- `POST /api/search/intent` - 意图分析
- `GET /api/kg/statistics` - KG统计
- `GET /api/kg/entity/{name}` - 实体信息
- `POST /api/search/expand` - 查询扩展
- `POST /api/pattern/extract` - 知识提取
- `GET /api/patterns` - 模式列表

## 注意事项

### 1. 默认使用原始API

当前部署使用的是 `api/index.py`，如果需要使用增强功能，需要：

**选项A：保留原功能，添加新端点**
- 在 `api/index.py` 中导入增强模块
- 添加新的API端点

**选项B：完全切换到增强版**
- 修改 `zbpack.json` 中的 `start_command`
- 改为使用 `api.enhanced_index:app`

### 2. 依赖安装

确保 `requirements.txt` 已更新，Zeabur会自动安装依赖。

### 3. 数据库兼容

增强功能使用独立的知识图谱，不需要修改现有数据库。

## 故障排除

### 推送失败

**问题：** `fatal: unable to access 'https://github.com/...'`

**解决方案：**
1. 检查网络连接
2. 使用SSH协议：`git remote set-url origin git@github.com:sanawo/blocktradedt.git`
3. 使用GitHub Desktop
4. 联系网络管理员配置代理

### 部署失败

**问题：** Zeabur构建失败

**检查：**
1. 查看构建日志
2. 确认 `requirements.txt` 正确
3. 检查端口配置

**解决方案：**
```bash
# 检查依赖
cat requirements.txt

# 查看日志
# 在Zeabur控制台查看"Build Logs"
```

### 功能不可用

**问题：** 部署成功但新功能404

**原因：** 使用的是原版API

**解决方案：**
1. 修改 `api/index.py` 添加新端点
2. 或切换到 `api/enhanced_index.py`

## 验证清单

部署完成后，验证以下内容：

- [ ] 网站可访问：https://www.blocktradedt.xyz
- [ ] 健康检查通过：https://www.blocktradedt.xyz/health
- [ ] API文档可访问：https://www.blocktradedt.xyz/docs
- [ ] 原功能正常：搜索、登录等
- [ ] 新功能可用（如果启用了增强版）

## 回滚

如果需要回滚到之前的版本：

```bash
# 回退到上一个commit
git reset --hard HEAD~1
git push origin master --force

# 在Zeabur上触发重新部署
```

## 联系支持

如有问题：
1. 查看日志：Zeabur控制台
2. 检查GitHub：https://github.com/sanawo/blocktradedt
3. 提交Issue

---

**下一步：**
1. 运行 `deploy_to_website.bat` 或手动推送
2. 在Zeabur控制台触发部署
3. 等待3-5分钟
4. 访问 https://www.blocktradedt.xyz 验证

