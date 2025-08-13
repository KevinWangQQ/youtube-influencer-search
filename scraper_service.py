import json
import pandas as pd
from googleapiclient.discovery import build
import time
from typing import List, Dict, Set, Optional, Callable
import re

class YouTubeInfluencerScraperService:
    def __init__(self, 
                 api_key: str,
                 min_subscribers: int = 10000,
                 min_view_count: int = 5000,
                 max_results_per_query: int = 50,
                 region_code: str = 'US',
                 published_after: str = '2023-01-01T00:00:00Z',
                 progress_callback: Optional[Callable] = None):
        """
        YouTube Influencer爬虫服务
        
        Args:
            api_key: YouTube Data API密钥
            min_subscribers: 最小订阅数筛选条件
            min_view_count: 最小视频观看数筛选条件
            max_results_per_query: 每个查询的最大结果数
            region_code: 地区限制代码
            published_after: 搜索发布日期范围
            progress_callback: 进度回调函数
        """
        if not api_key:
            raise ValueError("API密钥不能为空")
        
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.min_subscribers = min_subscribers
        self.min_view_count = min_view_count
        self.max_results_per_query = max_results_per_query
        self.region_code = region_code
        self.published_after = published_after
        self.progress_callback = progress_callback
        
        self.influencers = []
        self.processed_channels = set()
        self.total_keywords = 0
        self.current_keyword_index = 0
    
    def generate_search_keywords(self, product_name: str) -> List[str]:
        """
        根据产品名称生成搜索关键词
        
        Args:
            product_name: 产品名称，如"eero 7", "Netgear Orbi 370"
            
        Returns:
            生成的搜索关键词列表
        """
        # 清理产品名称
        product_clean = product_name.strip().lower()
        
        # 基础关键词模板
        base_templates = [
            "{product} review",
            "{product} unboxing", 
            "{product} test",
            "{product} wifi router review",
            "{product} mesh router review"
        ]
        
        keywords = []
        
        # 生成完整产品名称的关键词
        for template in base_templates:
            keywords.append(template.format(product=product_name))
        
        # 如果是多词产品名，生成简化版关键词
        words = product_clean.split()
        if len(words) > 1:
            # 尝试不同的简化组合
            if len(words) >= 2:
                short_name = f"{words[-2]} {words[-1]}"  # 取最后两个词
                for template in base_templates[:3]:  # 只用前3个模板避免过多
                    keywords.append(template.format(product=short_name))
            
            # 如果包含品牌名，生成品牌+型号的组合
            brands = ['eero', 'netgear', 'asus', 'tp-link', 'linksys', 'google', 'amazon']
            for brand in brands:
                if brand in product_clean:
                    # 提取型号部分
                    model_part = product_clean.replace(brand, '').strip()
                    if model_part:
                        keywords.extend([
                            f"{brand} {model_part} review",
                            f"{model_part} review"
                        ])
                    break
        
        # 去重并返回
        return list(dict.fromkeys(keywords))  # 保持顺序的去重
    
    def update_progress(self, message: str, percentage: float = None):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback({
                'message': message,
                'percentage': percentage,
                'current_keyword': self.current_keyword_index,
                'total_keywords': self.total_keywords,
                'found_influencers': len(self.influencers)
            })
    
    def search_videos(self, query: str) -> List[Dict]:
        """搜索视频"""
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=self.max_results_per_query,
                type='video',
                publishedAfter=self.published_after,
                regionCode=self.region_code,
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
        return (subscriber_count >= self.min_subscribers or 
                view_count >= self.min_view_count)
    
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
    
    def process_video(self, video_item: Dict, search_keyword: str, product_name: str) -> None:
        """处理单个视频，检查是否为influencer"""
        video_id = video_item['id']['videoId']
        channel_id = video_item['snippet']['channelId']
        
        # 避免重复处理同一频道+产品组合
        channel_product_key = f"{channel_id}_{product_name.replace(' ', '_')}"
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
    
    def scrape_product(self, product_name: str) -> Dict:
        """
        爬取指定产品的influencer数据
        
        Args:
            product_name: 产品名称
            
        Returns:
            包含结果统计的字典
        """
        print(f"开始搜索产品: {product_name}")
        self.update_progress(f"生成搜索关键词: {product_name}")
        
        # 生成关键词
        keywords = self.generate_search_keywords(product_name)
        self.total_keywords = len(keywords)
        self.current_keyword_index = 0
        
        self.update_progress(f"生成了 {len(keywords)} 个搜索关键词", 0)
        
        initial_count = len(self.influencers)
        
        for i, keyword in enumerate(keywords):
            self.current_keyword_index = i + 1
            percentage = (i / len(keywords)) * 100
            
            self.update_progress(f"搜索关键词: '{keyword}'", percentage)
            print(f"正在搜索关键词: '{keyword}' ({i+1}/{len(keywords)})")
            
            videos = self.search_videos(keyword)
            
            for video in videos:
                self.process_video(video, keyword, product_name)
                time.sleep(0.1)  # 避免请求过快
            
            time.sleep(1)  # 关键词间延迟
            
        found_count = len(self.influencers) - initial_count
        
        result = {
            'product_name': product_name,
            'keywords_searched': len(keywords),
            'influencers_found': found_count,
            'total_influencers': len(self.influencers)
        }
        
        self.update_progress(f"产品 {product_name} 搜索完成，找到 {found_count} 个influencer", 100)
        
        return result
    
    def get_results_dataframe(self) -> pd.DataFrame:
        """获取结果DataFrame"""
        if not self.influencers:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.influencers)
        # 按订阅数排序
        df = df.sort_values('subscriber_count', ascending=False)
        return df
    
    def export_to_csv(self, filename: str) -> str:
        """导出结果到CSV文件"""
        df = self.get_results_dataframe()
        if df.empty:
            return None
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        return filename
    
    def get_summary_stats(self) -> Dict:
        """获取结果统计信息"""
        if not self.influencers:
            return {}
        
        df = self.get_results_dataframe()
        
        return {
            'total_influencers': len(self.influencers),
            'unique_channels': len(set(inf['channel_id'] for inf in self.influencers)),
            'products_searched': len(set(inf['product_reviewed'] for inf in self.influencers)),
            'avg_subscriber_count': int(df['subscriber_count'].mean()),
            'max_subscriber_count': int(df['subscriber_count'].max()),
            'avg_video_view_count': int(df['video_view_count'].mean()),
            'max_video_view_count': int(df['video_view_count'].max()),
            'top_channels': df.head(5)[['channel_name', 'subscriber_count', 'product_reviewed']].to_dict('records')
        }