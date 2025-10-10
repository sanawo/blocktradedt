# 🚀 Block Trade DT - Cloudflare部署指南

## 📋 部署方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **Cloudflare Workers** | 全球CDN、自动扩展、免费额度大 | 需要重构为JS | 推荐方案 |
| **Cloudflare Pages** | 简单部署、免费 | 仅支持静态网站 | 静态版本 |
| **Railway/Render** | 支持Python、简单 | 需要付费、有资源限制 | 备选方案 |

## 🎯 推荐方案：Cloudflare Workers

### 第一步：安装Wrangler CLI

```bash
# 安装Wrangler
npm install -g wrangler

# 或者使用yarn
yarn global add wrangler
```

### 第二步：登录Cloudflare

```bash
# 登录Cloudflare账户
wrangler login
```

### 第三步：配置项目

1. **创建KV存储空间**：
```bash
# 创建生产环境KV
wrangler kv:namespace create "BLOCK_TRADE_KV"

# 创建预览环境KV
wrangler kv:namespace create "BLOCK_TRADE_KV" --preview
```

2. **更新wrangler.toml**：
   - 将生成的KV namespace ID填入配置文件
   - 设置环境变量

3. **设置密钥**：
```bash
# 设置智谱AI API密钥
wrangler secret put ZHIPU_API_KEY

# 设置JWT密钥
wrangler secret put JWT_SECRET_KEY
```

### 第四步：上传静态文件

```bash
# 上传HTML文件到KV存储
wrangler kv:key put "index.html" --path "./templates/index.html"
wrangler kv:key put "trends.html" --path "./templates/trends.html"
```

### 第五步：部署

```bash
# 安装依赖
npm install

# 本地测试
npm run dev

# 部署到生产环境
npm run deploy

# 部署到预览环境
npm run deploy:staging
```

## 🌐 部署后的访问

部署成功后，您将获得：
- **生产环境**：`https://block-trade-dt.your-subdomain.workers.dev`
- **自定义域名**：可在Cloudflare Dashboard中绑定您的域名

## 🔧 环境变量配置

在Cloudflare Dashboard中设置以下环境变量：

```
ZHIPU_API_KEY=your-zhipu-api-key
JWT_SECRET_KEY=your-jwt-secret-key
ENVIRONMENT=production
```

## 📊 监控和维护

1. **访问Cloudflare Dashboard**查看：
   - 请求统计
   - 错误日志
   - 性能指标

2. **自动部署**：
   - 连接GitHub仓库
   - 设置自动部署触发器

## 🆓 免费额度

Cloudflare Workers免费计划包括：
- 100,000 请求/天
- 10ms CPU时间/请求
- 1GB KV存储
- 全球CDN加速

## 🔄 从FastAPI迁移的优势

1. **无需服务器管理**：自动扩展，全球部署
2. **更快的响应速度**：边缘计算，就近访问
3. **更高的可用性**：99.9%+ 正常运行时间
4. **更低的成本**：免费额度足够个人使用
5. **自动HTTPS**：SSL证书自动管理

## 🚨 注意事项

1. **数据库替代**：使用Cloudflare KV替代SQLite
2. **文件上传**：静态文件需要上传到KV存储
3. **AI API**：智谱AI API调用需要配置CORS
4. **JWT处理**：使用Web Crypto API替代PyJWT

## 📞 技术支持

如遇到部署问题，可以：
1. 查看Cloudflare Workers文档
2. 检查Wrangler CLI日志
3. 使用`wrangler tail`查看实时日志
