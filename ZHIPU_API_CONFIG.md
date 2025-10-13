# 智谱AI API配置指南

## 🎯 目标
在 www.blocktradedt.xyz 网站上成功集成智谱AI功能

## ⚠️ 重要提示
根据之前的代码分析，您的API密钥已经在代码中泄露：
```
fc42f6448b65494a9f34617d5167dcbf.PFtIy0kn19Vauf1D
```

**必须立即删除此密钥并创建新密钥！**

---

## 📋 配置步骤

### 第一步：删除泄露的API密钥

1. 访问智谱AI控制台：https://bigmodel.cn/usercenter/proj-mgmt/apikeys
2. 找到密钥：`fc42f6448b65494a9f34617d5167dcbf.PFtIy0kn19Vauf1D`
3. 点击 **删除** 按钮
4. 确认删除

### 第二步：创建新的API密钥

1. 在智谱AI控制台中点击 **创建API Key**
2. 给密钥命名（例如：blocktradedt-production）
3. 复制新生成的密钥（格式类似：`xxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxx`）
4. **妥善保存，不要再公开分享！**

### 第三步：在Zeabur配置环境变量

1. **登录Zeabur Dashboard**
   - 访问：https://dash.zeabur.com
   - 使用您的账号登录

2. **找到项目**
   - 在项目列表中找到您的项目
   - 应该是部署 blocktradedt 的项目

3. **进入服务设置**
   - 点击服务名称
   - 点击顶部的 **变量（Variables）** 或 **环境变量（Environment Variables）** 标签

4. **添加智谱AI密钥**
   - 点击 **添加变量** 或 **Add Variable** 按钮
   - 配置如下：
     ```
     变量名: ZHIPU_API_KEY
     变量值: [粘贴您的新API密钥]
     类型: Private（私有）- 确保勾选此选项！
     ```
   - 点击 **保存** 或 **Save**

5. **重新部署服务**
   - 添加环境变量后，Zeabur会自动重新部署
   - 或者手动点击 **重新部署** 按钮
   - 等待2-3分钟完成部署

---

## ✅ 验证配置

### 方法1：通过浏览器测试

1. 访问 https://www.blocktradedt.xyz
2. 滚动到页面底部的 **AI智能助手** 区域
3. 在输入框中输入：`你好，请介绍一下大宗交易`
4. 点击发送按钮
5. 等待AI回复

**预期结果：**
- ✅ AI助手应该返回专业的回复
- ❌ 如果显示 "undefined" 或 "AI助手暂时不可用"，说明配置有问题

### 方法2：通过API测试

在命令行中运行：

```powershell
# 测试AI聊天API
$headers = @{
    "Content-Type" = "application/json"
}
$body = @{
    message = "你好，请介绍一下大宗交易"
    system_prompt = "你是一个专业的金融分析师"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://www.blocktradedt.xyz/api/chat" -Method Post -Headers $headers -Body $body
```

**预期输出：**
```json
{
    "message": "你好，请介绍一下大宗交易",
    "response": "大宗交易是指...[AI的详细回复]",
    "status": "success"
}
```

### 方法3：检查健康状态

```powershell
Invoke-RestMethod -Uri "https://www.blocktradedt.xyz/health"
```

**预期输出：**
```json
{
    "status": "ok"
}
```

### 方法4：查看Zeabur日志

1. 在Zeabur Dashboard中
2. 点击您的服务
3. 查看 **日志（Logs）** 标签
4. 查找以下成功消息：
   ```
   LLM instance loaded successfully
   Zhipu AI client initialized successfully
   ```

如果看到这些消息，说明配置成功！

---

## 🔍 故障排查

### 问题1：AI助手显示 "undefined"

**原因：**
- 前端代码期望字段名是 `response`，但后端返回的是 `reply`

**解决方案：**
✅ 已修复！我们已经更新了代码：
- `app_working.py` 中所有返回字段改为 `response`
- 需要重新部署代码到Zeabur

**重新部署步骤：**
```bash
# 1. 提交更新的代码
git add app_working.py app/llm.py
git commit -m "Fix AI chat API response field name"
git push origin master

# 2. Zeabur会自动检测并重新部署
# 3. 等待2-3分钟
```

### 问题2：AI助手显示 "AI助手暂时不可用"

**可能原因：**
1. 环境变量未设置或设置错误
2. API密钥无效
3. API密钥余额不足

**排查步骤：**

**A. 检查环境变量**
- 登录Zeabur Dashboard
- 进入服务 → 变量标签
- 确认 `ZHIPU_API_KEY` 存在且类型为 Private

**B. 检查API密钥**
- 访问智谱AI控制台
- 确认密钥状态为"正常"
- 检查剩余额度是否充足

**C. 查看日志**
在Zeabur日志中查找错误信息：
```
Failed to load LLM: [错误详情]
AI chat failed: [错误详情]
```

### 问题3：搜索时AI摘要不生成

**原因：**
- 用户没有勾选"使用AI生成摘要"
- 或者智谱API配置有问题

**解决方案：**
1. 确保勾选了"AI分析"开关
2. 检查环境变量配置（同问题2）

---

## 📊 环境变量完整列表

在Zeabur中应该配置的所有环境变量：

| 变量名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `ZHIPU_API_KEY` | Private | 是 | 智谱AI API密钥 |
| `PORT` | Public | 否 | Zeabur自动设置 |
| `HOST` | Public | 否 | 默认 0.0.0.0 |

**注意：**
- `ZHIPU_API_KEY` 必须设置为 **Private** 类型
- 不要在代码中硬编码API密钥

---

## 🎨 测试功能清单

配置完成后，逐项测试以下功能：

### 1. 基础功能
- [ ] 网站首页正常加载
- [ ] 趋势页面正常显示
- [ ] 搜索功能正常工作

### 2. AI聊天功能
- [ ] 打开AI助手对话框
- [ ] 发送测试消息："你好"
- [ ] 收到AI回复（不是"undefined"）
- [ ] 回复内容是中文且相关

### 3. 智能搜索摘要
- [ ] 执行搜索（例如："钢材"）
- [ ] 勾选"AI分析"开关
- [ ] 查看AI生成的摘要
- [ ] 摘要内容专业且相关

### 4. 高级功能
- [ ] 多轮对话正常
- [ ] 使用快捷建议按钮
- [ ] 市场分析功能正常
- [ ] 清空聊天记录正常

---

## 💰 成本估算

### 智谱AI定价（GLM-4-Flash）

- **输入Token**: ¥0.001/千tokens
- **输出Token**: ¥0.001/千tokens

### 日常使用估算

假设每天：
- 100次AI对话（平均每次500 tokens）
- 50次智能搜索摘要（平均每次300 tokens）

**日成本**：约 ¥0.08
**月成本**：约 ¥2.40

### 充值建议
- 最低充值：¥10（可用1-2个月）
- 推荐充值：¥50（可用半年以上）

---

## 🔒 安全建议

### 1. 保护API密钥
- ✅ 使用环境变量，不要硬编码
- ✅ 设置为Private类型
- ✅ 定期轮换密钥
- ❌ 不要提交到Git
- ❌ 不要在聊天中分享

### 2. 实施访问控制
建议添加：
- 用户认证
- API调用限流
- 使用量监控
- 异常告警

### 3. 监控使用情况
定期检查：
- 智谱AI控制台的使用统计
- Zeabur的服务日志
- 异常调用模式

---

## 📞 获取支持

### 智谱AI支持
- 官网：https://open.bigmodel.cn
- API文档：https://open.bigmodel.cn/dev/api
- 控制台：https://bigmodel.cn/usercenter

### Zeabur支持
- 文档：https://zeabur.com/docs
- Discord：https://discord.gg/zeabur
- 状态页：https://status.zeabur.com

---

## ✨ 快速命令参考

### 测试AI功能
```powershell
# 测试聊天
$body = @{message='你好'} | ConvertTo-Json
Invoke-RestMethod -Uri "https://www.blocktradedt.xyz/api/chat" -Method Post -Body $body -ContentType "application/json"

# 测试智能搜索
$body = @{query='钢材'; top_k=5; use_llm=$true} | ConvertTo-Json
Invoke-RestMethod -Uri "https://www.blocktradedt.xyz/api/search" -Method Post -Body $body -ContentType "application/json"

# 检查健康状态
Invoke-RestMethod -Uri "https://www.blocktradedt.xyz/health"
```

### 重新部署
```bash
# 更新代码后
git add .
git commit -m "Update AI configuration"
git push origin master

# Zeabur会自动部署，等待2-3分钟
```

---

## 🎉 完成！

配置完成后，您的网站应该具有：
- ✅ AI智能对话助手
- ✅ 智能搜索摘要生成
- ✅ 市场趋势AI分析
- ✅ 专业的金融知识问答

**现在就去测试吧！** 🚀

访问：https://www.blocktradedt.xyz

---

**配置日期**: 2025-10-13
**版本**: 1.1
**状态**: 待配置

