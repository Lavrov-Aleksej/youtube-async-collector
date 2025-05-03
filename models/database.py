from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import DateTime, func
from models.config import settings

from datetime import datetime

# Create async session
DATABASE_URL: str = settings.get_db_url()
engine = create_async_engine(
    url=DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10
)

async_session_maker = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False)

# Base class
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True  
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now()
    )

def connection(method):
    """Decorator for automatic management of database sessions"""
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback() 
                raise e  
            finally:
                await session.close() 

    return wrapper