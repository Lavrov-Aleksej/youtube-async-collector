from youtube_api import YouTubeDataAPI
from typing import List, Optional
from functools import lru_cache
from datetime import datetime
import re

class YouTubeValidator:
    @staticmethod
    def _sync_extract_video_id(url_or_id: str) -> Optional[str]:
        """Synchronous implementation of ID extraction"""
        if len(url_or_id) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', url_or_id):
            return url_or_id
            
        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11})",
            r"youtu\.be\/([0-9A-Za-z_-]{11})"
        ]
        for pattern in patterns:
            if match := re.search(pattern, url_or_id):
                return match.group(1)
        return None

    @staticmethod
    def validate_query(q: str) -> str:
        """Validates that the search query is not empty and contains at least 2 non-whitespace characters."""
        if not isinstance(q, str):
            raise TypeError("Query must be a string")
        
        stripped_q = q.strip()  
        if len(stripped_q) < 2:
            raise ValueError('Query must be at least 2 non-whitespace characters long')
        return stripped_q
    
    @staticmethod
    def validate_category(category: str) -> str:
         """Validates the video category format"""
         if not (1 <= int(category) <= 44):
             raise ValueError('The videoCategoryId takes positions from 1 to 44')
         return str(category)

    @staticmethod
    def validate_max_results(max_results: int) -> int:
         """Validates the maximum results value"""
         if not (max_results > 0):
             raise ValueError('The result cannot be negative or zero')
         return max_results

    @staticmethod
    def validate_dates(date_input: datetime) -> datetime:
        """Validates the input value as a datetime object"""
        if not isinstance(date_input, datetime):
            raise ValueError('Input must be a datetime object')
        return date_input


class YouTubeDataModel:
    def __init__(self, api_key: str):
        self.YT = self._create_client(api_key)
        self.video_id = None 
        self.channel_id = None

    @staticmethod
    @lru_cache(maxsize=42)
    def _create_client(api_key: str):
        """Static method with caching for API client creation"""
        return YouTubeDataAPI(key=api_key, api_version='3', verify_api_key=True)
    
    def set_video_id(self, video_id: str) -> None:
        """Sets the video ID for subsequent operations"""
        self.video_id = YouTubeValidator._sync_extract_video_id(video_id)
        
    async def search_youtube_videos(
            self,
            query: str,
            published_after: datetime = datetime(2005, 2, 14),  
            published_before: datetime = datetime(2025, 1, 1),
            category: str = '1', 
            max_results: int = 42, 
            video_duration: str = 'medium') -> list[str]:
        """
        Searches for YouTube videos based on specified criteria.
        """
        # Define validation class
        valid = YouTubeValidator

        try:
            data = self.YT.search(
                q=valid.validate_query(q=query),
                max_results=valid.validate_max_results(max_results=max_results), 
                order_by='viewCount',
                region_code="RU",
                relevance_language='ru',
                published_after=valid.validate_dates(date_input=published_after),
                published_before=valid.validate_dates(date_input=published_before),
                video_duration=video_duration, 
                search_type='video', 
                videoCategoryId=valid.validate_category(category=category), 
                part=['snippet']
            )
            return [item['video_id'] for item in data]
        except Exception as e:
            print(f"Error searching YouTube: {e}")

    async def get_video_comments(self, video_id: str = None) -> List[dict]:
        """Retrieves comments for the specified video"""
        if video_id:
            self.set_video_id(video_id)
        elif not self.video_id:
            raise ValueError("Video ID is not set")
        try:
            return self.YT.get_video_comments(
                video_id=self.video_id,
                part=['snippet']
            )
        except Exception as e:
            raise RuntimeError(f"Error fetching comments: {e}") from e
        
    async def get_video_metadata(self, video_id: str = None)-> List[dict]:
        """Retrieves metadata for the specified video"""
        if video_id:
            self.set_video_id(video_id)
        elif not self.video_id:
            raise ValueError("Video ID is not set")
        try:
            metadata = self.YT.get_video_metadata(
                video_id=self.video_id, 
                part=['statistics', 'snippet']  
            )
            self.channel_id = str(metadata['channel_id']) # extract channel_id
            return metadata
        except Exception as e:
            raise RuntimeError(f"Error fetching video metadata: {e}")
    
    async def get_channel_metadata(self, channel_id: str = None):
        """Retrieves channel metadata"""
        channel_id = channel_id or self.channel_id
        if not channel_id:
            raise ValueError('Channel ID not found. Enter it manually or call get_video_metadata first')
        try:
            return self.YT.get_channel_metadata(
                channel_id=channel_id,
                part=[
                    "id", "snippet", "contentDetails", 
                    "statistics", "topicDetails", "brandingSettings"
                ] 
            )
        except Exception as e:
            raise RuntimeError(f"Error fetching channel metadata: {e}")