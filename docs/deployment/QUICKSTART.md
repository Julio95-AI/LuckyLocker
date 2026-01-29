# 🚀 LuckyLocker 快速部署指南

> 5步完成部署，让你的抽奖系统上线公网！

---

## ✅ 前置准备

- [x] 有GitHub账号
- [x] 有Cloudflare账号（托管域名 julio98.dpdns.org）
- [x] 项目代码已准备好

---

## 📝 5步部署流程

### 第1步：推送代码到GitHub（2分钟）

```bash
cd E:/GitRepo/Local/MyProject/LuckyLocker

# 添加所有文件
git add .

# 提交
git commit -m "准备部署到公网"

# 推送（确保仓库是Public）
git push origin master
```

---

### 第2步：注册并部署到Render（3分钟）

1. **注册Render**
   - 访问：https://render.com
   - 用GitHub账号登录

2. **创建Web Service**
   - 点击 **"New +"** → **"Web Service"**
   - 选择 `LuckyLocker` 仓库
   - 配置：
     - **Name**: `luckylocker`
     - **Region**: `Singapore` (新加坡)
     - **Branch**: `master`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `cd backend && gunicorn -w 2 -b 0.0.0.0:$PORT app:app`
   - 选择 **Free** 计划
   - 点击 **"Create Web Service"**

3. **等待部署完成**
   - 大约2-5分钟
   - 看到 "Your service is live" 即成功
   - 记录分配的域名：`https://luckylocker-xxxx.onrender.com`

---

### 第3步：配置Cloudflare DNS（2分钟）

1. **在Render获取域名**
   - 在Render服务页面，点击 **"Settings"**
   - 点击 **"Add Custom Domain"**
   - 输入：`julio98.dpdns.org`
   - 记下CNAME目标（格式：`luckylocker-xxxx.onrender.com`）

2. **在Cloudflare添加DNS记录**
   - 登录：https://dash.cloudflare.com
   - 选择域名 `dpdns.org`
   - 点击 **"DNS"** → **"Records"**
   - 点击 **"Add record"**：
     - **Type**: CNAME
     - **Name**: `julio98`
     - **Target**: `luckylocker-xxxx.onrender.com` (替换为你的)
     - **Proxy status**: **Proxied** (橙色云朵)
     - **TTL**: Auto
   - 点击 **"Save"**

3. **等待生效**
   - 大约5-10分钟
   - 访问：`https://julio98.dpdns.org`

---

### 第4步：测试功能（2分钟）

1. **访问抽奖页面**
   ```
   https://julio98.dpdns.org
   ```

2. **访问管理后台**
   ```
   https://julio98.dpdns.org/admin.html
   ```

3. **测试抽奖功能**
   - 点击"立即抽奖"
   - 查看是否能正常抽取格子

4. **测试后台功能**
   - 修改格子密码
   - 添加绿通凭证
   - 查看抽奖记录

---

### 第5步：配置防休眠（可选，5分钟）

**问题**：Render免费版15分钟无访问会休眠

**解决**：使用Cloudflare Worker定时唤醒

1. **创建Worker**
   - 登录Cloudflare
   - 点击 **"Workers & Pages"** → **"Create Application"** → **"Create Worker"**
   - 名称：`luckylocker-keepalive`
   - 复制 `cloudflare-worker-keepalive.js` 的代码
   - 修改域名为：`https://julio98.dpdns.org/api/system/config`
   - 点击 **"Save and Deploy"**

2. **添加定时任务**
   - 点击 **"Triggers"** → **"Add Cron Trigger"**
   - 输入：`*/10 * * * *` (每10分钟)
   - 点击 **"Add Trigger"**

3. **测试**
   - 等待10分钟
   - 查看Worker执行日志

---

## ⚠️ 重要提示

### 数据持久化问题

**问题**：Render免费版重启会清空数据库文件

**影响**：
- ❌ 格子配置会丢失
- ❌ 抽奖记录会丢失
- ❌ 绿通凭证会丢失

**临时解决方案**（测试阶段）：
1. 每次重启后重新配置格子
2. 定期导出配置（后台功能）
3. 活动期间尽量不重启

**永久解决方案**（正式上线前必做）：
1. 使用外部PostgreSQL数据库
2. 参考 `DEPLOY_PUBLIC.md` 中的详细步骤
3. 推荐使用：Supabase（免费500MB）

---

## 🎯 验收清单

部署完成后，确认以下项目：

- [ ] 可以访问 `https://julio98.dpdns.org`
- [ ] 可以访问管理后台 `https://julio98.dpdns.org/admin.html`
- [ ] 可以正常抽奖
- [ ] 可以在后台修改格子配置
- [ ] 可以添加绿通凭证
- [ ] 手机访问正常
- [ ] HTTPS证书有效（浏览器地址栏有锁图标）
- [ ] （可选）配置了防休眠Worker

---

## 📞 常见问题

### Q1: 部署失败怎么办？

**检查清单**：
1. GitHub仓库是否为Public（免费部署需要）
2. requirements.txt是否包含gunicorn
3. 查看Render的Deploy日志，找到错误信息

### Q2: 域名无法访问？

**检查清单**：
1. DNS是否已生效（等待5-10分钟）
2. Cloudflare DNS记录是否正确（CNAME类型，橙色云朵）
3. Render域名是否添加成功
4. 用 `nslookup julio98.dpdns.org` 检查DNS

### Q3: 抽奖后数据丢失？

**原因**：Render重启清空了SQLite文件

**解决**：
1. 短期：接受数据丢失，活动期间不重启
2. 长期：迁移到PostgreSQL数据库

---

## 🎉 下一步

部署完成后，你可以：

1. **生成二维码**
   - 使用 https://cli.im
   - 输入：`https://julio98.dpdns.org`
   - 下载二维码图片

2. **制作宣传海报**
   - 添加二维码
   - 添加活动说明
   - 打印张贴

3. **测试活动流程**
   - 用多个设备测试抽奖
   - 测试绿通凭证功能
   - 模拟用户取货流程

4. **监控运行状态**
   - 定期查看Render日志
   - 查看Cloudflare流量统计
   - 检查抽奖记录

---

**🎊 恭喜！你的抽奖系统已成功部署到公网！**

如需了解更多部署方案和优化建议，请查看 `DEPLOY_PUBLIC.md`
