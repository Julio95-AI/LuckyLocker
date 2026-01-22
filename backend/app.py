"""
LuckyLocker 抽奖系统后端
简单的Flask应用，提供抽奖和管理API
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import random
import hashlib
from datetime import datetime, timedelta
import os

app = Flask(__name__, static_folder='../frontend')
CORS(app)  # 允许跨域访问

DB_PATH = 'luckylocker.db'

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
    
    conn.commit()
    conn.close()

# ==================== 工具函数 ====================
def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
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

# ==================== API接口 ====================

@app.route('/')
def index():
    """首页"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """静态文件"""
    return send_from_directory(app.static_folder, path)

@app.route('/api/draw', methods=['POST'])
def draw():
    """抽奖接口"""
    user_id = generate_user_id(request)
    
    # 检查活动状态
    activity_status = get_system_config('activity_status')
    if activity_status == 'finished':
        return jsonify({'success': False, 'message': '今天已抽完', 'reason': 'finished'})
    elif activity_status == 'disabled':
        return jsonify({'success': False, 'message': '活动已结束', 'reason': 'disabled'})
    
    # 检查用户今天是否已抽过
    if check_user_drawn_today(user_id):
        return jsonify({'success': False, 'message': '每个手机号限免费抽奖1次，乱吃抽奖即可止', 'reason': 'already_drawn'})
    
    # 检查今天是否还有名额
    daily_limit = int(get_system_config('daily_limit') or 2)
    today_count = get_today_draw_count()
    
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if today_count >= daily_limit:
        # 今天名额已满，记录但不分配格子
        order_code = None
        locker_id = None
        c.execute('INSERT INTO draw_records (user_id, locker_id, draw_time, order_code) VALUES (?, ?, ?, ?)',
                 (user_id, locker_id, now, order_code))
        conn.commit()
        conn.close()
        return jsonify({
            'success': True, 
            'lucky': False,
            'message': '很遗憾，今日名额已满，明天再来吧！'
        })
    
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
             (user_id, locker_id, now, order_code))
    
    # 标记格子为不可用（可选：如果想让格子只能被抽一次）
    # c.execute('UPDATE lockers SET is_available = 0 WHERE id = ?', (locker_id,))
    
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
    """获取系统状态"""
    daily_limit = int(get_system_config('daily_limit') or 2)
    today_count = get_today_draw_count()
    activity_status = get_system_config('activity_status')
    
    return jsonify({
        'daily_limit': daily_limit,
        'today_count': today_count,
        'remaining': max(0, daily_limit - today_count),
        'activity_status': activity_status
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
        return jsonify({
            'success': True,
            'config': {
                'daily_limit': daily_limit,
                'activity_status': activity_status
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
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': '配置更新成功'})

@app.route('/api/admin/records', methods=['GET'])
def get_records():
    """获取抽奖记录"""
    conn = get_db()
    c = conn.cursor()
    
    # 获取今天的记录
    today_start = get_today_start()
    c.execute('''SELECT r.*, l.product_name 
                 FROM draw_records r 
                 LEFT JOIN lockers l ON r.locker_id = l.id 
                 WHERE r.draw_time >= ? 
                 ORDER BY r.draw_time DESC''', (today_start,))
    records = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'records': records})

@app.route('/api/admin/reset_lockers', methods=['POST'])
def reset_lockers():
    """重置所有格子为可用状态（放置新货品时使用）"""
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE lockers SET is_available = 1')
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': '格子已重置'})

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    print("=" * 50)
    print("LuckyLocker 抽奖系统启动")
    print("前端访问: http://localhost:5000")
    print("管理后台: http://localhost:5000/admin.html")
    print("=" * 50)
    
    # 启动Flask服务
    app.run(host='0.0.0.0', port=5000, debug=True)
