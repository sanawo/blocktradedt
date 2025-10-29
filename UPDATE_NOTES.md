# Feature Updates - Dark Mode & News Links

## 📋 Update Summary

### 1. ✅ Trends Page - Dark Mode

**Changes:**
- Updated `/trends` route to use dark mode interface (`trends_dark.html`)
- Enhanced visual comfort for long-term usage
- Supports real-time data updates and interactive charts

**Modified Files:**
- `app/main.py` - Lines 90-92
- `api/index.py` - Lines 77-79

**Access:**
```
https://www.blocktradedt.xyz/trends
```

---

### 2. ✅ Real-time News - Clickable Links

**Changes:**
- Added `/news` page route for real-time news display
- Added `/api/news` API with accessible news URLs
- Added `/api/news/latest` API for homepage news display
- News items are clickable and open in new tabs

**News Sources:**
- Sina Finance (https://finance.sina.com.cn)
- East Money (https://www.eastmoney.com)
- Tencent Finance (https://finance.qq.com)
- NDRC (https://www.ndrc.gov.cn)
- Caixin (https://www.caixin.com)
- CSRC (https://www.csrc.gov.cn)
- Yicai (https://www.yicai.com)
- 21st Century Business Herald (https://www.21jingji.com)
- Wall Street CN (https://wallstreetcn.com)
- FT Chinese (https://www.ftchinese.com)

**News Categories:**
- `all` - All news
- `market` - Market dynamics
- `policy` - Policy & regulations
- `analysis` - Industry analysis
- `company` - Company news
- `international` - International news

**Modified/Added Files:**
- `app/main.py` - Added `/news` route and APIs
- `api/index.py` - Added `/news` route and APIs
- `templates/news.html` - News page with clickable links

**Access:**
```
# News page
https://www.blocktradedt.xyz/news

# News API
https://www.blocktradedt.xyz/api/news?page=1&category=all&limit=20

# Latest news API
https://www.blocktradedt.xyz/api/news/latest?limit=6
```

---

### 3. ✅ Enhanced Trends Data API

**Updates:**
- Optimized `/api/trends/data` API with richer data
- Supports 24-hour real-time data tracking
- Provides category and region rankings

**Data Structure:**
```json
{
  "stats": {
    "total_volume": 75.32,
    "total_transactions": 234,
    "avg_price": -0.82,
    "active_sellers": 89
  },
  "time_labels": ["00:00", "01:00", ...],
  "transaction_volumes": [120, 145, ...],
  "price_trends": [3620.5, 3615.2, ...],
  "categories": [...],
  "regions": [...],
  "last_update": "2024-10-13 14:30:00"
}
```

---

## 🚀 Deployment

This update will be automatically deployed to **www.blocktradedt.xyz** via Zeabur when pushed to GitHub.

---

## 📝 Key Features

1. **Dark Mode Trends Page**
   - Dark background for comfortable viewing
   - Real-time data updates
   - Interactive charts
   - Category and region rankings

2. **Real-time News**
   - Clickable news items
   - Opens real news websites in new tabs
   - Category filtering
   - Auto-refresh every 30 seconds

---

## 🔧 Technical Details

**Backend Changes:**
- Added news API endpoints
- Enhanced trends data API
- Updated route handlers

**Frontend Changes:**
- Dark mode styles for trends page
- News timeline interface
- Click handlers for news links
- Auto-refresh mechanism

---

## 📊 API Documentation

### GET /api/news
Get news list

**Parameters:**
- `page` (int): Page number, default 1
- `category` (str): Category filter, default "all"
- `limit` (int): Items per page, default 20

### GET /api/news/latest
Get latest news

**Parameters:**
- `limit` (int): Number of items, default 6

### GET /api/trends/data
Get trends data with 24-hour tracking and rankings

---

**Last Updated:** October 13, 2024


















