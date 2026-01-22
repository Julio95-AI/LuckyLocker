# 🎁 LuckyLocker - 幸运格子柜抽奖系统

一个简单易用的格子柜抽奖系统，适合店铺做活动推广。用户扫码抽奖，中奖后获得格子密码取货。

## 📋 功能特点

- ✅ **用户抽奖**：扫码访问，每天限抽一次
- ✅ **随机分配**：从8个格子中随机抽取，显示开锁密码
- ✅ **名额限制**：可配置每日中奖人数（默认2人）
- ✅ **后台管理**：配置商品、更新密码、查看记录
- ✅ **简单部署**：单文件后端，HTML前端，无需复杂配置

## 🏗️ 项目结构

```
LuckyLocker/
├── backend/
│   └── app.py              # Flask后端（包含所有API）
├── frontend/
│   ├── index.html          # 用户抽奖页面
│   └── admin.html          # 管理后台页面
├── requirements.txt        # Python依赖
└── README.md              # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

确保已安装 Python 3.7 及以上版本，然后安装依赖：

```bash
cd LuckyLocker
pip install -r requirements.txt
```

### 2. 启动服务

```bash
cd backend
python app.py
```

启动成功后，你会看到：

```
==================================================
LuckyLocker 抽奖系统启动
前端访问: http://localhost:5000
管理后台: http://localhost:5000/admin.html
==================================================
```

### 3. 访问系统

- **用户抽奖页面**：`http://localhost:5000`
- **管理后台**：`http://localhost:5000/admin.html`

## 📱 使用流程

### 用户端（抽奖）

1. 用户扫码或访问抽奖页面
2. 点击"立即抽奖"按钮
3. 系统随机分配格子，显示开锁密码（如：`2-038`）
4. 用户凭密码到格子柜取货

### 管理端（后台）

1. 访问 `http://localhost:5000/admin.html`
2. **仪表盘**：查看今日抽奖统计
3. **格子管理**：
   - 设置每个格子的密码
   - 设置每个格子的商品名称
   - 设置格子可用/不可用状态
   - 放置新货品后，点击"重置所有格子为可用"
4. **系统配置**：
   - 设置每日中奖名额（1-8人）
   - 设置活动状态（进行中/今日已结束/活动已停止）
5. **抽奖记录**：查看今天所有抽奖记录

## ⚙️ 配置说明

### 每日名额限制

在管理后台 > 系统配置中修改"每日中奖名额限制"，例如：
- 设置为 `2`：每天只有2个人能中奖
- 设置为 `8`：每天最多8人中奖（所有格子）

### 活动状态

- **进行中**：正常抽奖
- **今日已结束**：今天活动结束，显示"今天已抽完"
- **活动已停止**：整个活动结束，显示"活动已结束"

### 格子密码设置

建议密码格式：`001`, `002`, `003` ... `008`
实际开锁密码会显示为：`格子号-密码`，例如 `2-038` 表示2号格子，密码038

## 🌐 部署到服务器

### 方案1：直接部署（适合小规模使用）

1. 将整个项目上传到服务器
2. 安装依赖：`pip install -r requirements.txt`
3. 修改 `app.py` 最后一行，改为生产模式：
   ```python
   app.run(host='0.0.0.0', port=5000, debug=False)
   ```
4. 启动服务：`python app.py`

### 方案2：使用 Nginx + Gunicorn（推荐生产环境）

1. 安装 Gunicorn：
   ```bash
   pip install gunicorn
   ```

2. 启动 Gunicorn：
   ```bash
   cd backend
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. 配置 Nginx 反向代理：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### 方案3：使用 Cloudflare + 服务器

1. 将域名 DNS 托管到 Cloudflare
2. 在服务器上部署项目（方案1或2）
3. 在 Cloudflare 添加 A 记录指向服务器IP
4. 开启 Cloudflare 的 CDN 和 SSL

## 📊 数据库说明

项目使用 SQLite 数据库，数据库文件会自动创建在 `backend/luckylocker.db`

包含3个表：
- `lockers`：格子柜信息（8个格子）
- `draw_records`：抽奖记录
- `system_config`：系统配置

### 备份数据库

```bash
# 备份
cp backend/luckylocker.db backend/luckylocker_backup.db

# 恢复
cp backend/luckylocker_backup.db backend/luckylocker.db
```

### 重置数据库

如果需要清空所有数据，删除数据库文件即可：
```bash
rm backend/luckylocker.db
# 重新启动 app.py 会自动创建新数据库
```

## 🎯 常见问题

### Q1: 用户如何被识别为"同一个人"？

A: 系统通过用户的 IP 地址 + User-Agent（浏览器信息）生成唯一标识。同一设备同一天只能抽一次。

### Q2: 如果想让格子只能被抽一次怎么办？

A: 打开 `backend/app.py`，找到第115行左右，取消注释：
```python
# 标记格子为不可用（可选：如果想让格子只能被抽一次）
c.execute('UPDATE lockers SET is_available = 0 WHERE id = ?', (locker_id,))
```

### Q3: 如何更改端口？

A: 修改 `backend/app.py` 最后一行的 `port=5000` 改为其他端口，例如 `port=8080`

### Q4: 如何自定义格子数量？

A: 打开 `backend/app.py`，找到 `init_db()` 函数中的：
```python
for i in range(1, 9):  # 改为 range(1, 5) 表示4个格子
```
同时修改前端页面的格子显示。

### Q5: 可以用微信小程序吗？

A: 可以！前端代码已经兼容移动端，你可以：
1. 将 HTML 页面部署到服务器
2. 生成二维码让用户扫码访问
3. 或者参考 `frontend/index.html` 的 API 调用方式，开发微信小程序

## 🔒 安全建议

1. **生产环境**：
   - 修改 `app.py` 中的 `debug=False`
   - 为管理后台添加密码保护（可以在 Nginx 层面配置 Basic Auth）
   
2. **防止作弊**：
   - 可以要求用户输入手机号并发送验证码
   - 可以集成微信登录获取 OpenID

3. **数据安全**：
   - 定期备份数据库文件
   - 设置文件权限，防止未授权访问

## 📞 技术支持

如遇问题，请检查：
1. Python 版本是否 >= 3.7
2. 依赖是否正确安装
3. 端口是否被占用
4. 防火墙是否开放端口

## 📄 许可证

MIT License - 自由使用，无需授权

---

**祝你的活动大卖！** 🎉
