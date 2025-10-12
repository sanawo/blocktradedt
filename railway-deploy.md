# 🚀 Railway部署指南 - Block Trade DT

## 📋 为什么选择Railway？

✅ **完美支持Python/FastAPI**  
✅ **自动部署和扩展**  
✅ **免费额度充足**  
✅ **简单易用的界面**  
✅ **自动HTTPS和域名**  

## 🎯 部署步骤

### 第一步：准备项目

您的项目已经包含了所有必要的配置文件：
- ✅ `railway.json` - Railway配置
- ✅ `Procfile` - 启动命令
- ✅ `requirements.txt` - Python依赖
- ✅ `app/main.py` - FastAPI应用

### 第二步：创建Railway账户

1. 访问 [Railway.app](https://railway.app)
2. 点击 "Login" 使用GitHub账户登录
3. 完成账户设置

### 第三步：连接GitHub仓库

1. 在Railway Dashboard中点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 授权Railway访问您的GitHub仓库
4. 选择您的项目仓库

### 第四步：配置环境变量

在Railway Dashboard中设置以下环境变量：

```
ZHIPU_API_KEY=7aee1f12feb24b5f8c298d445ddc6923.IphCkMRMDt0l0aAV
JWT_SECRET_KEY=your-super-secret-jwt-key-here
DATABASE_URL=sqlite:///./block_trade_dt.db
```

### 第五步：部署

1. Railway会自动检测到您的Python项目
2. 自动安装依赖包
3. 启动FastAPI应用
4. 分配一个公网URL

### 第六步：访问您的应用

部署完成后，您将获得：
- **公网URL**: `https://your-app-name.railway.app`
- **自动HTTPS**: SSL证书自动配置
- **全球CDN**: 快速访问

## 🔧 高级配置

### 自定义域名

1. 在Railway Dashboard中进入项目设置
2. 点击 "Domains"
3. 添加您的自定义域名
4. 配置DNS记录

### 数据库配置

Railway提供PostgreSQL数据库：
1. 在项目中添加 "Database" 服务
2. 更新 `DATABASE_URL` 环境变量
3. 修改 `app/config.py` 中的数据库配置

### 监控和日志

- **实时日志**: 在Railway Dashboard中查看
- **性能监控**: 自动收集应用指标
- **错误追踪**: 详细的错误日志

## 💰 费用说明

**免费计划包括：**
- 500小时/月运行时间
- 1GB RAM
- 1GB 存储空间
- 自定义域名支持

**付费计划：**
- $5/月起，无限制运行时间
- 更多资源和功能

## 🚨 注意事项

1. **环境变量**: 确保所有敏感信息都设置为环境变量
2. **数据库**: 生产环境建议使用PostgreSQL
3. **静态文件**: 确保静态文件路径正确
4. **API密钥**: 智谱AI API密钥已配置

## 🔄 自动部署

每次推送到GitHub主分支时，Railway会自动：
1. 拉取最新代码
2. 安装依赖
3. 重新部署应用
4. 更新在线版本

## 📞 技术支持

如遇到问题：
1. 查看Railway Dashboard中的日志
2. 检查环境变量配置
3. 确认所有依赖包已安装
4. 查看Railway官方文档

## 🎉 部署完成后的优势

- ✅ **无需手动重启服务器**
- ✅ **全球用户快速访问**
- ✅ **自动扩展和负载均衡**
- ✅ **99.9%+ 正常运行时间**
- ✅ **自动备份和恢复**
