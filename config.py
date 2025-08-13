import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # YouTube API设置
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    
    # 搜索参数 - 多品牌WiFi路由器
    SEARCH_KEYWORDS = [
        # eero 7系列
        'eero 7 review',
        'eero pro 7 review', 
        'eero max 7 review',
        'eero 7 unboxing',
        'eero 7 test',
        
        # Netgear Orbi 370
        'netgear orbi 370 review',
        'orbi 370 review',
        'netgear orbi 370 unboxing',
        'orbi 370 test',
        
        # Asus ZenWifi BE5000
        'asus zenwifi be5000 review',
        'zenwifi be5000 review',
        'asus zenwifi be5000 unboxing',
        'zenwifi be5000 test',
        
        # Asus ZenWifi BD5
        'asus zenwifi bd5 review',
        'zenwifi bd5 review', 
        'asus zenwifi bd5 unboxing',
        'zenwifi bd5 test',
        
        # Asus RT-BE92U
        'asus rt-be92u review',
        'rt-be92u review',
        'asus rt be92u review',
        'rt be92u unboxing',
        
        # Netgear RS300
        'netgear rs300 review',
        'rs300 router review',
        'netgear rs300 unboxing',
        'rs300 test',
        
        # Netgear BE9300
        'netgear be9300 review',
        'be9300 router review',
        'netgear be9300 unboxing',
        'be9300 test'
    ]
    
    # Influencer筛选条件
    MIN_SUBSCRIBERS = 10000  # 最小订阅数
    MIN_VIEW_COUNT = 5000    # 最小观看数
    
    # 搜索限制
    MAX_RESULTS_PER_QUERY = 50  # 每个查询最大结果数
    PUBLISHED_AFTER = '2023-01-01T00:00:00Z'  # 搜索发布日期范围
    REGION_CODE = 'US'  # 限制美国地区
    
    # 输出设置
    OUTPUT_FILE = 'wifi_router_influencers_us.csv'