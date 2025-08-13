import json
import pandas as pd
from googleapiclient.discovery import build
from config import Config
import time
from typing import List, Dict, Set

class YouTubeInfluencerScraper:
    def __init__(self):
        if not Config.YOUTUBE_API_KEY:
            raise ValueError("请设置YOUTUBE_API_KEY环境变量")
        
        self.youtube = build(
            Config.YOUTUBE_API_SERVICE_NAME, 
            Config.YOUTUBE_API_VERSION,
            developerKey=Config.YOUTUBE_API_KEY
        )
        self.influencers = []
        self.processed_channels = set()  # 去重用
    
    def search_videos(self, query: str) -> List[Dict]:
        """搜索视频"""
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=Config.MAX_RESULTS_PER_QUERY,
                type='video',
                publishedAfter=Config.PUBLISHED_AFTER,
                regionCode=Config.REGION_CODE,
                order='relevance'
            ).execute()
            
            return search_response.get('items', [])
        except Exception as e:
            print(f"搜索'{query}'时出错: {e}")
            return []
    
    def get_video_statistics(self, video_id: str) -> Dict:
        """获取视频统计信息"""
        try:
            video_response = self.youtube.videos().list(
                part='statistics',
                id=video_id
            ).execute()
            
            items = video_response.get('items', [])
            if items:
                return items[0]['statistics']
            return {}
        except Exception as e:
            print(f"获取视频{video_id}统计信息时出错: {e}")
            return {}
    
    def get_channel_info(self, channel_id: str) -> Dict:
        """获取频道信息"""
        try:
            channel_response = self.youtube.channels().list(
                part='snippet,statistics,localizations',
                id=channel_id
            ).execute()
            
            items = channel_response.get('items', [])
            if items:
                return items[0]
            return {}
        except Exception as e:
            print(f"获取频道{channel_id}信息时出错: {e}")
            return {}
    
    def is_influencer(self, subscriber_count: int, view_count: int) -> bool:
        """判断是否为influencer"""
        return (subscriber_count >= Config.MIN_SUBSCRIBERS or 
                view_count >= Config.MIN_VIEW_COUNT)
    
    def is_us_channel(self, channel_info: Dict) -> bool:
        """检查频道是否为美国地区"""
        snippet = channel_info.get('snippet', {})
        country = snippet.get('country', '')
        
        # 检查频道国家设置
        if country == 'US':
            return True
            
        # 检查频道描述和标题中的美国相关关键词
        description = snippet.get('description', '').lower()
        title = snippet.get('title', '').lower()
        
        us_indicators = ['usa', 'united states', 'america', 'us based', 'california', 
                        'new york', 'texas', 'florida', 'washington', 'oregon']
        
        text_content = f"{description} {title}"
        
        # 如果包含美国相关关键词，认为是美国频道
        for indicator in us_indicators:
            if indicator in text_content:
                return True
                
        # 如果没有国家信息且没有明显的非美国指标，默认认为可能是美国
        non_us_indicators = ['uk', 'canada', 'australia', 'germany', 'france', 
                           'spain', 'italy', 'japan', 'korea', 'china', 'india']
        
        for indicator in non_us_indicators:
            if indicator in text_content:
                return False
                
        # 没有明确地区信息时，保守处理，认为可能是美国
        return country == '' or country == 'US'
    
    def extract_product_from_keyword(self, keyword: str) -> str:
        """从搜索关键词提取产品型号"""
        keyword_lower = keyword.lower()
        
        if 'eero 7' in keyword_lower or 'eero pro 7' in keyword_lower or 'eero max 7' in keyword_lower:
            if 'max 7' in keyword_lower:
                return 'eero Max 7'
            elif 'pro 7' in keyword_lower:
                return 'eero Pro 7'
            else:
                return 'eero 7'
        elif 'orbi 370' in keyword_lower:
            return 'Netgear Orbi 370'
        elif 'zenwifi be5000' in keyword_lower:
            return 'Asus ZenWifi BE5000'
        elif 'zenwifi bd5' in keyword_lower:
            return 'Asus ZenWifi BD5'
        elif 'rt-be92u' in keyword_lower or 'rt be92u' in keyword_lower:
            return 'Asus RT-BE92U'
        elif 'rs300' in keyword_lower:
            return 'Netgear RS300'
        elif 'be9300' in keyword_lower:
            return 'Netgear BE9300'
        else:
            return 'Unknown'
    
    def process_video(self, video_item: Dict, search_keyword: str = '') -> None:
        """处理单个视频，检查是否为influencer"""
        video_id = video_item['id']['videoId']
        channel_id = video_item['snippet']['channelId']
        
        # 避免重复处理同一频道+产品组合
        channel_product_key = f"{channel_id}_{self.extract_product_from_keyword(search_keyword)}"
        if channel_product_key in self.processed_channels:
            return
        
        # 获取视频统计信息
        video_stats = self.get_video_statistics(video_id)
        if not video_stats:
            return
            
        view_count = int(video_stats.get('viewCount', 0))
        
        # 获取频道信息
        channel_info = self.get_channel_info(channel_id)
        if not channel_info:
            return
        
        # 检查是否为美国地区频道
        if not self.is_us_channel(channel_info):
            return
            
        channel_stats = channel_info.get('statistics', {})
        subscriber_count = int(channel_stats.get('subscriberCount', 0))
        
        # 检查是否符合influencer条件
        if self.is_influencer(subscriber_count, view_count):
            self.processed_channels.add(channel_product_key)
            
            product_name = self.extract_product_from_keyword(search_keyword)
            
            influencer_info = {
                'channel_name': channel_info['snippet']['title'],
                'channel_id': channel_id,
                'channel_url': f"https://www.youtube.com/channel/{channel_id}",
                'channel_country': channel_info['snippet'].get('country', 'US'),
                'subscriber_count': subscriber_count,
                'product_reviewed': product_name,
                'search_keyword': search_keyword,
                'video_title': video_item['snippet']['title'],
                'video_id': video_id,
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'video_view_count': view_count,
                'video_published_at': video_item['snippet']['publishedAt'],
                'video_description': video_item['snippet']['description'][:200] + '...',
                'total_channel_views': int(channel_stats.get('viewCount', 0)),
                'total_channel_videos': int(channel_stats.get('videoCount', 0))
            }
            
            self.influencers.append(influencer_info)
            print(f"发现Influencer: {influencer_info['channel_name']} "
                  f"(订阅数: {subscriber_count:,}, 视频观看: {view_count:,})")
    
    def scrape_all_keywords(self) -> None:
        """搜索所有关键词"""
        for keyword in Config.SEARCH_KEYWORDS:
            print(f"正在搜索关键词: '{keyword}'")
            videos = self.search_videos(keyword)
            
            for video in videos:
                self.process_video(video, keyword)
                time.sleep(0.1)  # 避免请求过快
            
            time.sleep(1)  # 关键词间延迟
            print(f"'{keyword}' 搜索完成，当前找到 {len(self.influencers)} 个influencer")
    
    def export_to_csv(self) -> None:
        """导出结果到CSV"""
        if not self.influencers:
            print("没有找到符合条件的influencer")
            return
        
        df = pd.DataFrame(self.influencers)
        # 按订阅数排序
        df = df.sort_values('subscriber_count', ascending=False)
        df.to_csv(Config.OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print(f"结果已导出到 {Config.OUTPUT_FILE}")
        print(f"总共找到 {len(self.influencers)} 个符合条件的influencer")
    
    def run(self) -> None:
        """运行完整的爬取流程"""
        print("开始搜索WiFi路由器产品的美国地区influencer...")
        print(f"筛选条件: 订阅数 >= {Config.MIN_SUBSCRIBERS:,} 或 视频观看量 >= {Config.MIN_VIEW_COUNT:,}")
        print(f"地区限制: 仅美国地区频道 (region={Config.REGION_CODE})")
        
        self.scrape_all_keywords()
        self.export_to_csv()
        
        # 打印摘要
        if self.influencers:
            print("\n=== 结果摘要 ===")
            df = pd.DataFrame(self.influencers)
            print(f"平均订阅数: {df['subscriber_count'].mean():,.0f}")
            print(f"最高订阅数: {df['subscriber_count'].max():,}")
            print(f"平均视频观看数: {df['video_view_count'].mean():,.0f}")
            print(f"最高视频观看数: {df['video_view_count'].max():,}")

if __name__ == "__main__":
    scraper = YouTubeInfluencerScraper()
    scraper.run()