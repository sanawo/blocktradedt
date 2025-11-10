# 大宗交易数据API文档

## 概述

本文档描述了大宗交易数据抓取和展示系统的API接口。系统从同花顺网站（https://data.10jqka.com.cn/market/dzjy/）抓取大宗交易数据，并提供RESTful API供前端调用。

## 数据模型

### DzjyTrade 数据模型

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键ID |
| trade_time | DateTime | 交易时间 |
| stock_code | String(10) | 股票代码 |
| stock_name | String(50) | 股票名称 |
| volume | Float | 成交量（万股） |
| amount | Float | 成交金额（万元） |
| price | Float | 成交价格 |
| source_raw | Text | 原始数据来源（JSON格式） |
| created_at | DateTime | 创建时间 |

## API端点

### 1. 获取最新大宗交易数据

**端点**: `GET /api/dzjy/latest`

**描述**: 获取最新的大宗交易数据记录

**参数**:
- `limit` (可选, int): 返回记录数量，默认10

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "trade_time": "2025-01-10T10:30:00",
      "stock_code": "000001",
      "stock_name": "平安银行",
      "volume": 100.5,
      "amount": 1500.0,
      "price": 15.0,
      "source_raw": "{\"date\":\"2025-01-10\",\"code\":\"000001\",...}"
    }
  ],
  "count": 10,
  "timestamp": "2025-01-10T12:00:00"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "错误信息",
  "data": [],
  "count": 0
}
```

---

### 2. 获取交易量趋势数据

**端点**: `GET /api/dzjy/trends`

**描述**: 获取指定时间周期内的交易量趋势数据

**参数**:
- `period` (可选, string): 时间周期，可选值：
  - `24h`: 最近24小时（按小时分组）
  - `7d`: 最近7天（按天分组）
  - `30d`: 最近30天（按天分组）
  - 默认: `24h`

**响应示例**:
```json
{
  "success": true,
  "period": "24h",
  "data": [
    {
      "date": "2025-01-10 10:00",
      "volume": 1000.5,
      "amount": 15000.0,
      "count": 50
    },
    {
      "date": "2025-01-10 11:00",
      "volume": 1200.3,
      "amount": 18000.0,
      "count": 55
    }
  ],
  "timestamp": "2025-01-10T12:00:00"
}
```

---

### 3. 获取大宗交易列表（分页）

**端点**: `GET /api/dzjy/list`

**描述**: 获取大宗交易数据列表，支持分页

**参数**:
- `page` (可选, int): 页码，从1开始，默认1
- `size` (可选, int): 每页数量，默认20

**响应示例**:
```json
{
  "success": true,
  "page": 1,
  "size": 20,
  "total": 100,
  "data": [
    {
      "trade_time": "2025-01-10T10:30:00",
      "stock_code": "000001",
      "stock_name": "平安银行",
      "volume": 100.5,
      "amount": 1500.0,
      "price": 15.0
    }
  ],
  "timestamp": "2025-01-10T12:00:00"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "错误信息",
  "page": 1,
  "size": 20,
  "total": 0,
  "data": []
}
```

## 数据抓取

### 抓取方式

系统支持两种数据抓取方式：

1. **JSON API方式**（优先）: 自动查找目标网站的JSON接口
2. **Playwright方式**（备用）: 使用Playwright模拟浏览器抓取渲染后的数据

### 抓取配置

- **抓取频率**: 每5分钟执行一次
- **重试机制**: 最多重试3次，每次重试延迟递增（2秒、4秒、6秒）
- **限速控制**: 最小请求间隔1秒
- **错误告警**: 连续5次失败后发送告警

### 启动抓取调度器

```bash
python scripts/start_dzjy_scheduler.py
```

## 注意事项

1. **robots.txt**: 在正式部署前，请确认目标网站的robots.txt和服务条款，确保抓取行为符合规定。

2. **数据来源**: 数据来源于同花顺网站，仅供学习和研究使用。

3. **性能优化**: 
   - 数据库已创建索引以提高查询性能
   - API响应支持缓存（可在应用层实现）

4. **错误处理**: 所有API都包含错误处理，即使数据库为空也会返回空数组而不是错误。

## 部署说明

详见 `DZJY_DEPLOYMENT.md`

