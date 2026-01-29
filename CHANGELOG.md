# 更新日志

## [0.2.0] - 2026-01-29

### 🚀 部署相关

#### 新增完整部署文档体系
- ✨ **[快速部署指南](docs/deployment/QUICKSTART.md)**：5步完成部署，20分钟上线公网
- ✨ **[方案全对比](docs/deployment/DEPLOYMENT_COMPARISON.md)**：按预算/流量/技术水平选择最佳方案
- ✨ **[完整部署指南](docs/deployment/DEPLOY_PUBLIC.md)**：涵盖Render、Railway、Cloudflare Tunnel等6种方案
- ✨ **[部署检查清单](docs/deployment/DEPLOYMENT_CHECKLIST.md)**：可视化部署步骤，逐项打勾完成
- ✨ **[部署指南索引](docs/deployment/DEPLOY_GUIDE.md)**：文档导航，不知道看哪个？从这里开始

#### 云平台部署支持
- ✨ **Render平台配置**：新增 `render.yaml` 自动部署配置
- ✨ **环境变量支持**：`backend/app.py` 支持 PORT 和 DEBUG 环境变量，适配各云平台
- ✨ **Gunicorn生产服务器**：`requirements.txt` 新增 gunicorn 依赖

#### 工具脚本
- ✨ **Cloudflare Worker防休眠脚本**：`scripts/cloudflare-worker-keepalive.js`
- ✨ **项目清理脚本**：`scripts/cleanup.sh` 和 `scripts/cleanup.bat`

### 📁 项目结构优化

#### 新增文件夹
- ✅ `docs/` - 统一管理项目文档
- ✅ `docs/deployment/` - 部署相关文档
- ✅ `scripts/` - 工具脚本

#### 文件整理
- 📂 所有部署文档移至 `docs/deployment/`
- 📂 所有脚本移至 `scripts/`
- 📄 中文文件名改为英文（避免Git跨平台问题）
- 📄 新增 `.gitignore` 防止数据库文件误提交

#### 文档更新
- 📝 `README.md` 更新部署章节，添加文档链接
- 📝 新增 `docs/STRUCTURE.md` 说明项目结构
- 📝 新增 `docs/WECHAT_MINIPROGRAM_DESIGN.md` 微信小程序设计文档

### 🎯 部署方案概览

| 方案 | 费用 | 难度 | 推荐场景 |
|------|------|------|----------|
| Render免费版 | ¥0 | ⭐ 极简单 | 测试/小流量 |
| Railway | ¥35/月 | ⭐⭐ 简单 | 中流量活动 |
| 云服务器 | ¥70+/月 | ⭐⭐⭐⭐ 复杂 | 正式商用 |

### 💡 推荐新手方案

**Render（免费） + Cloudflare**
- ✅ 完全免费
- ✅ 5分钟部署
- ✅ 自动HTTPS
- ✅ 适合测试和小流量活动

查看 [docs/deployment/QUICKSTART.md](docs/deployment/QUICKSTART.md) 开始部署！

---

## [0.1.0] - 2026-01-22

### 新增功能
- ✨ **系统版本管理**：版本号 0.1.0，在前后端显示
- 🎬 **抽奖动画效果**：3秒转动动画，8个格子随机高亮切换
- 🛡️ **冷却防刷机制**：
  - 同一IP/UA只能抽一次
  - 不同IP/UA需等待1-3分钟随机时间
  - 提示"数据同步中，请稍后刷新重试"
- 🎫 **绿通凭证系统**：
  - 后台可添加凭证（手机号/订单号/自定义码）
  - 设置剩余抽奖次数和有效期
  - 用户通过凭证可绕过限制抽奖
- 🎁 **预设产品池**：
  - 后台管理产品名称列表
  - 前端从产品池随机显示，每5秒刷新
  - 产品名称不一定对应实际格子商品

### 界面优化
- 格子柜后台显示完整开锁密码（格式：格子号-密码）
- 移除"全部重置"按钮，改为逐个管理
- 商品名称输入框提示文字优化

### 技术改进
- 数据库新增 `greenlist` 表（绿通凭证）
- 数据库新增 `product_pool` 表（产品池）
- `draw_records` 表新增 `last_draw_time` 字段
- API新增绿通凭证验证接口
- API新增产品池管理接口

### 防作弊强化
- IP + User-Agent 双重识别
- 随机冷却时间（1-3分钟）
- 绿通凭证有效期和次数限制
- 抽奖记录包含时间戳用于冷却判断

---

**升级说明**：
1. 首次启动会自动创建新表和初始化数据
2. 旧数据库会自动迁移兼容
3. 建议备份数据库后再升级
