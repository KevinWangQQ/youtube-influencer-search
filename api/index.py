from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from scraper_service import YouTubeInfluencerScraperService
except ImportError:
    # 如果导入失败，创建一个简单的模拟版本
    class YouTubeInfluencerScraperService:
        def __init__(self, **kwargs):
            self.api_key = kwargs.get('api_key')
        
        def generate_search_keywords(self, product_name):
            return [
                f"{product_name} review",
                f"{product_name} unboxing",
                f"{product_name} test"
            ]

app = Flask(__name__, 
           template_folder=os.path.join(parent_dir, 'templates'),
           static_folder=os.path.join(parent_dir, 'static'))
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)

@app.route('/')
def index():
    """主页"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>YouTube Influencer Search</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="alert alert-warning">
                    <h4>🚧 系统正在部署中</h4>
                    <p>我们正在为Vercel优化系统架构。请稍后再试。</p>
                    <p>错误信息: {str(e)}</p>
                </div>
                <div class="card">
                    <div class="card-body">
                        <h5>YouTube Influencer搜索系统</h5>
                        <p>系统功能:</p>
                        <ul>
                            <li>智能关键词生成</li>
                            <li>YouTube API集成</li>
                            <li>美国地区筛选</li>
                            <li>实时搜索结果</li>
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/api/test')
def test_api():
    """测试API端点"""
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'timestamp': datetime.now().isoformat(),
        'python_path': sys.path[:3]
    })

@app.route('/api/validate-key', methods=['POST'])
def validate_api_key():
    """验证YouTube API密钥"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({'valid': False, 'error': 'API密钥不能为空'})
        
        # 简单的格式验证
        if len(api_key) < 30:
            return jsonify({'valid': False, 'error': 'API密钥格式不正确'})
            
        return jsonify({'valid': True, 'message': 'API密钥格式正确'})
            
    except Exception as e:
        return jsonify({'valid': False, 'error': f'验证失败: {str(e)}'})

@app.route('/api/generate-keywords', methods=['POST'])
def generate_keywords():
    """生成搜索关键词"""
    try:
        data = request.get_json()
        product_name = data.get('product_name', '').strip()
        
        if not product_name:
            return jsonify({'error': '请输入产品名称'}), 400
        
        # 创建服务实例并生成关键词
        service = YouTubeInfluencerScraperService(api_key='dummy')
        keywords = service.generate_search_keywords(product_name)
        
        return jsonify({
            'success': True,
            'product_name': product_name,
            'keywords': keywords,
            'total_keywords': len(keywords)
        })
        
    except Exception as e:
        return jsonify({'error': f'生成关键词失败: {str(e)}'}), 500

@app.route('/api/search-demo', methods=['POST'])
def search_demo():
    """演示搜索功能（不实际调用YouTube API）"""
    try:
        data = request.get_json()
        product_name = data.get('product_name', '').strip()
        
        if not product_name:
            return jsonify({'error': '请输入产品名称'}), 400
        
        # 生成演示数据
        demo_results = [
            {
                'channel_name': 'Tech Reviews Pro',
                'channel_id': 'demo_channel_1',
                'subscriber_count': 156000,
                'product_reviewed': product_name,
                'video_title': f'{product_name} Complete Review - Worth the Money?',
                'video_view_count': 45600,
                'video_published_at': '2024-11-15T10:30:00Z',
                'channel_country': 'US'
            },
            {
                'channel_name': 'Unbox Everything',
                'channel_id': 'demo_channel_2', 
                'subscriber_count': 89400,
                'product_reviewed': product_name,
                'video_title': f'Unboxing the {product_name} - First Impressions',
                'video_view_count': 23100,
                'video_published_at': '2024-11-10T14:20:00Z',
                'channel_country': 'US'
            }
        ]
        
        return jsonify({
            'success': True,
            'demo_mode': True,
            'results': demo_results,
            'summary': {
                'total_influencers': len(demo_results),
                'avg_subscriber_count': sum(r['subscriber_count'] for r in demo_results) // len(demo_results),
                'max_subscriber_count': max(r['subscriber_count'] for r in demo_results)
            },
            'message': '这是演示数据。完整功能需要有效的YouTube API密钥。'
        })
        
    except Exception as e:
        return jsonify({'error': f'演示搜索失败: {str(e)}'}), 500

@app.route('/api/info')
def system_info():
    """系统信息"""
    return jsonify({
        'system': 'YouTube Influencer Search System',
        'version': '2.0-vercel',
        'environment': 'Vercel Serverless',
        'features': [
            '关键词生成',
            'API密钥验证', 
            '演示模式',
            '响应式界面'
        ],
        'limitations': [
            '无服务器环境限制',
            '需要有效的YouTube API密钥进行完整搜索',
            '无数据持久化存储'
        ]
    })

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'API端点不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

# Vercel处理函数
def handler(event, context):
    try:
        return app(event, context)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Function handler error: {str(e)}',
                'event': str(event)[:200]
            })
        }

# 开发模式
if __name__ == '__main__':
    app.run(debug=True, port=8080)