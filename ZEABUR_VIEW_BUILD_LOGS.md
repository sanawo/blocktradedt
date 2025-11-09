# 🔍 Zeabur 构建日志查看指南

## ❌ 问题：查看不到构建日志

如果你在 Zeabur Dashboard 中看不到构建日志，可能是以下原因：

### 1. 构建还没有开始

**症状**：Deployments 页面显示"Pending"或没有新的部署记录

**解决方案**：
- 等待 2-3 分钟让 Zeabur 检测到新的 Git 提交
- 或者手动触发构建（见下方）

### 2. 构建被删除或失败太快

**症状**：看到部署记录但状态是"Deleted"或"Failed"，点击后看不到日志

**解决方案**：
- 点击部署记录，尝试展开"Build Logs"部分
- 如果看不到，尝试刷新页面
- 查看"Runtime Logs"（运行时日志）而不是"Build Logs"

### 3. 权限问题

**症状**：无法访问部署详情页面

**解决方案**：
- 确认你有项目的访问权限
- 尝试退出并重新登录 Zeabur

## 📋 详细步骤：如何查看构建日志

### 方法 1：通过 Zeabur Dashboard（推荐）

1. **访问 Dashboard**
   ```
   https://dash.zeabur.com
   ```

2. **进入项目**
   - 点击左侧菜单中的项目名称
   - 或直接访问：`https://dash.zeabur.com/projects/[你的项目名]`

3. **选择服务**
   - 在项目页面中，点击你的服务名称（如 `blocktradedt`）

4. **查看部署记录**
   - 点击顶部菜单中的 **"Deployments"** 标签
   - 你会看到所有部署记录的列表

5. **查看构建日志**
   - 点击最新的部署记录（通常是第一个）
   - 在详情页面中，找到 **"Build Logs"** 部分
   - 点击展开查看完整的构建日志

6. **查看运行时日志**
   - 如果构建成功但应用崩溃，查看 **"Runtime Logs"** 部分
   - 这里会显示应用运行时的错误信息

### 方法 2：通过 API（高级）

如果你有 Zeabur API Token，可以通过 API 获取日志：

```bash
# 获取部署列表
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.zeabur.com/projects/[project_id]/services/[service_id]/deployments

# 获取特定部署的日志
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.zeabur.com/projects/[project_id]/services/[service_id]/deployments/[deployment_id]/logs
```

## 🚀 手动触发构建

如果构建没有自动触发，可以手动触发：

### 方法 1：通过 Dashboard

1. 进入服务页面
2. 点击 **"Redeploy"** 按钮（通常在右上角）
3. 选择要部署的分支（通常是 `master` 或 `main`）
4. 点击确认

### 方法 2：通过 Git 推送

运行以下命令创建一个空提交来触发构建：

```bash
# Windows (PowerShell)
git commit --allow-empty -m "chore: trigger rebuild"
git push origin master

# 或使用提供的脚本
.\trigger_zeabur_build.bat
```

## 🔧 常见构建错误及解决方案

### ❌ 错误：`No Dockerfile found`

**原因**：Zeabur 无法找到 Dockerfile

**解决方案**：
- ✅ 确保 `Dockerfile` 在项目根目录
- ✅ 确保文件名大小写正确（`Dockerfile`，不是 `dockerfile`）
- ✅ 检查 `.dockerignore` 没有排除 Dockerfile

### ❌ 错误：`Build timeout` 或构建超时

**原因**：构建时间过长（超过 20 分钟）

**解决方案**：
- 优化 Dockerfile，减少构建步骤
- 使用更小的基础镜像
- 检查是否有大量文件被复制到镜像中

### ❌ 错误：`pip install failed`

**原因**：依赖安装失败

**解决方案**：
- 检查 `requirements.txt` 中的依赖版本
- 确保所有依赖都可用
- 查看构建日志中的具体错误信息

### ❌ 错误：`ModuleNotFoundError`

**原因**：应用代码导入错误

**解决方案**：
- 检查 `api/index.py` 中的导入语句
- 确保所有必需的 Python 文件都在项目中
- 检查 `__init__.py` 文件是否存在

## 📊 构建日志示例

正常的构建日志应该包含：

```
Step 1/10 : FROM python:3.11-slim
 ---> [hash]
Step 2/10 : WORKDIR /app
 ---> [hash]
...
Step 10/10 : CMD sh -c "..."
 ---> [hash]
Successfully built [image_id]
Successfully tagged [tag]
```

如果看到错误，通常会以 `ERROR` 或 `FAILED` 开头。

## 🆘 如果仍然看不到日志

如果按照上述步骤仍然看不到构建日志，请：

1. **截图**：截取 Zeabur Dashboard 的页面
2. **检查网络**：确认能正常访问 Zeabur
3. **联系支持**：
   - Zeabur Discord: https://discord.gg/zeabur
   - 提供项目名称、服务名称和部署时间

## 📝 检查清单

在查看构建日志之前，确认：

- [ ] 已登录 Zeabur Dashboard
- [ ] 有项目的访问权限
- [ ] 已选择正确的项目和服务
- [ ] 已点击"Deployments"标签
- [ ] 已点击最新的部署记录
- [ ] 已尝试展开"Build Logs"部分
- [ ] 已尝试刷新页面

## 🎯 快速诊断命令

在本地运行以下命令来诊断问题：

```bash
# 检查 Dockerfile 是否存在
ls -la Dockerfile

# 检查 requirements.txt 是否存在
ls -la requirements.txt

# 测试本地构建（如果安装了 Docker）
docker build -t test-build .

# 检查应用入口文件
ls -la api/index.py
```

如果本地构建成功，问题可能在 Zeabur 环境配置。

