# 大宗交易数据抓取系统 - 快速启动指南

## ✅ 系统状态

系统已成功实现并测试通过！

- ✅ 数据抓取功能正常（已测试，成功抓取50条记录）
- ✅ 数据保存功能正常（已测试，成功保存50条记录）
- ✅ 数据库模型已创建
- ✅ API端点已实现
- ✅ 前端页面已更新

## 🚀 快速启动（4步）

### 步骤0: 安装依赖（首次运行必须）

**方法1：使用依赖检查脚本（推荐）**
```bash
python check_dependencies.py
```
脚本会自动检查并提示安装缺失的依赖。

**方法2：直接安装所有依赖**
```bash
pip install -r requirements.txt
```

如果遇到 `ModuleNotFoundError`，请确保：
1. 使用正确的 Python 环境（如果使用虚拟环境，请先激活）
2. 运行 `pip install -r requirements.txt` 安装所有依赖
3. 主要依赖包括：`beautifulsoup4`, `requests`, `sqlalchemy`, `fastapi`, `python-dotenv` 等

### 步骤1: 启动Web服务

```bash
uvicorn api.index:app --host 0.0.0.0 --port 8080
```

或者使用gunicorn（生产环境推荐）:
```bash
gunicorn api.index:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

### 步骤2: 启动数据抓取调度器（新终端窗口）

```bash
python scripts/start_dzjy_scheduler.py
```

调度器会：
- 立即执行一次数据抓取
- 之后每5分钟自动抓取一次
- 自动去重，避免重复数据

### 步骤3: 访问页面

打开浏览器访问：**http://localhost:8080/trends**

你将看到：
- 📊 4个统计卡片（总成交额、总成交量、活跃股票数、平均折价率）
- 📈 交易量趋势图（支持24h/7d/30d切换）
- 📋 大宗交易数据表格（分页显示）
- 🔄 自动刷新（每5分钟）

## 📡 API端点

系统提供3个API端点：

### 1. 获取最新数据
```
GET /api/dzjy/latest?limit=10
```

### 2. 获取趋势数据
```
GET /api/dzjy/trends?period=24h
```
支持的时间周期：`24h`, `7d`, `30d`

### 3. 获取分页列表
```
GET /api/dzjy/list?page=1&size=50
```

## 🧪 测试

### 测试数据抓取
```bash
python test_dzjy_scraper.py
```

### 测试完整流程
```bash
python test_full_dzjy_flow.py
```

## 📊 数据来源

数据来源：**同花顺** (https://data.10jqka.com.cn/market/dzjy/)

⚠️ **重要提示**：
- 在正式部署前，请确认目标网站的robots.txt和服务条款
- 确保抓取行为符合规定
- 数据仅供学习和研究使用

## 🔧 配置

### 修改抓取频率

编辑 `scripts/start_dzjy_scheduler.py`，修改：
```python
scheduler.start_scheduler(interval_minutes=5)  # 改为你想要的分钟数
```

### 修改数据库

编辑 `.env` 文件或环境变量：
```bash
DATABASE_URL=sqlite:///./block_trade_dt.db
```

## 📁 文件结构

```
.
├── app/
│   ├── models.py              # 数据模型（DzjyTrade）
│   ├── dzjy_scraper.py        # 数据抓取脚本
│   └── dzjy_scheduler.py       # 定时任务调度器
├── api/
│   └── index.py               # API端点（3个新端点）
├── scripts/
│   └── start_dzjy_scheduler.py # 调度器启动脚本
├── templates/
│   └── trends_dark.html       # 前端页面（已更新）
├── test_dzjy_scraper.py       # 抓取测试脚本
├── test_full_dzjy_flow.py     # 完整流程测试
└── DZJY_QUICK_START.md        # 本文档
```

## 🐛 故障排查

### 问题0: 端口被占用（错误 10048）

**错误信息：** `[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8080)`

**原因：** 端口 8080 已被其他进程占用（通常是之前启动的服务器实例）

**解决方案：**

**方法1：关闭占用端口的进程（推荐）**
```bash
# 1. 查找占用 8080 端口的进程
netstat -ano | findstr :8080

# 2. 找到 PID（最后一列的数字），然后关闭进程
# Windows:
taskkill /PID <进程ID> /F
# 例如：taskkill /PID 46520 /F
```

**方法2：使用其他端口**
```bash
# 使用 8081 端口启动
uvicorn api.index:app --host 0.0.0.0 --port 8081
```
然后访问：`http://localhost:8081`

**方法3：快速关闭所有 Python 进程（谨慎使用）**
```bash
taskkill /IM python.exe /F
```

### 问题1: ModuleNotFoundError（模块未找到）

#### 错误1: `ModuleNotFoundError: No module named 'bs4'`

**原因：** 缺少 `beautifulsoup4` 依赖包

**解决方案：**
```bash
# 安装缺失的依赖
pip install beautifulsoup4==4.12.2

# 或者安装所有依赖
pip install -r requirements.txt
```

#### 错误2: `ModuleNotFoundError: No module named 'api'`

**原因：** 不在项目根目录下运行命令

**解决方案：**
1. 确认当前目录是项目根目录（应该能看到 `api`、`app`、`scripts` 等文件夹）
2. 切换到项目根目录：
   ```bash
   # Windows PowerShell
   cd "C:\Users\ruoha\Desktop\共享"
   
   # Windows CMD
   cd /d "C:\Users\ruoha\Desktop\共享"
   ```

如果遇到其他 `ModuleNotFoundError`：

1. **检查是否在正确的 Python 环境中**：
   ```bash
   python --version
   which python  # Linux/Mac
   where python  # Windows
   ```

2. **安装所有依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **如果使用虚拟环境，确保已激活**：
   ```bash
   # 创建虚拟环境（如果还没有）
   python -m venv venv
   
   # 激活虚拟环境
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # 然后安装依赖
   pip install -r requirements.txt
   ```

4. **验证安装**：
   ```bash
   python -c "from bs4 import BeautifulSoup; print('OK')"
   ```

### 问题2: 无法抓取数据

1. 检查网络连接
2. 检查目标网站是否可访问
3. 查看调度器日志

### 问题3: API返回空数据

1. 确认调度器正在运行
2. 检查数据库中是否有数据：
   ```python
   from app.models import DzjyTrade
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   
   engine = create_engine("sqlite:///./block_trade_dt.db")
   Session = sessionmaker(bind=engine)
   db = Session()
   count = db.query(DzjyTrade).count()
   print(f"数据库中有 {count} 条记录")
   ```

### 问题4: 前端页面无数据

1. 打开浏览器开发者工具（F12）
2. 查看Console标签页的错误信息
3. 查看Network标签页的API请求状态

## 📚 更多文档

- **API文档**: `DZJY_API_DOCS.md`
- **部署说明**: `DZJY_DEPLOYMENT.md`
- **实现总结**: `DZJY_IMPLEMENTATION_SUMMARY.md`

## 🎉 完成！

系统已完全部署并可以使用。享受你的大宗交易数据平台吧！

如有问题，请查看日志文件或相关文档。

