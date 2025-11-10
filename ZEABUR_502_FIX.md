# 🔧 Zeabur 502错误完整修复指南

## 🔍 问题诊断

502错误表示：
- **服务无响应** - 应用可能未启动
- **端口配置错误** - 应用监听端口与Zeabur期望的不一致
- **应用崩溃** - 启动时发生错误导致容器退出
- **健康检查失败** - 应用启动但健康检查未通过

## ✅ 已实施的修复

### 1. **简化Dockerfile启动命令**
   - ✅ 移除了复杂的启动脚本
   - ✅ 直接使用uvicorn启动
   - ✅ 使用环境变量`${PORT}`（Zeabur自动设置）

### 2. **改进错误处理** (`api/index.py`)
   - ✅ 所有导入都有错误处理
   - ✅ 数据库初始化有后备方案
   - ✅ 详细的启动日志

### 3. **健康检查配置**
   - ✅ Dockerfile中配置了健康检查
   - ✅ `/health`端点返回详细状态

### 4. **Zeabur配置文件**
   - ✅ 创建了`.zeaburrc`配置文件
   - ✅ 明确指定启动命令

## 🚀 部署步骤

### 步骤1: 提交所有更改

```bash
git add .
git commit -m "fix: 简化启动命令，修复502错误

- 简化Dockerfile CMD命令
- 添加.zeaburrc配置文件
- 确保端口配置正确"
git push origin master
```

### 步骤2: 在Zeabur控制台检查配置

1. 访问: https://dash.zeabur.com
2. 进入你的项目
3. 点击 `blocktradedt` 服务
4. 进入 **"Settings"** 标签

#### 检查以下配置：

**端口设置**:
- Zeabur会自动设置`PORT`环境变量（通常为 `8080`）
- 应用会自动使用 `${PORT}` 环境变量，无需手动配置

**环境变量**（可选）:
```
DATABASE_URL=sqlite:///./block_trade_dt.db
JWT_SECRET_KEY=your-secret-key-here
```

**启动命令**:
- 应该自动检测到: `python -m uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8080}`
- 如果不同，手动设置为上述命令

### 步骤3: 触发重新部署

**方法1: 自动部署（推荐）**
- 推送代码后，Zeabur会自动检测并开始部署
- 等待2-3分钟

**方法2: 手动触发**
1. 在Zeabur控制台
2. 点击服务
3. 点击 **"Redeploy"** 按钮

### 步骤4: 监控部署日志

1. 在Zeabur控制台
2. 点击最新部署
3. 查看 **"Build Logs"** 和 **"Runtime Logs"**

**期望看到的日志**:
```
🚀 正在初始化应用...
✅ FastAPI 导入成功
✅ SQLAlchemy 导入成功
✅ Models 导入成功
✅ Schemas 导入成功
✅ Config 导入成功
✅ PyJWT 导入成功
✅ 数据库初始化成功
✅ 静态文件目录已挂载
✅ 模板目录已加载
==================================================
✅ 应用初始化完成！
📊 数据库状态: 已初始化
🔍 Retriever可用: True
🤖 LLM可用: True
📁 模板系统: 已加载
==================================================
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

### 步骤5: 验证部署

**测试健康检查**:
```bash
curl https://www.blocktradedt.xyz/health
```

**期望响应**:
```json
{
  "status": "healthy",
  "service": "Block Trade DT",
  "database": "ok",
  "retriever_available": true,
  "llm_available": true,
  "timestamp": "2024-..."
}
```

**测试主页**:
访问: https://www.blocktradedt.xyz/

应该看到正常的网站界面。

## 🔍 如果仍然出现502错误

### 1. 检查部署日志

在Zeabur控制台查看详细的错误信息：

**常见错误及解决方案**:

#### ❌ `ModuleNotFoundError`
```
ModuleNotFoundError: No module named 'xxx'
```
**解决方案**:
- 检查`requirements.txt`是否包含所有依赖
- 确保所有依赖都已正确安装

#### ❌ `Port already in use`
```
Address already in use
```
**解决方案**:
- 确保使用`${PORT}`环境变量
- 检查Zeabur端口配置

#### ❌ `ImportError`
```
ImportError: cannot import name 'xxx'
```
**解决方案**:
- 检查`api/index.py`中的导入路径
- 确保所有模块文件存在

#### ❌ `Database initialization failed`
```
❌ 数据库初始化失败
```
**解决方案**:
- 应用会自动切换到内存数据库
- 检查`DATABASE_URL`环境变量

### 2. 检查容器状态

在Zeabur控制台：
1. 查看服务状态
2. 如果显示"重启中"或"失败"，查看日志
3. 检查资源使用情况（内存、CPU）

### 3. 检查端口配置

**在Zeabur服务设置中**:
- **端口**: Zeabur会自动设置 `PORT` 环境变量（通常为 `8080`）
- **协议**: `HTTP`

**验证方法**:
在部署日志中查找：
```
Uvicorn running on http://0.0.0.0:8080
```
应用会自动使用 Zeabur 设置的端口。

### 4. 检查启动命令

**正确的启动命令**:
```bash
python -m uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8080} --log-level info
```

**在Zeabur服务设置中验证**:
1. 进入服务设置
2. 查看"Start Command"
3. 确保与上述命令一致

### 5. 手动测试应用

如果本地可以运行，但Zeabur不行：

**本地测试**:
```bash
# 设置端口（模拟Zeabur环境）
export PORT=8080

# 启动应用
python -m uvicorn api.index:app --host 0.0.0.0 --port $PORT

# 测试健康检查
curl http://localhost:8080/health
```

如果本地也失败，说明代码有问题，需要先修复。

## 📋 检查清单

部署前确保：
- [ ] `Dockerfile`存在且正确
- [ ] `requirements.txt`包含所有依赖
- [ ] `api/index.py`存在且可导入
- [ ] `.zeaburrc`配置文件存在
- [ ] 代码已推送到GitHub
- [ ] Zeabur服务配置正确

部署后验证：
- [ ] 部署状态为"运行中"（绿色）
- [ ] `/health`端点返回200
- [ ] 主页可以访问
- [ ] 没有502错误

## 🎯 快速修复命令

如果问题持续，尝试以下步骤：

```bash
# 1. 确保所有文件已提交
git add .
git commit -m "fix: 修复502错误"
git push origin master

# 2. 在Zeabur控制台手动触发重新部署
# 3. 等待3-5分钟
# 4. 检查部署日志
# 5. 测试健康检查端点
```

## 📞 获取帮助

如果以上步骤都无法解决问题：

1. **收集信息**:
   - 完整的部署日志（Build Logs + Runtime Logs）
   - 错误消息截图
   - Zeabur服务配置截图

2. **检查点**:
   - 应用是否成功启动？
   - 端口是否正确监听？
   - 健康检查是否通过？
   - 是否有内存/CPU限制？

3. **联系支持**:
   - Zeabur支持: https://zeabur.com/docs
   - 查看Zeabur文档: https://zeabur.com/docs

## 🔄 回滚方案

如果新部署导致问题：

1. 在Zeabur控制台
2. 进入"Deployments"标签
3. 找到之前成功的部署
4. 点击"Redeploy"恢复到旧版本

---

**最后更新**: 2024-12-19  
**状态**: 等待部署验证

