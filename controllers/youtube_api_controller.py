from controllers.database_controller import insert_data_api
from models.async_youtube_model import YouTubeDataModel
import asyncio
from datetime import datetime

class YouTubeDataParser:
    def __init__(self, api_key: str):
        self.cor = YouTubeDataModel(api_key=api_key)
        self.list_videos_id = None

        self.semaphore = asyncio.Semaphore(5)

    async def search_videos(self,
                query: str,
                date_after: datetime = datetime(2005, 2, 14).strftime("%Y-%m-%d"),  
                date_before: datetime = datetime(2025, 1, 1).strftime("%Y-%m-%d"),
                category: str = '1', 
                max_results: int = 42, 
                video_duration: str = 'medium'): 
        try:
            self.list_videos_id = await self.cor.search_youtube_videos(
                query=query,
                max_results=max_results,
                category=category,
                published_after=datetime.strptime(date_after, "%Y-%m-%d"),
                published_before=datetime.strptime(date_before, "%Y-%m-%d"), 
                video_duration=video_duration)
            return self.list_videos_id  
        except Exception as e:
            print(f"Error occurred: {e}")
            return None 

    async def create_data_video(self, video_id):
        async with self.semaphore: # Using a semaphore
            try:
                data_comment, data_video, data_channel = await asyncio.gather(
                    self.cor.get_video_comments(video_id=video_id), 
                    self.cor.get_video_metadata(),
                    self.cor.get_channel_metadata()
                )

                comment_data = [
                    {
                        'comment_id': comment['comment_id'],
                        'text': comment['text'],
                        'comment_publish_date': datetime.fromtimestamp(comment['comment_publish_date']),
                        'comment_like_count': comment['comment_like_count'],
                        'reply_count': comment.get('reply_count', 0),
                        'commenter_channel_id': comment['commenter_channel_id'],
                        'comment_parent_id': comment.get('comment_parent_id')
                    }
                    for comment in data_comment
                ]

                result = await insert_data_api(
                    comment_data=comment_data,
                    video_id=data_video['video_id'],
                    title=data_video['video_title'],
                    view_count=int(data_video['video_view_count']),
                    comment_count=int(data_video['video_comment_count']),
                    like_count=int(data_video['video_like_count']),
                    publish_date=datetime.fromtimestamp(data_video['video_publish_date']),
                    channel_id=data_video['channel_id'],
                    description=data_video.get('video_description'),
                    category=data_video.get('video_category'),
                    id_channel=data_channel['channel_id'],
                    title_channel=data_channel['title'],
                    view_count_channel=int(data_channel['view_count']),
                    subscription_count=int(data_channel['subscription_count']),
                    video_count=int(data_channel['video_count']),
                    account_creation_date=datetime.fromtimestamp(data_channel['account_creation_date']),
                    country=data_channel.get('country'),
                    keywords=data_channel.get('keywords'),
                    description_channel=data_channel.get('description')
                )
                return result
            except Exception as e:
                print(f"Error occurred: {e}")
                return False