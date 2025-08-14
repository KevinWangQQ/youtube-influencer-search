# Vercel入口文件
from api.index import app

# 这是Vercel的入口点
def handler(event, context):
    return app(event, context)

# 如果直接运行，启动Flask开发服务器
if __name__ == '__main__':
    app.run(debug=True)