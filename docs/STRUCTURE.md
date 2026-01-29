# 📁 项目文档结构说明

> v0.2 版本整理后的文档组织结构

---

## 📂 目录结构

```
LuckyLocker/
├── backend/                      # 后端代码
│   ├── app.py                   # Flask应用主文件
│   └── uploads/                 # 用户上传文件
│
├── frontend/                     # 前端代码
│   ├── index.html              # 用户抽奖页面
│   └── admin.html              # 管理后台页面
│
├── docs/                        # 📚 项目文档（新增）
│   ├── deployment/             # 部署相关文档
│   │   ├── QUICKSTART.md       # 快速部署指南（5分钟上手）
│   │   ├── DEPLOY_PUBLIC.md    # 完整部署方案详解
│   │   ├── DEPLOYMENT_COMPARISON.md  # 方案对比表
│   │   ├── DEPLOYMENT_CHECKLIST.md   # 可视化检查清单
│   │   ├── DEPLOY_GUIDE.md     # 部署指南索引
│   │   └── DEPLOY.md           # 传统服务器部署
│   └── WECHAT_MINIPROGRAM_DESIGN.md  # 微信小程序设计文档
│
├── scripts/                     # 🔧 工具脚本（新增）
│   ├── cleanup.sh              # Linux清理脚本
│   ├── cleanup.bat             # Windows清理脚本
│   └── cloudflare-worker-keepalive.js  # Cloudflare Worker防休眠脚本
│
├── uploads/                     # 上传文件存储
│
├── .gitignore                   # Git忽略配置
├── render.yaml                  # Render平台部署配置
├── requirements.txt             # Python依赖
├── README.md                    # 项目说明（主入口）
├── CHANGELOG.md                 # 更新日志
├── start.sh                     # Linux启动脚本
└── start.bat                    # Windows启动脚本
```

---

## 📖 文档导航

### 新手入门

1. **[README.md](../README.md)** - 从这里开始了解项目
2. **[docs/deployment/QUICKSTART.md](deployment/QUICKSTART.md)** - 快速部署到公网

### 部署相关

- **[docs/deployment/DEPLOY_GUIDE.md](deployment/DEPLOY_GUIDE.md)** - 部署指南索引（不知道看哪个？看这个）
- **[docs/deployment/QUICKSTART.md](deployment/QUICKSTART.md)** - 5步快速部署
- **[docs/deployment/DEPLOYMENT_COMPARISON.md](deployment/DEPLOYMENT_COMPARISON.md)** - 方案全对比
- **[docs/deployment/DEPLOY_PUBLIC.md](deployment/DEPLOY_PUBLIC.md)** - 完整部署指南
- **[docs/deployment/DEPLOYMENT_CHECKLIST.md](deployment/DEPLOYMENT_CHECKLIST.md)** - 部署检查清单
- **[docs/deployment/DEPLOY.md](deployment/DEPLOY.md)** - 传统服务器部署

### 开发相关

- **[docs/WECHAT_MINIPROGRAM_DESIGN.md](WECHAT_MINIPROGRAM_DESIGN.md)** - 微信小程序设计文档
- **[CHANGELOG.md](../CHANGELOG.md)** - 版本更新日志

---

## 🔧 脚本说明

### scripts/cleanup.sh & cleanup.bat
**功能**：清理项目临时文件
- 清理Python缓存（`__pycache__`）
- 清理数据库文件（`*.db`）
- 清理上传文件

**使用方法**：
```bash
# Linux/Mac
bash scripts/cleanup.sh

# Windows
scripts\cleanup.bat
```

### scripts/cloudflare-worker-keepalive.js
**功能**：防止Render免费版自动休眠
- 部署到Cloudflare Workers
- 每10分钟自动ping应用

**使用方法**：参考 [docs/deployment/QUICKSTART.md](deployment/QUICKSTART.md) 第5步

---

## 📝 v0.2 版本文档整理说明

### 变更内容

#### 新增文件夹
- ✅ `docs/` - 统一管理项目文档
- ✅ `docs/deployment/` - 部署相关文档
- ✅ `scripts/` - 工具脚本

#### 文件移动
- ✅ 所有部署文档 → `docs/deployment/`
- ✅ 所有脚本文件 → `scripts/`
- ✅ 旧的 `doc/` 文件夹内容 → `docs/`

#### 文件重命名
- ✅ `部署指南索引.md` → `docs/deployment/DEPLOY_GUIDE.md`（避免中文文件名）
- ✅ `基于域名的...md` → `docs/WECHAT_MINIPROGRAM_DESIGN.md`

### 整理原因

1. **符合行业规范**：docs/ 和 scripts/ 是开源项目的标准目录
2. **更好的组织**：文档按类型分类，便于查找
3. **避免混乱**：根目录保持简洁，只保留必要文件
4. **跨平台兼容**：避免中文文件名在Git中出现编码问题

### 配置文件说明

以下文件**必须**保留在根目录（行业惯例）：
- ✅ `.gitignore` - Git忽略配置
- ✅ `render.yaml` - 云平台部署配置
- ✅ `requirements.txt` - Python依赖
- ✅ `README.md` - 项目说明
- ✅ `CHANGELOG.md` - 更新日志
- ✅ `start.sh` / `start.bat` - 启动脚本（常用）

---

## 🎯 最佳实践

### ✅ 应该提交到Git的文件

- ✅ 所有源代码（`backend/`, `frontend/`）
- ✅ 所有文档（`docs/`, `README.md`, `CHANGELOG.md`）
- ✅ 配置文件（`.gitignore`, `render.yaml`, `requirements.txt`）
- ✅ 脚本文件（`scripts/`）
- ✅ 启动脚本（`start.sh`, `start.bat`）

### ❌ 不应该提交到Git的文件（已在.gitignore中）

- ❌ 数据库文件（`*.db`, `*.sqlite`）
- ❌ Python缓存（`__pycache__/`, `*.pyc`）
- ❌ 上传文件（`uploads/`, `backend/uploads/`）
- ❌ IDE配置（`.vscode/`, `.idea/`）
- ❌ 日志文件（`*.log`）

---

## 📚 参考其他开源项目

这个目录结构参考了业界标准，类似于：
- [Flask官方示例](https://github.com/pallets/flask)
- [Django项目结构](https://github.com/django/django)
- [Vue.js项目](https://github.com/vuejs/vue)

---

## 🔄 版本历史

- **v0.2 (2026-01-29)**: 整理目录结构，新增docs/和scripts/文件夹
- **v0.1 (2026-01-20)**: 初始版本

---

## 📞 反馈

如果你对文档结构有任何建议，欢迎提Issue或Pull Request！
