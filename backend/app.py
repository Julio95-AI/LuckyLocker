"""
LuckyLocker 抽奖系统后端
简单的Flask应用，提供抽奖和管理API
版本: 0.1.0
"""
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sqlite3
import random
import hashlib
from datetime import datetime, timedelta
import os
import base64

app = Flask(__name__, static_folder='../frontend')
CORS(app)  # 允许跨域访问

VERSION = '0.1.0'
DB_PATH = 'luckylocker.db'

# 使用绝对路径确保文件能被找到
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== 数据库初始化 ====================
def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 格子柜表（8个格子）
    c.execute('''CREATE TABLE IF NOT EXISTS lockers (
        id INTEGER PRIMARY KEY,
        password TEXT NOT NULL,
        product_name TEXT,
        is_available INTEGER DEFAULT 1
    )''')
    
    # 抽奖记录表
    c.execute('''CREATE TABLE IF NOT EXISTS draw_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        locker_id INTEGER,
        draw_time TEXT NOT NULL,
        order_code TEXT
    )''')
    
    # 系统配置表
    c.execute('''CREATE TABLE IF NOT EXISTS system_config (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    # 绿通凭证表（强制重建以移除 UNIQUE 约束）
    # 检查表是否存在
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='greenlist'")
    table_exists = c.fetchone()
    
    old_data = []
    if table_exists:
        # 检查是否有UNIQUE约束
        c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='greenlist'")
        table_sql = c.fetchone()[0]
        if 'UNIQUE' in table_sql.upper():
            print("⚠️  检测到旧的greenlist表有UNIQUE约束，正在重建...")
            # 备份数据
            c.execute('SELECT * FROM greenlist')
            old_data = c.fetchall()
            # 删除旧表
            c.execute('DROP TABLE greenlist')
            print(f"   已备份 {len(old_data)} 条记录")
    
    # 创建新表（无UNIQUE约束）
    c.execute('''CREATE TABLE IF NOT EXISTS greenlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identifier TEXT NOT NULL,
        type TEXT NOT NULL,
        remaining_draws INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        expires_at TEXT
    )''')
    
    # 如果有备份数据，恢复
    if old_data:
        for row in old_data:
            c.execute('''INSERT INTO greenlist 
                       (id, identifier, type, remaining_draws, created_at, expires_at) 
                       VALUES (?, ?, ?, ?, ?, ?)''', row)
        print(f"   ✅ 已恢复 {len(old_data)} 条记录")
    
    # 预设产品池表
    c.execute('''CREATE TABLE IF NOT EXISTS product_pool (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )''')
    
    # 初始化8个格子（如果没有数据）
    c.execute('SELECT COUNT(*) FROM lockers')
    if c.fetchone()[0] == 0:
        for i in range(1, 9):
            c.execute('INSERT INTO lockers (id, password, product_name, is_available) VALUES (?, ?, ?, ?)',
                     (i, f'{i:03d}', f'商品{i}', 1))
    
    # 初始化系统配置
    c.execute('SELECT COUNT(*) FROM system_config')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO system_config (key, value) VALUES (?, ?)', 
                 ('daily_limit', '2'))  # 每天产生2个幸运顾客
        c.execute('INSERT INTO system_config (key, value) VALUES (?, ?)', 
                 ('activity_status', 'active'))  # active, finished, disabled
        c.execute('INSERT INTO system_config (key, value) VALUES (?, ?)', 
                 ('qrcode_path', ''))  # 客服二维码路径
        c.execute('INSERT INTO system_config (key, value) VALUES (?, ?)', 
                 ('mock_winners', '0'))  # 模拟中奖次数（默认0表示不模拟）
        c.execute('INSERT INTO system_config (key, value) VALUES (?, ?)', 
                 ('today_mock_cache', ''))  # 当天模拟产品缓存（JSON格式）
    
    # 初始化预设产品池
    c.execute('SELECT COUNT(*) FROM product_pool')
    if c.fetchone()[0] == 0:
        default_products = ['iPhone 15', '小米手机', '华为耳机', '戴森吹风机',  '索尼相机', 'AirPods Pro', '机械键盘', '游戏手柄']
        for product in default_products:
            c.execute('INSERT INTO product_pool (product_name, is_active) VALUES (?, ?)',
                     (product, 1))
    
    conn.commit()
    conn.close()

# ==================== 工具函数 ====================
def get_db():
    """获取数据库连接（添加超时设置避免锁定）"""
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn

def generate_user_id(request):
    """生成用户唯一标识（基于IP和User-Agent）"""
    user_agent = request.headers.get('User-Agent', '')
    ip = request.remote_addr or ''
    raw = f"{ip}_{user_agent}"
    return hashlib.md5(raw.encode()).hexdigest()

def get_today_start():
    """获取今天0点的时间字符串"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return today.strftime('%Y-%m-%d %H:%M:%S')

def check_user_drawn_today(user_id):
    """检查用户今天是否已抽过奖"""
    conn = get_db()
    c = conn.cursor()
    today_start = get_today_start()
    
    c.execute('SELECT COUNT(*) FROM draw_records WHERE user_id = ? AND draw_time >= ?',
             (user_id, today_start))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def get_today_draw_count():
    """获取今天已产生的幸运顾客数量"""
    conn = get_db()
    c = conn.cursor()
    today_start = get_today_start()
    
    c.execute('SELECT COUNT(*) FROM draw_records WHERE locker_id IS NOT NULL AND draw_time >= ?',
             (today_start,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_system_config(key):
    """获取系统配置"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT value FROM system_config WHERE key = ?', (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_system_config(key, value):
    """设置系统配置"""
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO system_config (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

# ==================== API接口 ====================

@app.route('/')
def index():
    """首页"""
    resp = send_from_directory(app.static_folder, 'index.html')
    # 禁用缓存，避免一直看到旧页面
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    return resp

@app.route('/<path:path>')
def static_files(path):
    """静态文件"""
    resp = send_from_directory(app.static_folder, path)
    # 对前端文件尽量禁用缓存（尤其是html）
    if path.endswith('.html'):
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
    return resp

@app.route('/api/draw', methods=['POST'])
def draw():
    """抽奖接口（支持绿通凭证）"""
    data = request.json or {}
    green_code = data.get('green_code', '').strip()
    user_id = generate_user_id(request)
    
    conn = get_db()
    c = conn.cursor()
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    
    # 检查活动状态
    activity_status = get_system_config('activity_status')
    if activity_status == 'finished':
        conn.close()
        return jsonify({'success': False, 'message': '今天已抽完', 'reason': 'finished'})
    elif activity_status == 'disabled':
        conn.close()
        return jsonify({'success': False, 'message': '活动已结束', 'reason': 'disabled'})
    
    # 如果使用绿通凭证
    if green_code:
        c.execute('''SELECT * FROM greenlist 
                    WHERE identifier = ? 
                    AND remaining_draws > 0 
                    AND (expires_at IS NULL OR expires_at > ?)
                    ORDER BY expires_at DESC, id DESC''',
                 (green_code, now_str))
        green_record = c.fetchone()
        
        if not green_record:
            conn.close()
            return jsonify({'success': False, 'message': '无效的绿通凭证或已过期', 'reason': 'invalid_green_code'})
        
        # 绿通凭证有效，直接进入抽奖逻辑
        pass
    else:
        # 常规抽奖逻辑：检查用户今天是否已抽过
        c.execute('SELECT COUNT(*) FROM draw_records WHERE user_id = ? AND draw_time >= ?',
                 (user_id, get_today_start()))
        count = c.fetchone()[0]
        
        if count > 0:
            conn.close()
            return jsonify({'success': False, 
                          'message': '免费次数已满，请联系客服通过绿通抽奖', 
                          'reason': 'already_drawn'})
        
        # 冷却检查：查询上次抽奖时间
        c.execute('''SELECT MAX(draw_time) FROM draw_records 
                    WHERE locker_id IS NOT NULL''')
        last_draw = c.fetchone()[0]
        
        if last_draw:
            last_draw_dt = datetime.strptime(last_draw, '%Y-%m-%d %H:%M:%S')
            # 生成1-3分钟的随机冷却时间
            cooldown_minutes = random.randint(1, 3)
            cooldown_delta = timedelta(minutes=cooldown_minutes)
            
            if now < last_draw_dt + cooldown_delta:
                conn.close()
                return jsonify({'success': False, 
                              'message': '数据同步中，请稍后刷新重试', 
                              'reason': 'cooldown'})
    
    # 随机选择一个可用的格子
    c.execute('SELECT id, password, product_name FROM lockers WHERE is_available = 1')
    available_lockers = c.fetchall()
    
    if not available_lockers:
        conn.close()
        return jsonify({'success': False, 'message': '系统故障，请联系管理员', 'reason': 'no_locker'})
    
    # 随机选择
    selected = random.choice(available_lockers)
    locker_id = selected[0]
    password = selected[1]
    product_name = selected[2]
    
    # 生成订单号（格式：2-038，代表2号柜）
    order_code = f"{locker_id}-{password}"
    
    # 记录抽奖
    c.execute('INSERT INTO draw_records (user_id, locker_id, draw_time, order_code) VALUES (?, ?, ?, ?)',
             (user_id, locker_id, now_str, order_code))
    
    # 标记格子为不可用
    c.execute('UPDATE lockers SET is_available = 0 WHERE id = ?', (locker_id,))
    
    # 如果使用了绿通凭证，减少剩余次数
    if green_code:
        c.execute('UPDATE greenlist SET remaining_draws = remaining_draws - 1 WHERE identifier = ?',
                 (green_code,))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'lucky': True,
        'locker_id': locker_id,
        'password': password,
        'order_code': order_code,
        'product_name': product_name,
        'message': f'恭喜中奖！您的开锁密码：{order_code}'
    })

@app.route('/api/status', methods=['GET'])
def status():
    """获取系统状态（支持模拟数据）"""
    import json
    today_start = get_today_start()
    
    conn = get_db()
    c = conn.cursor()
    
    # 1. 获取今天真实中奖的人数和产品名（包含重复产品）
    c.execute('''SELECT l.product_name 
                 FROM draw_records r 
                 JOIN lockers l ON r.locker_id = l.id 
                 WHERE r.draw_time >= ? AND r.locker_id IS NOT NULL
                 ORDER BY r.draw_time ASC''', (today_start,))
    real_products = [row[0] for row in c.fetchall() if row[0]]
    real_count = len(real_products)
    
    # 2. 获取模拟中奖次数配置
    mock_winners = int(get_system_config('mock_winners') or '0')
    
    # 3. 如果配置了模拟次数且真实中奖<模拟数，需要补齐
    if mock_winners > 0 and real_count < mock_winners:
        # 获取今天的缓存
        cache_str = get_system_config('today_mock_cache') or '{}'
        try:
            cache_data = json.loads(cache_str)
            cache_date = cache_data.get('date', '')
            cached_products = cache_data.get('products', [])
        except:
            cache_data = {}
            cache_date = ''
            cached_products = []
        
        # 如果缓存不是今天的，生成新的模拟产品
        today_date = datetime.now().strftime('%Y-%m-%d')
        if cache_date != today_date:
            # 从产品池随机选择
            c.execute('SELECT product_name FROM product_pool WHERE is_active = 1')
            pool_products = [row[0] for row in c.fetchall()]
            if not pool_products:
                pool_products = ['精美礼品']
            
            # 生成模拟产品列表（补齐到mock_winners个）
            import random
            cached_products = []
            for i in range(mock_winners):
                cached_products.append(random.choice(pool_products))
            
            # 保存缓存
            cache_data = {'date': today_date, 'products': cached_products}
            set_system_config('today_mock_cache', json.dumps(cache_data, ensure_ascii=False))
        
        # 使用真实中奖产品 + 剩余的模拟产品
        display_count = mock_winners
        won_products_display = real_products + cached_products[real_count:]
        won_products_display = list(dict.fromkeys(won_products_display))  # 去重
    else:
        # 不需要模拟，直接显示真实数据
        display_count = max(real_count, 1)
        if real_count == 0:
            c.execute('SELECT product_name FROM product_pool WHERE is_active = 1 LIMIT 1')
            p = c.fetchone()
            won_products_display = [p[0] if p else "精美礼品"]
        else:
            won_products_display = list(dict.fromkeys(real_products))

    conn.close()
    
    return jsonify({
        'version': VERSION,
        'today_count': display_count,
        'won_products': won_products_display
    })

@app.route('/api/check_draw_status', methods=['POST'])
def check_draw_status():
    """检查用户是否可以抽奖"""
    user_id = generate_user_id(request)
    
    conn = get_db()
    c = conn.cursor()
    now = datetime.now()
    
    # 检查活动状态
    activity_status = get_system_config('activity_status')
    if activity_status == 'finished':
        conn.close()
        return jsonify({
            'can_draw': False,
            'message': '今天已抽完',
            'reason': 'finished'
        })
    elif activity_status == 'disabled':
        conn.close()
        return jsonify({
            'can_draw': False,
            'message': '活动已结束',
            'reason': 'disabled'
        })
    
    # 检查用户今天是否已抽过
    c.execute('SELECT COUNT(*) FROM draw_records WHERE user_id = ? AND draw_time >= ?',
             (user_id, get_today_start()))
    count = c.fetchone()[0]
    
    if count > 0:
        conn.close()
        return jsonify({
            'can_draw': False,
            'message': '免费次数已满，请联系客服通过绿通抽奖',
            'reason': 'already_drawn'
        })
    
    # 检查冷却时间
    c.execute('''SELECT MAX(draw_time) FROM draw_records 
                WHERE locker_id IS NOT NULL''')
    last_draw = c.fetchone()[0]
    
    if last_draw:
        last_draw_dt = datetime.strptime(last_draw, '%Y-%m-%d %H:%M:%S')
        cooldown_minutes = random.randint(1, 3)
        cooldown_delta = timedelta(minutes=cooldown_minutes)
        
        if now < last_draw_dt + cooldown_delta:
            conn.close()
            return jsonify({
                'can_draw': False,
                'message': '数据同步中，请稍后刷新重试',
                'reason': 'cooldown'
            })
    
    # 检查是否有可用格子
    c.execute('SELECT COUNT(*) FROM lockers WHERE is_available = 1')
    available_count = c.fetchone()[0]
    conn.close()
    
    if available_count == 0:
        return jsonify({
            'can_draw': False,
            'message': '系统故障，请联系管理员',
            'reason': 'no_locker'
        })
    
    return jsonify({
        'can_draw': True,
        'message': '可以抽奖',
        'reason': 'ok'
    })

@app.route('/api/verify_order', methods=['POST'])
def verify_order():
    """验证订单号（供管理员核销使用）"""
    data = request.json
    order_code = data.get('order_code', '')
    
    if not order_code:
        return jsonify({'success': False, 'message': '请输入订单号'})
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM draw_records WHERE order_code = ?', (order_code,))
    record = c.fetchone()
    conn.close()
    
    if record:
        return jsonify({
            'success': True,
            'valid': True,
            'locker_id': record['locker_id'],
            'draw_time': record['draw_time']
        })
    else:
        return jsonify({
            'success': True,
            'valid': False,
            'message': '无效的订单号'
        })

# ==================== 管理后台API ====================

@app.route('/api/admin/lockers', methods=['GET'])
def get_lockers():
    """获取所有格子信息"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM lockers ORDER BY id')
    lockers = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'lockers': lockers})

@app.route('/api/admin/locker/<int:locker_id>', methods=['PUT'])
def update_locker(locker_id):
    """更新格子信息"""
    data = request.json
    password = data.get('password')
    product_name = data.get('product_name')
    is_available = data.get('is_available', 1)
    
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE lockers SET password = ?, product_name = ?, is_available = ? WHERE id = ?',
             (password, product_name, is_available, locker_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': '更新成功'})

@app.route('/api/admin/config', methods=['GET', 'POST'])
def manage_config():
    """管理系统配置"""
    if request.method == 'GET':
        daily_limit = get_system_config('daily_limit')
        activity_status = get_system_config('activity_status')
        mock_winners = get_system_config('mock_winners') or '0'
        return jsonify({
            'success': True,
            'config': {
                'daily_limit': daily_limit,
                'activity_status': activity_status,
                'mock_winners': mock_winners
            }
        })
    
    elif request.method == 'POST':
        data = request.json
        conn = get_db()
        c = conn.cursor()
        
        if 'daily_limit' in data:
            c.execute('UPDATE system_config SET value = ? WHERE key = ?',
                     (str(data['daily_limit']), 'daily_limit'))
        
        if 'activity_status' in data:
            c.execute('UPDATE system_config SET value = ? WHERE key = ?',
                     (data['activity_status'], 'activity_status'))
        
        if 'mock_winners' in data:
            c.execute('INSERT OR REPLACE INTO system_config (key, value) VALUES (?, ?)',
                     ('mock_winners', str(data['mock_winners'])))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': '配置更新成功'})

@app.route('/api/admin/records', methods=['GET'])
def get_records():
    """获取抽奖记录（支持日期筛选）"""
    conn = get_db()
    c = conn.cursor()
    
    # 获取查询参数
    date_filter = request.args.get('date', '')  # 格式：YYYY-MM-DD
    show_all = request.args.get('all', 'false').lower() == 'true'
    
    if show_all:
        # 显示所有记录
        c.execute('''SELECT r.*, l.product_name 
                     FROM draw_records r 
                     LEFT JOIN lockers l ON r.locker_id = l.id 
                     ORDER BY r.draw_time DESC''')
    elif date_filter:
        # 按指定日期筛选
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d')
            date_start = filter_date.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
            date_end = filter_date.replace(hour=23, minute=59, second=59, microsecond=999999).strftime('%Y-%m-%d %H:%M:%S')
            c.execute('''SELECT r.*, l.product_name 
                         FROM draw_records r 
                         LEFT JOIN lockers l ON r.locker_id = l.id 
                         WHERE r.draw_time >= ? AND r.draw_time <= ?
                         ORDER BY r.draw_time DESC''', (date_start, date_end))
        except ValueError:
            # 日期格式错误，返回今天的记录
            today_start = get_today_start()
            c.execute('''SELECT r.*, l.product_name 
                         FROM draw_records r 
                         LEFT JOIN lockers l ON r.locker_id = l.id 
                         WHERE r.draw_time >= ? 
                         ORDER BY r.draw_time DESC''', (today_start,))
    else:
        # 默认显示今天的记录
        today_start = get_today_start()
        c.execute('''SELECT r.*, l.product_name 
                     FROM draw_records r 
                     LEFT JOIN lockers l ON r.locker_id = l.id 
                     WHERE r.draw_time >= ? 
                     ORDER BY r.draw_time DESC''', (today_start,))
    
    records = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'records': records, 'filter': date_filter or ('全部' if show_all else '今日')})

@app.route('/api/admin/reset_lockers', methods=['POST'])
def reset_lockers():
    """重置所有格子为可用状态（放置新货品时使用）"""
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE lockers SET is_available = 1')
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': '格子已重置'})

# ==================== 绿通凭证管理API ====================

@app.route('/api/admin/greenlist', methods=['GET'])
def get_greenlist():
    """获取所有绿通凭证"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM greenlist ORDER BY created_at DESC')
    records = [dict(row) for row in c.fetchall()]
    conn.close()
    now = datetime.now()
    for record in records:
        status = '可用'
        if record.get('expires_at'):
            try:
                expires_at = datetime.strptime(record['expires_at'], '%Y-%m-%d %H:%M:%S')
                if now > expires_at:
                    status = '已过期'
            except ValueError:
                status = '已过期'
        if record.get('remaining_draws', 0) <= 0 and status != '已过期':
            status = '已用完'
        record['status'] = status
    return jsonify({'success': True, 'records': records})

@app.route('/api/admin/greenlist', methods=['POST'])
def add_greenlist():
    """添加绿通凭证"""
    try:
        print("=" * 50)
        print("收到添加绿通凭证请求")
        data = request.json
        print(f"请求数据: {data}")
        
        identifier = data.get('identifier', '').strip()
        type_name = data.get('type', 'phone')  # phone, order, custom
        remaining_draws = int(data.get('remaining_draws', 1))
        expires_hours = int(data.get('expires_hours', 24))  # 默认24小时过期
        
        print(f"解析后: identifier={identifier}, type={type_name}, draws={remaining_draws}, hours={expires_hours}")
        
        if not identifier:
            print("错误: 凭证标识为空")
            return jsonify({'success': False, 'message': '凭证标识不能为空'})
        
        conn = get_db()
        c = conn.cursor()
        now = datetime.now()
        expires_at = (now + timedelta(hours=expires_hours)).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"准备插入数据库: {identifier}, {type_name}, {remaining_draws}, {now.strftime('%Y-%m-%d %H:%M:%S')}, {expires_at}")
        
        c.execute('''INSERT INTO greenlist (identifier, type, remaining_draws, created_at, expires_at) 
                    VALUES (?, ?, ?, ?, ?)''',
                 (identifier, type_name, remaining_draws, now.strftime('%Y-%m-%d %H:%M:%S'), expires_at))
        conn.commit()
        conn.close()
        
        print("✅ 添加成功")
        print("=" * 50)
        return jsonify({'success': True, 'message': '绿通凭证添加成功'})
    except Exception as e:
        print(f"❌ 添加绿通凭证失败: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 50)
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'})

@app.route('/api/admin/greenlist/<int:record_id>', methods=['DELETE'])
def delete_greenlist(record_id):
    """删除绿通凭证"""
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM greenlist WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': '删除成功'})

@app.route('/api/verify_green_code', methods=['POST'])
def verify_green_code():
    """验证绿通凭证 (遍历查找有效项)"""
    data = request.json
    green_code = data.get('green_code', '').strip()
    
    if not green_code:
        return jsonify({'success': False, 'message': '请输入绿通凭证'})
    
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 修改逻辑：不加顺序，直接找第一个符合“有次数”且“没过期”的
    c.execute('''SELECT * FROM greenlist 
                WHERE identifier = ? 
                AND remaining_draws > 0 
                AND (expires_at IS NULL OR expires_at > ?)
                ORDER BY expires_at DESC, id DESC
                LIMIT 1''',
             (green_code, now))
    record = c.fetchone()
    conn.close()
    
    if record:
        return jsonify({
            'success': True,
            'valid': True,
            'remaining_draws': record['remaining_draws'],
            'message': '绿通凭证有效'
        })
    else:
        return jsonify({
            'success': True,
            'valid': False,
            'message': '无效的绿通凭证或已过期'
        })

# ==================== 产品池管理API ====================

@app.route('/api/admin/product_pool', methods=['GET'])
def get_product_pool():
    """获取产品池"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM product_pool ORDER BY id')
    products = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'products': products})

@app.route('/api/admin/product_pool', methods=['POST'])
def add_product():
    """添加产品到产品池"""
    data = request.json
    product_name = data.get('product_name', '').strip()
    
    if not product_name:
        return jsonify({'success': False, 'message': '产品名称不能为空'})
    
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO product_pool (product_name, is_active) VALUES (?, ?)',
             (product_name, 1))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': '产品添加成功'})

@app.route('/api/admin/product_pool/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """更新产品状态"""
    data = request.json
    product_name = data.get('product_name')
    is_active = data.get('is_active')
    
    conn = get_db()
    c = conn.cursor()
    
    # 如果只更新状态
    if is_active is not None and not product_name:
        c.execute('UPDATE product_pool SET is_active = ? WHERE id = ?',
                 (is_active, product_id))
    else:
        c.execute('UPDATE product_pool SET product_name = ?, is_active = ? WHERE id = ?',
                 (product_name, is_active or 1, product_id))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': '更新成功'})

@app.route('/api/admin/product_pool/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """删除产品"""
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM product_pool WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': '删除成功'})

# ==================== 客服二维码管理API ====================

@app.route('/api/qrcode', methods=['GET'])
def get_qrcode():
    """获取客服二维码"""
    qrcode_path = get_system_config('qrcode_path')
    
    # 调试信息
    print(f"=== 二维码API调试 ===")
    print(f"UPLOAD_FOLDER: {UPLOAD_FOLDER}")
    print(f"数据库配置路径: {qrcode_path}")
    
    # 尝试返回自定义上传的二维码
    if qrcode_path and os.path.exists(qrcode_path):
        print(f"返回自定义二维码: {qrcode_path}")
        try:
            return send_file(qrcode_path, mimetype='image/png')
        except Exception as e:
            print(f"加载自定义二维码失败: {e}")
    
    # 返回默认二维码
    default_qr = os.path.join(UPLOAD_FOLDER, 'default_qrcode.png')
    print(f"检查默认二维码: {default_qr}")
    print(f"文件存在: {os.path.exists(default_qr)}")
    
    if os.path.exists(default_qr):
        print(f"返回默认二维码")
        try:
            return send_file(default_qr, mimetype='image/png')
        except Exception as e:
            print(f"加载默认二维码失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 如果都没有，返回一个占位图片（SVG）
    print("返回占位SVG")
    svg_placeholder = '''<svg xmlns="http://www.w3.org/2000/svg" width="180" height="180">
        <rect width="180" height="180" fill="#f0f0f0"/>
        <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#999" font-size="14">暂无客服二维码</text>
    </svg>'''
    return svg_placeholder, 200, {'Content-Type': 'image/svg+xml'}

@app.route('/api/admin/upload_qrcode', methods=['POST'])
def upload_qrcode():
    """上传客服二维码"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有文件'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    if file and allowed_file(file.filename):
        filename = 'service_qrcode_' + datetime.now().strftime('%Y%m%d%H%M%S') + '.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 更新数据库配置
        conn = get_db()
        c = conn.cursor()
        c.execute('UPDATE system_config SET value = ? WHERE key = ?', (filepath, 'qrcode_path'))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '上传成功', 'path': filepath})
    else:
        return jsonify({'success': False, 'message': '不支持的文件格式'})

@app.route('/api/admin/qrcode_status', methods=['GET'])
def get_qrcode_status():
    """获取当前二维码状态"""
    qrcode_path = get_system_config('qrcode_path')
    has_custom = qrcode_path and os.path.exists(qrcode_path)
    has_default = os.path.exists(os.path.join(UPLOAD_FOLDER, 'default_qrcode.png'))
    
    return jsonify({
        'success': True,
        'has_custom': has_custom,
        'has_default': has_default,
        'current_path': qrcode_path if has_custom else 'default'
    })

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    print("=" * 50)
    print(f"LuckyLocker 抽奖系统启动 (v{VERSION})")
    print("前端访问: http://localhost:5000")
    print("管理后台: http://localhost:5000/admin.html")
    print("=" * 50)
    
    # 启动Flask服务
    app.run(host='0.0.0.0', port=5000, debug=True)
