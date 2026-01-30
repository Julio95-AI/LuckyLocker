# 多应用架构规划

## 当前架构 vs 推荐架构

### 当前架构（v0.1.0）

```
julio98.dpdns.org/
├── /                          # LuckyLocker 抽奖系统首页
├── /admin.html                # LuckyLocker 管理后台
├── /portal.html               # 应用门户页面（新增）
├── /c7ba572195...txt          # 微信验证文件
└── /api/                      # LuckyLocker API
    ├── /draw                  # 抽奖接口
    ├── /status                # 状态接口
    └── /admin/*               # 管理接口
```

**优点：**
- 简单直接，易于访问
- 无需修改现有代码
- 推广链接短

**缺点：**
- 域名被单个应用占用
- 无法添加其他应用
- API路径不够清晰

---

### 推荐架构（v0.2.0+）

```
julio98.dpdns.org/
├── /                          # 应用门户（展示所有应用）
├── /luckylocker/             # LuckyLocker 抽奖系统 ⭐
│   ├── index.html            # 抽奖页面
│   ├── admin.html            # 管理后台
│   └── /api/                 # LuckyLocker专属API
│       ├── /draw
│       ├── /status
│       └── /admin/*
├── /other-app/               # 其他应用
│   ├── index.html
│   └── /api/
└── /shared/                  # 共享资源（可选）
    ├── /assets/              # 图片、CSS、JS
    └── /api/                 # 跨应用API
```

**优点：**
- ✅ 清晰的路径结构
- ✅ 支持多个应用
- ✅ 独立的API命名空间
- ✅ 便于维护和扩展

**缺点：**
- 需要重构代码
- 推广链接变长（可用短链接解决）
- 需要迁移现有数据

---

## 🎯 迁移策略

### 阶段1：过渡期（当前方案）

**实施步骤：**

1. ✅ 创建 `portal.html` 门户页面（已完成）
2. ✅ 保持 `/` 为抽奖系统（向后兼容）
3. 推广时使用：`julio98.dpdns.org/`（不变）
4. 门户页面访问：`julio98.dpdns.org/portal.html`

**路径映射：**
```
/ → LuckyLocker 首页
/portal.html → 应用门户
/admin.html → LuckyLocker 管理后台
/api/* → LuckyLocker API
```

---

### 阶段2：平滑迁移（未来实施）

**前提条件：**
- 活动结束或暂停
- 用户量较少
- 有时间窗口测试

**实施步骤：**

#### 步骤1：创建子路径应用

```bash
# 创建新的目录结构
frontend/
├── portal.html              # 门户首页
├── luckylocker/            # 抽奖系统目录
│   ├── index.html
│   └── admin.html
└── shared/                 # 共享资源
    └── assets/
```

#### 步骤2：修改Flask路由

```python
# backend/app.py

from flask import Blueprint

# 创建LuckyLocker Blueprint
luckylocker_bp = Blueprint('luckylocker', __name__, url_prefix='/luckylocker')

# 将所有路由移到Blueprint
@luckylocker_bp.route('/')
def index():
    return send_from_directory(app.static_folder, 'luckylocker/index.html')

@luckylocker_bp.route('/api/draw', methods=['POST'])
def draw():
    # 抽奖逻辑
    pass

# 注册Blueprint
app.register_blueprint(luckylocker_bp)

# 根路径指向门户
@app.route('/')
def portal():
    return send_from_directory(app.static_folder, 'portal.html')
```

#### 步骤3：更新前端API路径

```javascript
// frontend/luckylocker/index.html

// 修改前
const API_BASE = '';  
fetch('/api/draw', ...)

// 修改后
const API_BASE = '/luckylocker';
fetch(API_BASE + '/api/draw', ...)
```

#### 步骤4：设置URL重定向

```python
# 保持向后兼容，旧链接自动跳转
@app.route('/')
def index_redirect():
    # 如果访问根路径，检查来源
    # 如果是直接访问（没有Referer），重定向到门户
    # 如果是扫码/分享链接，重定向到LuckyLocker
    return redirect('/luckylocker/')
```

#### 步骤5：更新推广材料

- 更新二维码：`julio98.dpdns.org/luckylocker/`
- 或使用短链接：`tinyurl.com/xxxxx` → `julio98.dpdns.org/luckylocker/`
- 更新海报上的URL

#### 步骤6：测试和部署

```bash
# 本地测试
python backend/app.py

# 访问测试
http://localhost:5000/                    # 门户
http://localhost:5000/luckylocker/        # 抽奖
http://localhost:5000/luckylocker/admin.html  # 管理

# 推送部署
git push github master
```

---

### 阶段3：完全迁移（最终目标）

**特点：**
- 所有应用在子路径下
- 根路径只有门户
- 清晰的路径规范

**路径规范：**
```
/{app-name}/              # 应用首页
/{app-name}/admin.html    # 应用管理（如有）
/{app-name}/api/*         # 应用API
```

---

## 📋 实施检查清单

### 当前阶段（过渡期）
- [x] 创建 portal.html 门户页面
- [x] 创建微信验证文件
- [ ] 测试门户页面显示
- [ ] 决定是否启用门户（可选）

### 迁移准备（可选）
- [ ] 备份当前数据库
- [ ] 创建子目录结构
- [ ] 修改Flask路由
- [ ] 更新前端API调用
- [ ] 设置URL重定向
- [ ] 全面测试功能

### 迁移实施
- [ ] 选择低峰时段
- [ ] 部署新版本
- [ ] 监控错误日志
- [ ] 更新推广材料
- [ ] 通知用户（如需要）

---

## 🎨 添加新应用的模板

### 1. 创建应用目录

```bash
frontend/
└── your-app/
    ├── index.html
    ├── admin.html (可选)
    └── assets/
        ├── css/
        ├── js/
        └── images/
```

### 2. 在Flask中注册应用

```python
# backend/apps/your_app.py
from flask import Blueprint, send_from_directory

your_app_bp = Blueprint('your_app', __name__, url_prefix='/your-app')

@your_app_bp.route('/')
def index():
    return send_from_directory('../frontend/your-app', 'index.html')

@your_app_bp.route('/api/example', methods=['GET'])
def api_example():
    return jsonify({'status': 'ok'})

# backend/app.py
from apps.your_app import your_app_bp
app.register_blueprint(your_app_bp)
```

### 3. 在门户页面添加入口

```html
<!-- frontend/portal.html -->
<a href="/your-app/" class="app-card">
    <div class="app-icon">🎯</div>
    <div class="app-name">您的应用名</div>
    <div class="app-desc">应用描述</div>
    <span class="app-status status-active">运行中</span>
</a>
```

---

## 🔗 相关文档

- [部署指南](./deployment/QUICKSTART.md)
- [微信限制破局](./WECHAT_WORKAROUND.md)
- [海报模板](./POSTER_TEMPLATE.md)

---

## 💡 最佳实践

### 1. 路径命名规范
- 全小写字母
- 使用连字符（-）而非下划线（_）
- 简短但具有描述性
- 示例：`/lucky-draw/`, `/user-center/`, `/product-list/`

### 2. API版本控制
```
/luckylocker/api/v1/draw
/luckylocker/api/v2/draw
```

### 3. 共享资源管理
```
/shared/assets/logo.png      # 全站通用Logo
/shared/api/auth             # 统一认证
```

### 4. 错误处理
- 404页面：友好提示，引导到门户
- 500错误：显示联系方式
- API错误：统一JSON格式

---

## 📊 成本效益分析

### 保持当前架构
- **成本**：0（无需改动）
- **限制**：只能运行一个应用
- **适用**：短期活动，无扩展需求

### 迁移到子路径架构
- **成本**：1-2天开发时间
- **收益**：可运行多个应用，清晰的架构
- **适用**：长期运营，有扩展计划

---

**建议：**
- 当前先使用过渡方案（portal.html作为备用）
- 活动结束后考虑迁移到子路径架构
- 未来添加新应用时再决定是否全面重构

---

**更新日期**：2026-01-29
