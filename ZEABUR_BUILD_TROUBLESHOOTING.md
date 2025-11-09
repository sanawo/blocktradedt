# Zeabur 构建问题排查指南

## 🔍 如何查看构建日志

### 1. 在 Zeabur Dashboard 中查看

1. 访问 [Zeabur Dashboard](https://dash.zeabur.com)
2. 进入你的项目
3. 点击服务名称（如 `blocktradedt`）
4. 点击 **"Deployments"** 标签
5. 点击最新的部署记录
6. 查看 **"Build Logs"**（构建日志）

### 2. 常见构建错误及解决方案

#### ❌ 错误：`No Dockerfile found` 或 `Cannot detect project type`

**原因**：Zeabur 无法识别项目类型

**解决方案**：
- ✅ 已添加 `zbpack.json` 明确指定 Python 项目
- ✅ 已添加 `.zeaburrc` 指定使用 Dockerfile
- ✅ 确保 `Dockerfile` 在项目根目录

#### ❌ 错误：`pip install failed` 或依赖安装失败

**可能原因**：
1. 依赖版本冲突
2. 网络问题
3. 缺少系统依赖

**解决方案**：
```bash
# 检查 requirements.txt 中的依赖
# 确保所有依赖版本兼容
# 已优化 Dockerfile 添加了 pip upgrade
```

#### ❌ 错误：`ModuleNotFoundError` 或导入错误

**可能原因**：
1. Python 路径问题
2. 缺少 `__init__.py` 文件
3. 模块导入顺序问题

**解决方案**：
- ✅ 已修复 `api/index.py` 中的导入问题
- ✅ 已添加路径设置

#### ❌ 错误：`Port already in use` 或端口冲突

**解决方案**：
- ✅ Dockerfile 已配置使用 `${PORT}` 环境变量
- ✅ Zeabur 会自动设置 PORT 环境变量

#### ❌ 错误：`Health check failed`

**解决方案**：
- ✅ 已优化健康检查端点 `/health`
- ✅ 已增加启动等待时间（start-period: 60s）

## 📋 构建配置检查清单

### ✅ 必需文件

- [x] `Dockerfile` - 在项目根目录
- [x] `requirements.txt` - Python 依赖
- [x] `zbpack.json` - Zeabur 构建配置
- [x] `.zeaburrc` - Zeabur 配置文件
- [x] `api/index.py` - 主应用文件

### ✅ 配置验证

1. **Dockerfile 检查**：
   ```dockerfile
   FROM python:3.11-slim  # ✅ 使用 Python 3.11
   WORKDIR /app            # ✅ 工作目录设置
   EXPOSE 8000             # ✅ 端口暴露
   ```

2. **zbpack.json 检查**：
   ```json
   {
     "type": "python",     # ✅ 明确指定类型
     "start_command": "...", # ✅ 启动命令
     "python_version": "3.11" # ✅ Python 版本
   }
   ```

3. **启动命令检查**：
   ```bash
   python -m uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8000}
   ```

## 🚀 手动触发重新构建

### 方法 1：通过 Dashboard

1. 进入 Zeabur Dashboard
2. 选择你的服务
3. 点击 **"Redeploy"** 按钮
4. 等待构建完成（5-10 分钟）

### 方法 2：通过 Git 推送

```bash
# 创建一个空提交来触发重新构建
git commit --allow-empty -m "trigger rebuild"
git push origin master
```

## 🔧 如果构建仍然失败

### 步骤 1：查看完整的构建日志

在 Zeabur Dashboard 中：
1. 进入服务 → Deployments
2. 点击失败的部署
3. 复制完整的 Build Logs
4. 查找错误信息（通常以 `ERROR` 或 `FAILED` 开头）

### 步骤 2：本地测试构建

```bash
# 在本地测试 Docker 构建
docker build -t blocktradedt-test .
docker run -p 8000:8000 -e PORT=8000 blocktradedt-test
```

如果本地构建成功，问题可能在 Zeabur 环境。

### 步骤 3：简化配置测试

如果构建仍然失败，可以尝试：

1. **简化 Dockerfile**：
   - 移除健康检查
   - 使用最简单的启动命令

2. **检查依赖**：
   - 确保 `requirements.txt` 中所有依赖都可用
   - 移除可能有问题的依赖

3. **联系支持**：
   - Zeabur Discord: https://discord.gg/zeabur
   - 提供构建日志和错误信息

## 📊 当前配置状态

### ✅ 已完成的优化

1. ✅ 添加 `type: "python"` 到 `zbpack.json`
2. ✅ 创建 `.zeaburrc` 明确指定使用 Dockerfile
3. ✅ 优化 Dockerfile：
   - 添加环境变量优化
   - 升级 pip
   - 优化缓存层
   - 增加健康检查等待时间
4. ✅ 修复应用代码中的导入问题
5. ✅ 增强错误处理和日志

### 📝 下一步

1. **等待自动部署**（5-10 分钟）
2. **查看构建日志**确认是否成功
3. **如果失败**，复制错误信息并按照上述步骤排查

## 🆘 需要帮助？

如果构建仍然失败，请提供：
1. 完整的构建日志（Build Logs）
2. 错误信息截图
3. 部署 ID 或时间戳

这样我可以更准确地帮你解决问题。

