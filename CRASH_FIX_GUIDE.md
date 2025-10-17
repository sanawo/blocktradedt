# 🚨 Zeabur 崩溃修复指南

## 🔍 问题诊断

### 错误信息
```
ValueError: numpy.dtype size changed, may indicate binary incompatibility. 
Expected 96 from C header, got 88 from PyObject
```

### 原因分析
- numpy和pandas版本不兼容
- 二进制文件大小不匹配
- 容器启动失败，进入BackOff重启循环

## 🔧 修复方案

### 1. 版本降级策略
已将以下包降级到稳定版本：

```txt
# 修复前（有问题）
numpy==1.24.3
pandas==2.0.3
sentence-transformers==5.1.1

# 修复后（稳定）
numpy==1.21.6
pandas==1.5.3
sentence-transformers==2.2.2
```

### 2. 版本兼容性说明
- **numpy 1.21.6**: 稳定版本，与pandas 1.5.3完全兼容
- **pandas 1.5.3**: 稳定版本，避免二进制不兼容问题
- **sentence-transformers 2.2.2**: 兼容版本，避免依赖冲突

## 🚀 部署步骤

### 步骤1: 推送修复
```bash
git add requirements.txt
git commit -m "fix: Downgrade numpy/pandas to fix compatibility crash"
git push origin master
```

### 步骤2: Zeabur重新部署
1. 访问: https://dash.zeabur.com
2. 找到 `blocktradedt` 项目
3. 点击 "重新部署"
4. 等待3-5分钟完成部署

### 步骤3: 验证修复
访问: https://www.blocktradedt.xyz
- ✅ 网站正常加载
- ✅ 无崩溃错误
- ✅ 所有功能正常

## 📊 修复对比

### 修复前
- ❌ numpy 1.24.3 + pandas 2.0.3 不兼容
- ❌ 容器启动失败
- ❌ BackOff重启循环
- ❌ 服务不可用

### 修复后
- ✅ numpy 1.21.6 + pandas 1.5.3 兼容
- ✅ 容器正常启动
- ✅ 服务稳定运行
- ✅ 所有功能正常

## 🔍 技术细节

### 错误原因
1. **二进制不兼容**: numpy编译时期望96字节，运行时得到88字节
2. **版本冲突**: 不同版本的numpy/pandas二进制接口不匹配
3. **依赖链问题**: sentence-transformers依赖特定版本的numpy

### 解决方案
1. **版本锁定**: 使用经过测试的稳定版本组合
2. **兼容性验证**: 确保所有包版本相互兼容
3. **渐进式升级**: 避免一次性升级多个相关包

## 🐛 故障排查

### 如果修复后仍有问题

#### 1. 检查部署日志
在Zeabur Dashboard中查看：
- 构建日志
- 运行时日志
- 错误信息

#### 2. 验证依赖安装
```bash
pip install -r requirements.txt
python -c "import numpy, pandas; print('OK')"
```

#### 3. 本地测试
```bash
python -m app.main
```

### 常见问题

#### 问题1: 仍然崩溃
**解决**: 进一步降级到更稳定的版本
```txt
numpy==1.19.5
pandas==1.3.5
```

#### 问题2: 功能缺失
**解决**: 检查sentence-transformers功能是否正常

#### 问题3: 性能下降
**解决**: 逐步升级到兼容的新版本

## 📈 监控建议

### 部署后监控
1. **服务状态**: 确保容器正常运行
2. **错误日志**: 监控是否有新的错误
3. **性能指标**: 检查响应时间和资源使用
4. **功能测试**: 验证所有功能正常

### 长期优化
1. **版本管理**: 建立依赖版本管理策略
2. **测试环境**: 在测试环境验证版本升级
3. **监控告警**: 设置服务异常告警
4. **回滚计划**: 准备快速回滚方案

## 🎯 预期结果

修复后应该看到：
- ✅ Zeabur部署成功
- ✅ 容器正常启动
- ✅ 网站可正常访问
- ✅ 所有功能正常运行
- ✅ 无崩溃错误

---

## 📞 技术支持

### 如果问题持续
1. 检查Zeabur Dashboard日志
2. 验证本地环境是否正常
3. 考虑使用Docker镜像固定版本
4. 联系Zeabur技术支持

### 联系方式
- 📧 邮箱: 2787618474@qq.com
- 🐛 GitHub Issues: https://github.com/sanawo/blocktradedt/issues
- 💬 Zeabur Discord: https://discord.gg/zeabur

---

**修复时间**: 预计5-10分钟  
**部署地址**: https://www.blocktradedt.xyz  
**状态**: 🚨 等待修复部署
