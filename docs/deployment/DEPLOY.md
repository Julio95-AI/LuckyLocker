# 🚀 部署指南

## 本地测试（Windows）

### 步骤1：安装Python
1. 下载 Python 3.9+：https://www.python.org/downloads/
2. 安装时勾选 "Add Python to PATH"

### 步骤2：安装依赖
```bash
cd LuckyLocker
pip install -r requirements.txt
```

### 步骤3：启动服务
双击 `start.bat` 或在命令行运行：
```bash
start.bat
```

### 步骤4：访问
- 用户页面：http://localhost:5000
- 管理后台：http://localhost:5000/admin.html

---

## 部署到云服务器（腾讯云/阿里云）

### 方案A：快速部署（适合新手）

#### 1. 购买服务器
- 推荐：腾讯云轻量应用服务器（2核2G，约70元/月）
- 系统：Ubuntu 20.04 或 CentOS 7

#### 2. 连接服务器
使用 SSH 工具（如 PuTTY、Xshell）连接服务器

#### 3. 安装环境
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和 pip
sudo apt install python3 python3-pip -y

# 安装 Git（用于上传代码）
sudo apt install git -y
```

#### 4. 上传代码
方式1：使用 Git
```bash
cd /home
git clone <你的仓库地址>
cd LuckyLocker
```

方式2：使用 FTP 工具（如 FileZilla）上传整个文件夹

#### 5. 安装依赖
```bash
cd /home/LuckyLocker
pip3 install -r requirements.txt
```

#### 6. 启动服务
```bash
cd backend
nohup python3 app.py > /dev/null 2>&1 &
```

#### 7. 开放端口
在云服务器控制台的"防火墙"或"安全组"中开放 5000 端口

#### 8. 访问
http://你的服务器IP:5000

---

### 方案B：生产级部署（推荐）

使用 Nginx + Gunicorn + Supervisor

#### 1. 安装 Gunicorn
```bash
pip3 install gunicorn
```

#### 2. 测试 Gunicorn
```bash
cd /home/LuckyLocker/backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 3. 安装 Supervisor（进程守护）
```bash
sudo apt install supervisor -y
```

#### 4. 配置 Supervisor
创建配置文件：
```bash
sudo nano /etc/supervisor/conf.d/luckylocker.conf
```

输入以下内容：
```ini
[program:luckylocker]
directory=/home/LuckyLocker/backend
command=gunicorn -w 4 -b 127.0.0.1:5000 app:app
autostart=true
autorestart=true
stderr_logfile=/var/log/luckylocker.err.log
stdout_logfile=/var/log/luckylocker.out.log
```

保存并退出（Ctrl+X, Y, Enter）

#### 5. 启动 Supervisor
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start luckylocker
```

#### 6. 安装 Nginx
```bash
sudo apt install nginx -y
```

#### 7. 配置 Nginx
创建配置文件：
```bash
sudo nano /etc/nginx/sites-available/luckylocker
```

输入以下内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 改成你的域名或IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

保存并退出

#### 8. 启用配置
```bash
sudo ln -s /etc/nginx/sites-available/luckylocker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. 访问
http://your-domain.com

---

## 配置 Cloudflare

### 为什么用 Cloudflare？
- ✅ 免费 CDN 加速
- ✅ 免费 SSL 证书（HTTPS）
- ✅ DDoS 防护
- ✅ 隐藏真实服务器 IP

### 配置步骤

#### 1. 注册 Cloudflare
访问：https://www.cloudflare.com
注册账号（免费）

#### 2. 添加域名
- 点击"添加站点"
- 输入你的域名（如：julio98.dpdns.org）
- 选择"免费计划"

#### 3. 修改域名 DNS
Cloudflare 会给你2个 DNS 服务器地址，例如：
```
ns1.cloudflare.com
ns2.cloudflare.com
```

到你的域名注册商（如阿里云、腾讯云）修改 DNS 为上述地址

#### 4. 添加 DNS 记录
在 Cloudflare DNS 管理页面：
- 类型：A
- 名称：@ （或者子域名，如 lucky）
- 内容：你的服务器IP
- 代理状态：已代理（橙色云朵）

#### 5. 配置 SSL/TLS
- 点击"SSL/TLS"
- 加密模式选择："完全"或"灵活"
- 等待几分钟，HTTPS 自动生效

#### 6. 优化设置（可选）
- **缓存规则**：静态文件缓存
- **防火墙规则**：限制访问频率
- **页面规则**：设置缓存策略

#### 7. 访问
https://your-domain.com

---

## 使用二维码推广

### 生成二维码

#### 方式1：在线生成
访问：https://cli.im
输入你的网址，生成二维码

#### 方式2：使用 Python 生成
```bash
pip install qrcode pillow
```

创建文件 `generate_qr.py`：
```python
import qrcode

url = "https://your-domain.com"  # 改成你的网址

qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("qrcode.png")
print("二维码已生成：qrcode.png")
```

运行：
```bash
python generate_qr.py
```

### 打印海报
1. 设计海报，加上二维码
2. 添加文字："扫码免费抽奖，领取神秘礼品"
3. 打印并张贴在店铺显眼位置

---

## 微信小程序版本（可选）

如果你想开发微信小程序版本，可以参考以下步骤：

### 1. 注册微信小程序
访问：https://mp.weixin.qq.com
注册小程序账号

### 2. 开发工具
下载微信开发者工具：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html

### 3. 前端代码
参考 `frontend/index.html` 的逻辑，用小程序语法重写：

**index.wxml**（界面）
```xml
<view class="container">
  <view class="locker-grid">
    <view class="locker-cell" wx:for="{{lockers}}" wx:key="id">
      {{item.id}}
    </view>
  </view>
  <button bindtap="draw">立即抽奖</button>
</view>
```

**index.js**（逻辑）
```javascript
Page({
  data: {
    lockers: [1,2,3,4,5,6,7,8]
  },
  
  draw() {
    wx.request({
      url: 'https://your-domain.com/api/draw',
      method: 'POST',
      success: (res) => {
        if (res.data.success && res.data.lucky) {
          wx.showModal({
            title: '恭喜中奖',
            content: '密码：' + res.data.order_code
          });
        } else {
          wx.showToast({ title: res.data.message });
        }
      }
    });
  }
});
```

### 4. 配置服务器域名
在小程序后台 > 开发管理 > 开发设置 > 服务器域名
添加：https://your-domain.com

---

## 常用命令

### 查看服务状态
```bash
sudo supervisorctl status luckylocker
```

### 重启服务
```bash
sudo supervisorctl restart luckylocker
```

### 查看日志
```bash
tail -f /var/log/luckylocker.out.log
tail -f /var/log/luckylocker.err.log
```

### 停止服务
```bash
sudo supervisorctl stop luckylocker
```

---

## 故障排查

### 问题1：无法访问
- 检查防火墙是否开放端口
- 检查服务是否启动：`ps aux | grep python`
- 检查端口是否被占用：`netstat -tunlp | grep 5000`

### 问题2：数据库错误
- 检查文件权限：`ls -la backend/luckylocker.db`
- 删除数据库重新生成：`rm backend/luckylocker.db`

### 问题3：CORS 跨域错误
- 确保安装了 flask-cors
- 检查 API 响应头是否包含 CORS 信息

---

**部署成功后，记得测试一下所有功能！** 🎉
