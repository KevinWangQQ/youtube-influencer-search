from datetime import datetime
import sqlite3
import json
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = 'database.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 搜索任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                product_name TEXT NOT NULL,
                api_key_hash TEXT NOT NULL,
                min_subscribers INTEGER NOT NULL,
                min_view_count INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                progress REAL DEFAULT 0,
                progress_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                total_keywords INTEGER DEFAULT 0,
                current_keyword INTEGER DEFAULT 0,
                found_influencers INTEGER DEFAULT 0,
                error_message TEXT
            )
        ''')
        
        # Influencer结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS influencer_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                channel_name TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                channel_url TEXT NOT NULL,
                channel_country TEXT,
                subscriber_count INTEGER NOT NULL,
                product_reviewed TEXT NOT NULL,
                search_keyword TEXT NOT NULL,
                video_title TEXT NOT NULL,
                video_id TEXT NOT NULL,
                video_url TEXT NOT NULL,
                video_view_count INTEGER NOT NULL,
                video_published_at TEXT NOT NULL,
                video_description TEXT,
                total_channel_views INTEGER,
                total_channel_videos INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES search_tasks (task_id)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_id ON influencer_results (task_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_channel_id ON influencer_results (channel_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product ON influencer_results (product_reviewed)')
        
        conn.commit()
        conn.close()
    
    def create_search_task(self, task_id: str, product_name: str, api_key_hash: str, 
                          min_subscribers: int, min_view_count: int) -> bool:
        """创建搜索任务"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO search_tasks 
                (task_id, product_name, api_key_hash, min_subscribers, min_view_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (task_id, product_name, api_key_hash, min_subscribers, min_view_count))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"创建搜索任务失败: {e}")
            return False
    
    def update_task_status(self, task_id: str, status: str, 
                          progress: float = None, progress_message: str = None,
                          total_keywords: int = None, current_keyword: int = None,
                          found_influencers: int = None, error_message: str = None) -> bool:
        """更新任务状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 构建动态更新语句
            updates = ['status = ?']
            params = [status]
            
            if progress is not None:
                updates.append('progress = ?')
                params.append(progress)
            
            if progress_message is not None:
                updates.append('progress_message = ?')
                params.append(progress_message)
            
            if total_keywords is not None:
                updates.append('total_keywords = ?')
                params.append(total_keywords)
            
            if current_keyword is not None:
                updates.append('current_keyword = ?')
                params.append(current_keyword)
            
            if found_influencers is not None:
                updates.append('found_influencers = ?')
                params.append(found_influencers)
            
            if error_message is not None:
                updates.append('error_message = ?')
                params.append(error_message)
            
            if status == 'running' and progress == 0:
                updates.append('started_at = CURRENT_TIMESTAMP')
            elif status == 'completed':
                updates.append('completed_at = CURRENT_TIMESTAMP')
            
            params.append(task_id)
            
            sql = f"UPDATE search_tasks SET {', '.join(updates)} WHERE task_id = ?"
            cursor.execute(sql, params)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新任务状态失败: {e}")
            return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT task_id, product_name, status, progress, progress_message,
                       total_keywords, current_keyword, found_influencers,
                       created_at, started_at, completed_at, error_message
                FROM search_tasks WHERE task_id = ?
            ''', (task_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'task_id': row[0],
                    'product_name': row[1],
                    'status': row[2],
                    'progress': row[3],
                    'progress_message': row[4],
                    'total_keywords': row[5],
                    'current_keyword': row[6],
                    'found_influencers': row[7],
                    'created_at': row[8],
                    'started_at': row[9],
                    'completed_at': row[10],
                    'error_message': row[11]
                }
            return None
        except Exception as e:
            print(f"获取任务状态失败: {e}")
            return None
    
    def save_influencer_results(self, task_id: str, influencers: List[Dict]) -> bool:
        """保存influencer结果"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for inf in influencers:
                cursor.execute('''
                    INSERT INTO influencer_results 
                    (task_id, channel_name, channel_id, channel_url, channel_country,
                     subscriber_count, product_reviewed, search_keyword, video_title,
                     video_id, video_url, video_view_count, video_published_at,
                     video_description, total_channel_views, total_channel_videos)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task_id, inf['channel_name'], inf['channel_id'], inf['channel_url'],
                    inf['channel_country'], inf['subscriber_count'], inf['product_reviewed'],
                    inf['search_keyword'], inf['video_title'], inf['video_id'],
                    inf['video_url'], inf['video_view_count'], inf['video_published_at'],
                    inf['video_description'], inf['total_channel_views'], inf['total_channel_videos']
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存influencer结果失败: {e}")
            return False
    
    def get_task_results(self, task_id: str) -> List[Dict]:
        """获取任务结果"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT channel_name, channel_id, channel_url, channel_country,
                       subscriber_count, product_reviewed, search_keyword, video_title,
                       video_id, video_url, video_view_count, video_published_at,
                       video_description, total_channel_views, total_channel_videos
                FROM influencer_results 
                WHERE task_id = ?
                ORDER BY subscriber_count DESC
            ''', (task_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'channel_name': row[0],
                    'channel_id': row[1],
                    'channel_url': row[2],
                    'channel_country': row[3],
                    'subscriber_count': row[4],
                    'product_reviewed': row[5],
                    'search_keyword': row[6],
                    'video_title': row[7],
                    'video_id': row[8],
                    'video_url': row[9],
                    'video_view_count': row[10],
                    'video_published_at': row[11],
                    'video_description': row[12],
                    'total_channel_views': row[13],
                    'total_channel_videos': row[14]
                })
            
            return results
        except Exception as e:
            print(f"获取任务结果失败: {e}")
            return []
    
    def get_search_history(self, limit: int = 20) -> List[Dict]:
        """获取搜索历史"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT task_id, product_name, status, found_influencers,
                       created_at, completed_at
                FROM search_tasks 
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    'task_id': row[0],
                    'product_name': row[1],
                    'status': row[2],
                    'found_influencers': row[3],
                    'created_at': row[4],
                    'completed_at': row[5]
                })
            
            return history
        except Exception as e:
            print(f"获取搜索历史失败: {e}")
            return []
    
    def get_task_summary(self, task_id: str) -> Optional[Dict]:
        """获取任务摘要统计"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取基本任务信息
            cursor.execute('''
                SELECT product_name, status, found_influencers, total_keywords
                FROM search_tasks WHERE task_id = ?
            ''', (task_id,))
            
            task_info = cursor.fetchone()
            if not task_info:
                return None
            
            # 获取统计信息
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_results,
                    COUNT(DISTINCT channel_id) as unique_channels,
                    AVG(subscriber_count) as avg_subscribers,
                    MAX(subscriber_count) as max_subscribers,
                    AVG(video_view_count) as avg_views,
                    MAX(video_view_count) as max_views
                FROM influencer_results WHERE task_id = ?
            ''', (task_id,))
            
            stats = cursor.fetchone()
            
            # 获取Top 5频道
            cursor.execute('''
                SELECT channel_name, subscriber_count, product_reviewed
                FROM influencer_results 
                WHERE task_id = ?
                ORDER BY subscriber_count DESC
                LIMIT 5
            ''', (task_id,))
            
            top_channels = [
                {
                    'channel_name': row[0],
                    'subscriber_count': row[1],
                    'product_reviewed': row[2]
                }
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            return {
                'product_name': task_info[0],
                'status': task_info[1],
                'total_influencers': task_info[2],
                'keywords_searched': task_info[3],
                'unique_channels': stats[1] if stats[1] else 0,
                'avg_subscriber_count': int(stats[2]) if stats[2] else 0,
                'max_subscriber_count': stats[3] if stats[3] else 0,
                'avg_video_view_count': int(stats[4]) if stats[4] else 0,
                'max_video_view_count': stats[5] if stats[5] else 0,
                'top_channels': top_channels
            }
            
        except Exception as e:
            print(f"获取任务摘要失败: {e}")
            return None