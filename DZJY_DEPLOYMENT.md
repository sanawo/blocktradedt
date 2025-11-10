# 大宗交易数据抓取系统部署说明

## 系统架构

- **后端**: FastAPI (Python)
- **数据库**: SQLite (可配置为PostgreSQL)
- **前端**: HTML + JavaScript + ECharts
- **抓取工具**: Requests + Playwright (可选)

## 部署步骤

### 1. 环境准备

#### 安装Python依赖

```bash
pip install -r requirements.txt
```

#### 可选：安装Playwright（用于备用抓取方式）

```bash
pip install playwright
playwright install chromium
```

### 2. 数据库初始化

数据库表会在应用启动时自动创建。如果需要手动初始化：

```python
from sqlalchemy import create_engine
from app.models import Base
from app.config import Config

engine = create_engine(Config.get_database_url())
Base.metadata.create_all(bind=engine)
```

### 3. 启动数据抓取调度器

#### 方式1：独立进程运行

```bash
python scripts/start_dzjy_scheduler.py
```

#### 方式2：后台运行（Linux/Mac）

```bash
nohup python scripts/start_dzjy_scheduler.py > dzjy_scheduler.log 2>&1 &
```

#### 方式3：使用systemd（Linux）

创建服务文件 `/etc/systemd/system/dzjy-scheduler.service`:

```ini
[Unit]
Description=DZJY Data Scheduler
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 /path/to/project/scripts/start_dzjy_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable dzjy-scheduler
sudo systemctl start dzjy-scheduler
```

### 4. 启动Web应用

```bash
uvicorn api.index:app --host 0.0.0.0 --port 8080
```

或使用gunicorn（生产环境推荐）:
```bash
gunicorn api.index:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

### 5. 配置环境变量（可选）

```bash
export DATABASE_URL="sqlite:///./block_trade_dt.db"
export PORT=8080
```

## Docker部署

### Dockerfile示例

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 可选：安装Playwright
# RUN pip install playwright && playwright install chromium

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8080"]
```

### docker-compose.yml示例

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=sqlite:///./block_trade_dt.db
    volumes:
      - ./block_trade_dt.db:/app/block_trade_dt.db
    restart: unless-stopped

  scheduler:
    build: .
    command: python scripts/start_dzjy_scheduler.py
    environment:
      - DATABASE_URL=sqlite:///./block_trade_dt.db
    volumes:
      - ./block_trade_dt.db:/app/block_trade_dt.db
    restart: unless-stopped
    depends_on:
      - web
```

启动：
```bash
docker-compose up -d
```

## Zeabur部署

### 1. 配置.zeaburrc

确保`.zeaburrc`文件包含正确的启动命令：

```json
{
  "buildCommand": "pip install -r requirements.txt",
  "startCommand": "uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8080}"
}
```

### 2. 环境变量

在Zeabur控制台设置：
- `DATABASE_URL`: 数据库连接字符串
- `PORT`: 端口号（默认8080）

### 3. 定时任务

Zeabur不支持后台进程，建议：
- 使用外部定时任务服务（如cron-job.org）定期调用抓取API
- 或在应用启动时创建后台线程运行调度器

## 测试

### 单元测试

```bash
python -m pytest tests/test_dzjy_scraper.py
python -m pytest tests/test_dzjy_api.py
```

### 集成测试

```bash
# 启动服务
uvicorn api.index:app --host 0.0.0.0 --port 8080

# 测试API
curl http://localhost:8080/api/dzjy/latest
curl http://localhost:8080/api/dzjy/trends?period=24h
curl http://localhost:8080/api/dzjy/list?page=1&size=10
```

## 监控和日志

### 日志位置

- 应用日志: 标准输出
- 调度器日志: `dzjy_scheduler.log`（如果使用nohup）

### 健康检查

```bash
curl http://localhost:8080/health
```

### 监控指标

- 数据抓取成功率
- API响应时间
- 数据库记录数量
- 错误告警次数

## 故障排查

### 问题1: 无法抓取数据

1. 检查网络连接
2. 检查目标网站是否可访问
3. 查看日志中的错误信息
4. 尝试手动运行抓取脚本

### 问题2: 数据库错误

1. 检查数据库文件权限
2. 确认数据库URL配置正确
3. 检查表是否已创建

### 问题3: API返回空数据

1. 确认调度器正在运行
2. 检查数据库中是否有数据
3. 查看调度器日志

## 性能优化建议

1. **数据库索引**: 已为`trade_time`和`stock_code`创建索引
2. **查询优化**: 使用分页避免一次性加载大量数据
3. **缓存**: 可以考虑添加Redis缓存热门查询
4. **CDN**: 静态资源使用CDN加速

## 安全注意事项

1. **API限流**: 建议添加API限流机制
2. **数据验证**: 所有输入参数都应验证
3. **错误信息**: 生产环境不要暴露详细错误信息
4. **HTTPS**: 生产环境必须使用HTTPS

## 维护

### 数据清理

定期清理旧数据（可选）：

```python
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import DzjyTrade

# 删除30天前的数据
cutoff_date = datetime.now() - timedelta(days=30)
db.query(DzjyTrade).filter(DzjyTrade.trade_time < cutoff_date).delete()
db.commit()
```

### 备份

定期备份数据库：

```bash
cp block_trade_dt.db block_trade_dt.db.backup.$(date +%Y%m%d)
```

## 联系和支持

如有问题，请查看日志文件或联系开发团队。

