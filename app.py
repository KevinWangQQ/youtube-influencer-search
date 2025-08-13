from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import uuid
import hashlib
import threading
import os
import pandas as pd
from datetime import datetime
import time

from scraper_service import YouTubeInfluencerScraperService
from models import DatabaseManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)

# 全局对象
db = DatabaseManager()
running_tasks = {}  # 存储正在运行的任务

def hash_api_key(api_key: str) -> str:
    """对API密钥进行哈希处理"""
    return hashlib.sha256(api_key.encode()).hexdigest()[:16]

def progress_callback(task_id: str, progress_data: dict):
    """进度回调函数"""
    db.update_task_status(
        task_id=task_id,
        status='running',
        progress=progress_data.get('percentage', 0),
        progress_message=progress_data.get('message', ''),
        total_keywords=progress_data.get('total_keywords', 0),
        current_keyword=progress_data.get('current_keyword', 0),
        found_influencers=progress_data.get('found_influencers', 0)
    )

def run_scraper_task(task_id: str, product_name: str, api_key: str, 
                    min_subscribers: int, min_view_count: int):
    """后台运行爬虫任务"""
    try:
        # 创建进度回调
        def callback(data):
            progress_callback(task_id, data)
        
        # 初始化爬虫服务
        scraper = YouTubeInfluencerScraperService(
            api_key=api_key,
            min_subscribers=min_subscribers,
            min_view_count=min_view_count,
            progress_callback=callback
        )
        
        # 更新任务状态为运行中
        db.update_task_status(task_id, 'running', 0, '开始搜索...')
        
        # 执行搜索
        result = scraper.scrape_product(product_name)
        
        # 保存结果
        if scraper.influencers:
            db.save_influencer_results(task_id, scraper.influencers)
        
        # 更新任务状态为完成
        db.update_task_status(
            task_id=task_id,
            status='completed',
            progress=100,
            progress_message=f'搜索完成，找到 {len(scraper.influencers)} 个influencer',
            found_influencers=len(scraper.influencers)
        )
        
        # 从运行任务字典中移除
        if task_id in running_tasks:
            del running_tasks[task_id]
            
    except Exception as e:
        # 更新任务状态为失败
        db.update_task_status(
            task_id=task_id,
            status='failed',
            error_message=str(e)
        )
        
        # 从运行任务字典中移除
        if task_id in running_tasks:
            del running_tasks[task_id]

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def start_search():
    """启动搜索任务"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['product_name', 'api_key']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必需参数: {field}'}), 400
        
        product_name = data['product_name'].strip()
        api_key = data['api_key'].strip()
        min_subscribers = int(data.get('min_subscribers', 10000))
        min_view_count = int(data.get('min_view_count', 5000))
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        api_key_hash = hash_api_key(api_key)
        
        # 创建数据库记录
        success = db.create_search_task(
            task_id=task_id,
            product_name=product_name,
            api_key_hash=api_key_hash,
            min_subscribers=min_subscribers,
            min_view_count=min_view_count
        )
        
        if not success:
            return jsonify({'error': '创建任务失败'}), 500
        
        # 启动后台任务
        thread = threading.Thread(
            target=run_scraper_task,
            args=(task_id, product_name, api_key, min_subscribers, min_view_count)
        )
        thread.daemon = True
        thread.start()
        
        # 记录运行中的任务
        running_tasks[task_id] = {
            'thread': thread,
            'product_name': product_name,
            'started_at': datetime.now()
        }
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': f'搜索任务已启动: {product_name}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<task_id>')
def get_task_status(task_id):
    """获取任务状态"""
    try:
        status = db.get_task_status(task_id)
        if not status:
            return jsonify({'error': '任务不存在'}), 404
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/results/<task_id>')
def get_task_results(task_id):
    """获取任务结果"""
    try:
        # 检查任务是否存在
        task_status = db.get_task_status(task_id)
        if not task_status:
            return jsonify({'error': '任务不存在'}), 404
        
        # 获取结果
        results = db.get_task_results(task_id)
        summary = db.get_task_summary(task_id)
        
        return jsonify({
            'success': True,
            'task_status': task_status,
            'summary': summary,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_search_history():
    """获取搜索历史"""
    try:
        limit = request.args.get('limit', 20, type=int)
        history = db.get_search_history(limit)
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<task_id>')
def download_results(task_id):
    """下载CSV结果"""
    try:
        # 检查任务是否存在
        task_status = db.get_task_status(task_id)
        if not task_status:
            return jsonify({'error': '任务不存在'}), 404
        
        # 获取结果
        results = db.get_task_results(task_id)
        if not results:
            return jsonify({'error': '没有结果数据'}), 404
        
        # 创建DataFrame并保存CSV
        df = pd.DataFrame(results)
        filename = f"influencers_{task_status['product_name'].replace(' ', '_')}_{task_id[:8]}.csv"
        filepath = os.path.join('temp', filename)
        
        # 确保temp目录存在
        os.makedirs('temp', exist_ok=True)
        
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-key', methods=['POST'])
def validate_api_key():
    """验证YouTube API密钥"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({'valid': False, 'error': 'API密钥不能为空'})
        
        # 尝试创建YouTube服务来验证密钥
        try:
            scraper = YouTubeInfluencerScraperService(api_key=api_key)
            # 执行一个简单的搜索来验证密钥
            videos = scraper.search_videos('test')
            return jsonify({'valid': True})
        except Exception as e:
            return jsonify({'valid': False, 'error': f'API密钥无效: {str(e)}'})
            
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

@app.route('/api/running-tasks')
def get_running_tasks():
    """获取当前运行中的任务"""
    try:
        tasks = []
        for task_id, task_info in running_tasks.items():
            status = db.get_task_status(task_id)
            if status:
                tasks.append({
                    'task_id': task_id,
                    'product_name': task_info['product_name'],
                    'started_at': task_info['started_at'].isoformat(),
                    'status': status['status'],
                    'progress': status['progress']
                })
        
        return jsonify({
            'success': True,
            'running_tasks': tasks
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs('temp', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=8080)