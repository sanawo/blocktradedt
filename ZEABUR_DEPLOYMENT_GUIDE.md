# Zeabur 自动部署配置指南

## 🎯 部署目标
将集成了东方财富网数据爬虫的Block Trade DT平台部署到Zeabur

## 📋 部署前检查清单

### ✅ 代码更改已完成
- [x] 东方财富网数据爬虫 (`app/eastmoney_scraper.py`)
- [x] 移除智谱AI相关代码
- [x] 更新API接口
- [x] 替换logo和品牌标识
- [x] 更新依赖包

### ✅ Git提交状态
```bash
git status
git add .
git commit -m "feat: Integrate East Money data scraper and remove Zhipu AI"
```

## 🚀 部署步骤

### 1. 推送到GitHub
```bash
# 方法1: 直接推送
git push origin master

# 方法2: 使用部署脚本
bash deploy_eastmoney.sh
```

### 2. Zeabur自动部署
Zeabur会自动检测到GitHub仓库的更改并开始部署：

1. **检测更改**: Zeabur检测到新的commit
2. **构建镜像**: 根据`requirements.txt`安装依赖
3. **部署服务**: 启动新的服务实例
4. **健康检查**: 验证服务是否正常运行
5. **流量切换**: 将流量切换到新版本

### 3. 部署监控
在Zeabur Dashboard中监控部署状态：
- 访问: https://dash.zeabur.com
- 查看部署日志
- 检查服务状态

## 🔧 Zeabur配置

### 环境变量
确保以下环境变量已配置：
```
PORT=8001
HOST=0.0.0.0
DATABASE_URL=sqlite:///block_trade_dt.db
JWT_SECRET_KEY=your-secret-key
```

### 构建配置
Zeabur会自动检测Python项目并使用以下配置：
- **Python版本**: 3.11+
- **启动命令**: `python -m app.main`
- **端口**: 8001
- **依赖**: 从`requirements.txt`自动安装

## 📊 部署后验证

### 1. 基础功能测试
```bash
# 健康检查
curl https://www.blocktradedt.xyz/health

# API测试
curl https://www.blocktradedt.xyz/api/eastmoney/data
```

### 2. 功能验证清单
- [ ] 网站首页正常加载
- [ ] 东方财富网logo显示正确
- [ ] 实时数据更新正常
- [ ] API接口响应正常
- [ ] 搜索功能正常
- [ ] 智能分析功能正常

### 3. 数据源验证
- [ ] 东方财富网数据爬虫正常工作
- [ ] 市场统计数据实时更新
- [ ] 活跃股票数据正常显示
- [ ] 无智谱AI相关错误

## 🐛 故障排查

### 常见问题

#### 1. 部署失败
**原因**: 依赖包安装失败
**解决**: 检查`requirements.txt`中的包版本

#### 2. 服务启动失败
**原因**: 模块导入错误
**解决**: 确保使用`python -m app.main`启动

#### 3. 数据爬取失败
**原因**: 网络连接问题
**解决**: 检查东方财富网是否可访问

#### 4. API响应错误
**原因**: 依赖包缺失
**解决**: 确保beautifulsoup4、pandas、lxml已安装

### 日志查看
在Zeabur Dashboard中查看服务日志：
1. 进入项目页面
2. 点击服务名称
3. 查看"日志"标签
4. 查找错误信息

## 📈 性能优化

### 1. 数据缓存
建议添加Redis缓存提高性能：
```python
# 缓存东方财富网数据
cache.set('eastmoney_data', data, timeout=300)
```

### 2. 异步处理
使用异步爬虫提高效率：
```python
import asyncio
import aiohttp
```

### 3. 错误重试
添加重试机制：
```python
import time
from functools import wraps

def retry(max_attempts=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    time.sleep(2 ** attempt)
            return wrapper
        return decorator
    return decorator
```

## 🔄 持续部署

### 自动部署流程
1. **代码推送** → GitHub
2. **自动检测** → Zeabur
3. **构建镜像** → Docker
4. **部署服务** → 生产环境
5. **健康检查** → 验证服务

### 部署通知
配置部署成功/失败通知：
- 邮件通知
- Slack通知
- Discord通知

## 📞 技术支持

### Zeabur支持
- 文档: https://zeabur.com/docs
- Discord: https://discord.gg/zeabur
- 状态页: https://status.zeabur.com

### 项目支持
- GitHub Issues: https://github.com/sanawo/blocktradedt/issues
- 部署日志: Zeabur Dashboard

---

**部署时间**: 2025年1月27日  
**版本**: v2.0  
**状态**: 🚀 准备部署
