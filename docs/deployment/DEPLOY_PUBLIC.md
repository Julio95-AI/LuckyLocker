# 🌐 LuckyLocker 公网部署指南（免费方案）

> 适合第一次部署应用到公网的新手 | 无需购买服务器 | 5-10分钟完成

---

## 📌 方案对比

| 方案 | 费用 | 难度 | 适用场景 | 推荐指数 |
|------|------|------|----------|----------|
| **Render + Cloudflare** | 完全免费 | ⭐ 简单 | 测试/小流量 | ⭐⭐⭐⭐⭐ |
| Railway | 免费$5额度/月 | ⭐⭐ 中等 | 中小流量 | ⭐⭐⭐⭐ |
| 腾讯云/阿里云服务器 | ~70元/月 | ⭐⭐⭐ 复杂 | 生产环境 | ⭐⭐⭐ |

---

## 🎯 推荐方案：Render（免费） + Cloudflare

### 方案优势

1. **完全免费**：不需要信用卡，不需要买服务器
2. **5分钟部署**：不需要懂Linux、SSH、Nginx等复杂技术
3. **自动HTTPS**：Render自动提供SSL证书
4. **结合Cloudflare**：
   - 加速中国访问速度
   - 缓存静态资源，减少服务器负载
   - 防止Render免费版休眠（15分钟无访问会休眠）

### 方案局限性

1. **数据持久化问题**：
   - Render免费版重启会丢失SQLite数据
   - **解决方案**：使用外部PostgreSQL数据库（后面会讲）

2. **自动休眠**：
   - 15分钟无访问会休眠，下次访问需要10-20秒唤醒
   - **解决方案**：配合Cloudflare Workers定时ping（后面会讲）

3. **运行时间限制**：
   - 每月750小时免费（约31天），超出会暂停服务
   - **对于小流量活动完全够用**

---

## 📝 部署步骤（超详细）

### 阶段一：准备工作（5分钟）

#### 1. 注册 Render 账号

1. 访问：https://render.com
2. 点击 **"Get Started for Free"**
3. 使用 GitHub/GitLab/Google 账号登录（推荐GitHub）

#### 2. 准备代码仓库

**方式A：使用Git（推荐）**

```bash
# 在项目根目录执行
cd E:/GitRepo/Local/MyProject/LuckyLocker

# 创建.gitignore文件（如果没有）
echo "*.db" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

# 推送到GitHub
git add .
git commit -m "准备部署到Render"
git push origin master
```

**方式B：如果没有GitHub仓库**
1. 在GitHub创建新仓库：https://github.com/new
2. 仓库名：`LuckyLocker`
3. 设置为 **Public**（免费部署需要公开仓库）
4. 按照GitHub提示推送代码

---

### 阶段二：修改代码以支持部署（10分钟）

#### 1. 创建 Render 配置文件

在项目根目录创建 `render.yaml`：

```yaml
services:
  - type: web
    name: luckylocker
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "cd backend && gunicorn -w 2 -b 0.0.0.0:$PORT app:app"
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
```

#### 2. 更新 requirements.txt

确保包含以下依赖：

```txt
Flask==3.0.0
flask-cors==4.0.0
gunicorn==21.2.0
```

#### 3. 修改 backend/app.py

**问题**：Render需要从环境变量读取端口号

**解决**：修改 `backend/app.py` 最后几行：

找到这部分代码（通常在文件末尾）：

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

改为：

```python
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # 支持Render的环境变量
    debug = os.environ.get('DEBUG', 'False') == 'True'  # 生产环境关闭debug
    app.run(host='0.0.0.0', port=port, debug=debug)
```

#### 4. 提交代码

```bash
git add .
git commit -m "添加Render部署配置"
git push origin master
```

---

### 阶段三：部署到 Render（5分钟）

#### 1. 创建 Web Service

1. 登录Render后，点击 **"New +"** → **"Web Service"**
2. 连接GitHub仓库：
   - 如果是第一次，需要授权Render访问GitHub
   - 选择 `LuckyLocker` 仓库
3. 填写配置：
   - **Name**：`luckylocker`（或任意名称）
   - **Region**：选择 **Singapore**（新加坡，离中国最近）
   - **Branch**：`master`
   - **Root Directory**：留空
   - **Environment**：`Python 3`
   - **Build Command**：`pip install -r requirements.txt`
   - **Start Command**：`cd backend && gunicorn -w 2 -b 0.0.0.0:$PORT app:app`
4. 选择 **Free** 计划
5. 点击 **"Create Web Service"**

#### 2. 等待部署

- 部署大约需要2-5分钟
- 你会看到实时日志
- 看到 **"Your service is live"** 表示部署成功

#### 3. 测试访问

- Render会自动分配一个域名，格式：`https://luckylocker-xxxx.onrender.com`
- 点击域名，测试是否能访问抽奖页面
- 访问管理后台：`https://luckylocker-xxxx.onrender.com/admin.html`

---

### 阶段四：绑定自定义域名（5分钟）

#### 1. 在 Render 添加域名

1. 在Render服务页面，点击 **"Settings"**
2. 找到 **"Custom Domain"** 部分
3. 点击 **"Add Custom Domain"**
4. 输入：`julio98.dpdns.org`
5. Render会显示需要添加的DNS记录：
   ```
   类型：CNAME
   名称：julio98 (或 @)
   目标：luckylocker-xxxx.onrender.com
   ```

#### 2. 在 Cloudflare 配置DNS

1. 登录Cloudflare：https://dash.cloudflare.com
2. 选择你的域名（根域名，如 `dpdns.org`）
3. 点击 **"DNS"** → **"Records"**
4. 添加记录：
   - **类型**：CNAME
   - **名称**：`julio98`
   - **目标**：`luckylocker-xxxx.onrender.com`（替换为你的Render域名）
   - **代理状态**：**已代理**（橙色云朵图标）
   - **TTL**：Auto
5. 点击 **"Save"**

#### 3. 等待生效

- DNS生效大约需要5-10分钟
- 访问：`https://julio98.dpdns.org`
- 成功！🎉

---

### 阶段五：解决数据持久化问题（重要！）

#### 问题说明

- Render免费版每次重启会清空文件（包括SQLite数据库）
- 导致格子配置、抽奖记录等数据丢失

#### 解决方案选择

**方案A：使用外部PostgreSQL数据库（推荐）**

1. **注册免费PostgreSQL**：
   - Render自带免费PostgreSQL（90天过期）
   - 或使用 ElephantSQL（永久免费20MB）：https://www.elephantsql.com
   - 或使用 Supabase（永久免费500MB）：https://supabase.com

2. **修改代码支持PostgreSQL**：
   ```bash
   # 添加依赖到 requirements.txt
   echo "psycopg2-binary==2.9.9" >> requirements.txt
   echo "SQLAlchemy==2.0.23" >> requirements.txt
   ```

3. **修改 backend/app.py**：
   
   在文件开头添加：
   ```python
   import os
   from sqlalchemy import create_engine
   
   # 数据库配置（支持SQLite和PostgreSQL）
   DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///luckylocker.db')
   # 修复Render的PostgreSQL URL格式
   if DATABASE_URL.startswith('postgres://'):
       DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
   ```

   找到数据库初始化部分，替换为：
   ```python
   import sqlite3
   
   def get_db():
       if DATABASE_URL.startswith('postgresql://'):
           # 使用PostgreSQL（需要改写所有SQL语句）
           conn = psycopg2.connect(DATABASE_URL)
       else:
           # 使用SQLite
           conn = sqlite3.connect('luckylocker.db')
       conn.row_factory = sqlite3.Row
       return conn
   ```

   **注意**：这需要大量修改SQL语句（SQLite和PostgreSQL语法不同）

**方案B：使用外部文件存储（简单但不推荐）**

- 使用 GitHub Gist 存储JSON配置
- 每次启动从Gist读取配置
- 缺点：抽奖记录无法持久化

**方案C：接受数据丢失（适合测试）**

- 如果只是测试活动，每次重启重新配置即可
- 可以在管理后台导出/导入配置

#### 推荐实施

**对于项目初期测试，建议先使用方案C**，等活动正式上线再迁移到PostgreSQL。

---

### 阶段六：优化配置（可选）

#### 1. 防止Render休眠

Render免费版15分钟无访问会休眠，使用Cloudflare Workers定时唤醒：

1. 在Cloudflare，点击 **"Workers & Pages"**
2. 创建新Worker，代码如下：

```javascript
export default {
  async scheduled(event, env, ctx) {
    await fetch('https://julio98.dpdns.org/api/ping');
  },
};
```

3. 添加Cron触发器：`*/10 * * * *`（每10分钟ping一次）

#### 2. 启用Cloudflare缓存

1. 在Cloudflare，点击 **"Caching"** → **"Configuration"**
2. 缓存级别：**Standard**
3. 添加页面规则（Page Rules）：
   ```
   https://julio98.dpdns.org/frontend/*
   缓存级别：Cache Everything
   边缘缓存TTL：1 hour
   ```

#### 3. 启用HTTPS强制跳转

1. 在Cloudflare，点击 **"SSL/TLS"** → **"Edge Certificates"**
2. 开启 **"Always Use HTTPS"**
3. 加密模式选择：**Full (strict)**

---

## 📊 其他经济实惠的部署方案

### 方案2：Railway（推荐指数 ⭐⭐⭐⭐）

**优势**：
- 每月$5免费额度（约500小时运行时间）
- 支持PostgreSQL数据库
- 更稳定，不会自动休眠

**步骤**：
1. 注册：https://railway.app
2. 连接GitHub仓库
3. 一键部署（比Render更简单）
4. 配置域名（同Render）

**劣势**：需要信用卡验证（不扣费）

---

### 方案3：Vercel + Serverless（高级）

**优势**：
- 完全免费，不会休眠
- 全球CDN加速
- 适合高并发

**劣势**：
- 需要改造代码为Serverless架构
- 不支持SQLite，必须用外部数据库
- 配置复杂（不适合新手）

---

### 方案4：本地服务器 + 内网穿透（临时方案）

**适合**：短期活动（1-7天）

**工具**：
- 花生壳（免费版，1GB流量/月）：https://hsk.oray.com
- ngrok（免费版，有流量限制）：https://ngrok.com
- Cloudflare Tunnel（推荐，免费无限制）

**步骤（Cloudflare Tunnel）**：

1. 安装 cloudflared：
   ```bash
   # Windows
   下载：https://github.com/cloudflare/cloudflared/releases
   ```

2. 登录Cloudflare：
   ```bash
   cloudflared tunnel login
   ```

3. 创建隧道：
   ```bash
   cloudflared tunnel create luckylocker
   ```

4. 启动隧道：
   ```bash
   cloudflared tunnel --url http://localhost:5000 run luckylocker
   ```

5. 在Cloudflare配置DNS指向隧道

**优势**：
- 完全免费
- 数据在本地，无持久化问题

**劣势**：
- 电脑必须一直开着
- 网络中断会断线
- 不适合长期运行

---

### 方案5：购买云服务器（生产级）

**适合**：正式商用、长期运行

**推荐服务商**：

| 服务商 | 配置 | 价格 | 适用场景 |
|--------|------|------|----------|
| 腾讯云轻量服务器 | 2核2G 4M | ~70元/月 | 中小流量 |
| 阿里云ECS | 2核2G 3M | ~80元/月 | 中小流量 |
| 搬瓦工VPS | 1核1G 1T流量 | $49/年 | 小流量 |

**部署步骤**：参考 `DEPLOY.md` 中的详细教程

---

## 🎯 方案推荐矩阵

### 按使用场景选择

| 场景 | 推荐方案 | 理由 |
|------|----------|------|
| **测试/学习** | Render免费版 | 简单易用，快速上线 |
| **短期活动（1-7天）** | Cloudflare Tunnel | 免费，数据不丢失 |
| **小流量活动（<100人/天）** | Render + PostgreSQL | 免费且稳定 |
| **中流量活动（100-1000人/天）** | Railway | 性能更好，$5/月 |
| **正式商用** | 云服务器 | 完全可控，70元/月起 |

### 按预算选择

| 预算 | 推荐方案 | 预期效果 |
|------|----------|----------|
| **0元** | Render/Railway免费版 | 够用，有限制 |
| **$5/月** | Railway付费版 | 稳定可靠 |
| **70元/月** | 腾讯云/阿里云 | 生产级，可扩展 |

---

## ⚠️ 常见问题

### Q1: Render部署后访问很慢？

**原因**：Render服务器在国外，国内访问慢

**解决**：
1. 配合Cloudflare CDN加速
2. 在Render选择新加坡节点（Singapore）
3. 或改用Railway（速度稍快）

---

### Q2: 数据库文件丢失怎么办？

**原因**：Render免费版重启会清空文件

**解决**：
1. 使用外部PostgreSQL数据库（推荐）
2. 定期导出配置到GitHub Gist
3. 或改用云服务器

---

### Q3: Render自动休眠怎么办？

**原因**：15分钟无访问会休眠

**解决**：
1. 配置Cloudflare Workers定时ping
2. 或使用Railway（不会休眠）
3. 或升级Render付费版（$7/月）

---

### Q4: 如何备份数据？

**方法1：SQLite备份**
```bash
# 下载数据库文件
在Render Console中执行：
cat backend/luckylocker.db > backup.db
# 然后复制内容到本地
```

**方法2：使用外部数据库**
- PostgreSQL自动备份
- 或使用Supabase（自带备份功能）

---

### Q5: Cloudflare配置错误怎么办？

**检查清单**：
1. DNS记录类型是否为CNAME
2. 目标是否为Render分配的域名
3. 代理状态是否开启（橙色云朵）
4. 等待5-10分钟DNS生效

**查看DNS是否生效**：
```bash
# Windows PowerShell
nslookup julio98.dpdns.org
```

---

## 📖 实施建议

### 第一阶段：快速上线（1天）

1. ✅ 使用 **Render免费版** 部署
2. ✅ 配置Cloudflare域名
3. ✅ 测试基本功能
4. ⚠️ 接受数据可能丢失（测试阶段）

### 第二阶段：稳定运行（1周）

1. ✅ 改造代码支持PostgreSQL
2. ✅ 配置Cloudflare Workers防休眠
3. ✅ 启用缓存和HTTPS
4. ✅ 监控服务状态

### 第三阶段：正式商用（可选）

1. 根据流量决定是否升级
2. 考虑迁移到云服务器
3. 或升级Railway付费版

---

## 🎉 总结

### 最推荐的起步方案

**Render（免费） + Cloudflare + PostgreSQL（免费）**

**总成本**：0元  
**部署时间**：20分钟  
**适用场景**：测试、小流量活动  

### 实施优先级

1. **高优先级**（必做）：
   - ✅ Render部署
   - ✅ Cloudflare域名配置
   - ✅ 基本功能测试

2. **中优先级**（建议做）：
   - ⚡ 配置PostgreSQL数据库
   - ⚡ 防休眠机制
   - ⚡ HTTPS强制跳转

3. **低优先级**（可选）：
   - 💡 缓存优化
   - 💡 监控告警
   - 💡 性能调优

---

## 📞 需要帮助？

如果在部署过程中遇到问题，可以：

1. 查看Render部署日志（Logs选项卡）
2. 检查Cloudflare DNS配置
3. 确认代码是否正确推送到GitHub

---

**祝部署顺利！** 🚀
