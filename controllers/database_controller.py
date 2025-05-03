from models.orm_model import Channel, Comment, Video
from models.database import connection

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from datetime import datetime

@connection 
async def insert_data_api(
    # comment_data
    comment_data: list[dict],
    
    # video_data
    video_id: str,
    title: str,
    view_count: int,
    comment_count: int,
    like_count: int,
    publish_date: datetime,
    channel_id: str,
    
    # channel_data
    id_channel: str, 
    title_channel: str, 
    view_count_channel: int, 
    subscription_count: int, 
    video_count: int, 
    account_creation_date: datetime, 
    
    session: AsyncSession,
    
    # video_data (optional)
    description: str | None = None,
    category: str | None = None,
   
    # channel_data (optional)
    country: str | None = None, 
    keywords: str | None = None, 
    description_channel: str | None = None
) -> str:

    try:
        # Create channel
        existing_channel = await session.scalar(
            select(Channel).where(Channel.id_channel == id_channel)
        )
        
        if not existing_channel:
            channel = Channel(
                id_channel=id_channel,
                title_channel=title_channel,
                keywords=keywords,
                description_channel=description_channel,
                view_count_channel=view_count_channel,
                subscription_count=subscription_count,
                video_count=video_count,
                country=country,
                account_creation_date=account_creation_date
            )
            session.add(channel)
            await session.flush()
        else:
            channel = existing_channel

        # Create video
        existing_video = await session.scalar(
            select(Video).where(Video.video_id == video_id)
        )

        if not existing_video: 
            video = Video(
                video_id=video_id,
                title=title,
                description=description,
                category=category,
                view_count=str(view_count),  
                comment_count=str(comment_count),
                like_count=str(like_count),
                publish_date=publish_date,
                channel_id=channel.id_channel  
            )
            session.add(video)
            await session.flush()
        else: 
            video = existing_video
        
        # Create comment (batch_size = 1000 )
        batch_size = 1000 
        for i in range(0, len(comment_data), batch_size):
            batch = comment_data[i:i + batch_size]
            comment_values = [
                {
                    'comment_id': com['comment_id'],
                    'text': com['text'],
                    'comment_publish_date': com['comment_publish_date'],
                    'like_count': com['comment_like_count'],
                    'reply_count': com.get('reply_count', 0),
                    'video_id': video_id,
                    'commenter_channel_id': com.get('commenter_channel_id', channel.id_channel),
                    'parent_comment_id': com.get('comment_parent_id')
                }
                for com in batch
            ]
            
            stmt = pg_insert(Comment).values(comment_values).on_conflict_do_nothing()
            await session.execute(stmt)
        
        await session.commit()
        return f'Created video ID {video.video_id}'

    except IntegrityError as e:
        await session.rollback()
        return f'Database integrity error: {str(e)}'
    except Exception as e:
        await session.rollback()
        return f'Error: {str(e)}'