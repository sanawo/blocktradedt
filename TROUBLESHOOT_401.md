# 智谱AI 401错误排查指南

## 🚨 错误描述
```
Error code: 401, with error text {"error":{"code":"1000","message":"...
```

这是智谱AI API的认证错误，表示API密钥无效或未正确配置。

---

## ✅ 解决步骤

### 第一步：检查智谱AI API密钥状态

1. **登录智谱AI控制台**
   - 访问：https://bigmodel.cn/usercenter/proj-mgmt/apikeys
   - 使用您的账号登录

2. **检查API密钥**
   - 查看是否有有效的API密钥
   - 确认密钥状态为"正常"（不是"已停用"）
   - 检查余额是否充足

3. **如果密钥已删除或无效**
   - 点击"创建API Key"
   - 命名：`blocktradedt-production`
   - 复制新生成的完整密钥（格式：`xxxxxxxx.xxxxxxxxxx`）
   - **妥善保存！**

---

### 第二步：在Zeabur正确配置环境变量

#### A. 登录Zeabur Dashboard
1. 访问：https://dash.zeabur.com
2. 找到您的项目
3. 点击服务名称（应该显示为您的应用名）

#### B. 进入变量设置
1. 点击顶部的"**Variables**"（变量）标签
2. 查看是否已存在 `ZHIPU_API_KEY`

#### C. 配置/更新变量

**如果已存在 ZHIPU_API_KEY：**
1. 点击变量右侧的"编辑"按钮
2. 更新为新的API密钥
3. 确保类型为"**Private**"（私有）✅
4. 点击保存

**如果不存在 ZHIPU_API_KEY：**
1. 点击"**Add Variable**"（添加变量）
2. 填写：
   ```
   Name: ZHIPU_API_KEY
   Value: [粘贴您的完整API密钥]
   Type: Private ✅ 必须选择Private！
   ```
3. 点击保存

#### D. 重新部署
1. 保存环境变量后，点击"**Redeploy**"（重新部署）按钮
2. 或者等待自动重启（约1分钟）
3. 在"**Logs**"标签查看部署进度

---

### 第三步：验证配置

#### 方法1：查看Zeabur日志

在Logs标签中，应该看到：
```
✅ Zhipu AI client initialized successfully
✅ LLM instance loaded successfully
```

**如果看到错误：**
```
❌ Failed to initialize Zhipu AI client: [错误信息]
❌ Warning: zhipuai package not installed
```

说明配置有问题。

#### 方法2：测试API

等待部署完成（约2-3分钟）后，运行：

```powershell
# 测试AI聊天
$headers = @{"Content-Type" = "application/json"}
$body = @{message = "你好"} | ConvertTo-Json

Invoke-RestMethod -Uri "https://www.blocktradedt.xyz/api/chat" `
    -Method Post `
    -Headers $headers `
    -Body $body
```

**成功的响应：**
```json
{
    "message": "你好",
    "response": "您好！我是专业的大宗交易数据分析助手...",
    "status": "success"
}
```

**失败的响应：**
```json
{
    "message": "AI助手不可用...",
    "response": "AI助手暂时不可用，请检查API密钥配置。"
}
```

---

## 🔍 常见问题排查

### 问题1：环境变量类型设置错误

**症状：**
- 环境变量已设置
- 但仍然返回401错误

**原因：**
- 变量类型设置为"Public"而非"Private"

**解决：**
1. 在Zeabur Variables标签中
2. 找到 `ZHIPU_API_KEY`
3. 确认类型显示为"🔒 Private"
4. 如果不是，重新创建变量并选择Private

---

### 问题2：API密钥格式错误

**症状：**
- 复制的密钥不完整
- 有多余的空格或换行

**智谱AI密钥正确格式：**
```
xxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxx
```
- 长度约40-50个字符
- 中间有一个点(.)
- 只包含字母、数字和点

**解决：**
1. 重新复制API密钥
2. 检查没有多余空格
3. 确保完整复制（包括点号前后）

---

### 问题3：API密钥余额不足

**症状：**
- 密钥配置正确
- 但仍然无法调用

**检查余额：**
1. 登录智谱AI控制台
2. 查看"我的账户" → "余额"
3. 如果余额为0，需要充值

**最低充值建议：**
- ¥10（约可用1-2个月）

---

### 问题4：Zeabur未检测到环境变量更新

**症状：**
- 已更新环境变量
- 但日志显示仍未初始化

**解决：**
1. 手动重新部署：
   - 在Zeabur中点击"Redeploy"
2. 或者推送代码触发部署：
   ```bash
   git commit --allow-empty -m "Trigger redeploy"
   git push origin master
   ```

---

## 📋 完整配置检查清单

在Zeabur Dashboard中逐项检查：

- [ ] 登录了正确的Zeabur账号
- [ ] 找到了正确的项目
- [ ] 选择了正确的服务
- [ ] 进入了Variables（变量）标签
- [ ] `ZHIPU_API_KEY` 变量存在
- [ ] 变量值是完整的API密钥（40-50字符）
- [ ] 变量类型是"Private"（显示🔒图标）
- [ ] 已点击保存
- [ ] 服务已重新部署
- [ ] Logs显示"Zhipu AI client initialized successfully"

---

## 🧪 详细测试步骤

### 1. 测试健康状态
```powershell
Invoke-RestMethod -Uri "https://www.blocktradedt.xyz/health"
```
预期：`{"status":"ok"}`

### 2. 测试AI聊天（简单消息）
```powershell
$body = @{message='你好'} | ConvertTo-Json
Invoke-RestMethod -Uri "https://www.blocktradedt.xyz/api/chat" `
    -Method Post -Body $body -ContentType "application/json"
```
预期：收到AI的中文回复

### 3. 测试AI聊天（专业问题）
```powershell
$body = @{message='请介绍一下大宗交易的特点'} | ConvertTo-Json
Invoke-RestMethod -Uri "https://www.blocktradedt.xyz/api/chat" `
    -Method Post -Body $body -ContentType "application/json"
```
预期：收到专业的分析回复

### 4. 测试智能搜索摘要
```powershell
$body = @{query='钢材'; top_k=5; use_llm=$true} | ConvertTo-Json
Invoke-RestMethod -Uri "https://www.blocktradedt.xyz/api/search" `
    -Method Post -Body $body -ContentType "application/json"
```
预期：返回搜索结果和AI生成的摘要

---

## 📸 Zeabur配置截图说明

### 正确的配置应该是：

```
[Variables 标签]

┌─────────────────────────────────────────────┐
│ 🔒 ZHIPU_API_KEY        Private       [Edit] │
│    ●●●●●●●●●●●●●●●●●●●●●●●●●.●●●●●●●●●     │
└─────────────────────────────────────────────┘

[Add Variable 按钮]
```

**关键点：**
1. 🔒 图标表示Private类型
2. 值被隐藏显示为点号
3. 可以点击Edit编辑

---

## 🔄 重新配置流程（完整版）

如果以上都不行，从头开始：

### 1. 清理旧配置
```bash
# 在Zeabur中
1. 删除现有的 ZHIPU_API_KEY 变量
2. 点击保存
```

### 2. 创建新的API密钥
```bash
# 在智谱AI控制台
1. 删除所有旧密钥
2. 创建新密钥：blocktradedt-prod
3. 复制完整密钥（不要中断）
```

### 3. 重新添加到Zeabur
```bash
# 在Zeabur Variables标签
1. 点击"Add Variable"
2. Name: ZHIPU_API_KEY
3. Value: [粘贴新密钥]
4. Type: Private ✅
5. 点击Save
```

### 4. 强制重新部署
```bash
# 在本地
git commit --allow-empty -m "Force redeploy for API key update"
git push origin master
```

### 5. 等待并验证
```bash
# 等待3-5分钟
# 然后在Zeabur Logs中查看
# 应该看到：Zhipu AI client initialized successfully
```

---

## 💡 额外提示

### 1. API密钥安全
- ✅ 只在Zeabur环境变量中配置
- ✅ 设置为Private类型
- ❌ 不要硬编码在代码中
- ❌ 不要提交到Git
- ❌ 不要在聊天中分享

### 2. 调试技巧
如果仍然不行，在Zeabur Logs中查找：
```
ZHIPU_API_KEY: 已设置  # 或 '未设置'
```

### 3. 临时测试
可以先在本地测试API密钥是否有效：
```powershell
# 在本地设置环境变量
$env:ZHIPU_API_KEY="你的API密钥"

# 启动本地服务器
python app_working.py

# 测试（在另一个窗口）
$body = @{message='你好'} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" `
    -Method Post -Body $body -ContentType "application/json"
```

如果本地可以工作，说明密钥有效，问题在Zeabur配置。

---

## 📞 仍然无法解决？

请提供以下信息：

1. **Zeabur Logs截图**
   - 启动时的日志
   - 特别是包含"Zhipu"或"LLM"的行

2. **Zeabur Variables截图**
   - 显示环境变量列表
   - 确认有ZHIPU_API_KEY且类型为Private

3. **智谱AI控制台截图**
   - API密钥列表
   - 确认有有效密钥且状态正常

4. **错误信息**
   - 完整的401错误响应
   - 浏览器控制台的错误（F12）

---

**更新日期**: 2025-10-13
**适用于**: Zeabur部署 + 智谱AI集成



