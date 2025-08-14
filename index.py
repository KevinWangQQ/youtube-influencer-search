# Vercel入口文件
import os
import sys

# 确保当前目录在Python路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from api.index import app, handler
    
    # 直接导出app和handler
    app = app
    
except Exception as e:
    # 如果导入失败，创建一个最小的Flask应用
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return jsonify({
            'error': 'Import failed',
            'message': str(e),
            'status': 'System is being optimized for Vercel deployment'
        })
    
    def handler(event, context):
        return app(event, context)

# 如果直接运行，启动Flask开发服务器
if __name__ == '__main__':
    app.run(debug=True, port=8080)