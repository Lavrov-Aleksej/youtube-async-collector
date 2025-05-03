from models.database import Base
from sqlalchemy import DateTime, String, Integer, BigInteger, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

class Comment(Base):
    __tablename__ = 'comments'
    
    comment_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    comment_publish_date: Mapped[datetime] = mapped_column(DateTime)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    video_id: Mapped[str | None] = mapped_column(String(255), ForeignKey('videos_metadata.video_id'), nullable=True, index=True)
    commenter_channel_id: Mapped[str] = mapped_column(String(255), index=True)
    parent_comment_id: Mapped[str | None] = mapped_column(String(255), ForeignKey('comments.comment_id'), nullable=True, index=True)

    video: Mapped["Video"] = relationship(
        'Video', 
        back_populates='comments',
        lazy="joined"
    )

    channel: Mapped["Channel"] = relationship(
        'Channel', 
        back_populates='comments',
        primaryjoin="Comment.commenter_channel_id == Channel.id_channel",
        foreign_keys=[commenter_channel_id],
        lazy="joined"
    )
    
    parent_comment: Mapped["Comment"] = relationship(
        'Comment',
        remote_side=[comment_id],
        back_populates='replies',
        lazy="joined"
    )
    
    replies: Mapped[list["Comment"]] = relationship(
        'Comment',
        back_populates='parent_comment',
        lazy="dynamic"
    )

class Video(Base):
    __tablename__ = 'videos_metadata'
    
    video_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    view_count: Mapped[str] = mapped_column(Text)
    comment_count: Mapped[str] = mapped_column(String(10))
    like_count: Mapped[str] = mapped_column(Text)
    publish_date: Mapped[datetime] = mapped_column(DateTime)
    channel_id: Mapped[str | None] = mapped_column(String(255), ForeignKey('channels_metadata.id_channel'), nullable=True, index=True)

    comments: Mapped[list["Comment"]] = relationship(
        'Comment',
        back_populates='video',
        lazy="dynamic", 
        cascade="all, delete-orphan"
    )
    
    channel: Mapped["Channel"] = relationship(
        'Channel',
        back_populates='videos',
        lazy="joined"
    )

class Channel(Base):
    __tablename__ = 'channels_metadata'
    
    id_channel: Mapped[str] = mapped_column(String(255), primary_key=True)
    title_channel: Mapped[str] = mapped_column(String(255))
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_channel: Mapped[str | None] = mapped_column(Text, nullable=True)
    view_count_channel: Mapped[int] = mapped_column(BigInteger)
    subscription_count: Mapped[int] = mapped_column(BigInteger)
    video_count: Mapped[int] = mapped_column(BigInteger)
    country: Mapped[str | None] = mapped_column(Text, nullable=True)
    account_creation_date: Mapped[datetime] = mapped_column(DateTime)

    comments: Mapped[list["Comment"]] = relationship(
        'Comment', 
        back_populates='channel',
        primaryjoin="Channel.id_channel == Comment.commenter_channel_id",
        foreign_keys="[Comment.commenter_channel_id]",
        lazy="dynamic"
    )
    
    videos: Mapped[list["Video"]] = relationship(
        'Video',
        back_populates='channel',
        lazy="dynamic"
    )