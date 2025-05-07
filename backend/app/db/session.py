from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import urllib.parse
import logging

logger = logging.getLogger(__name__)

# Defensive: ensure password is a string, even if None
password = settings.POSTGRES_PASSWORD or ""
if not password:
    logger.warning("POSTGRES_PASSWORD is not set. Using empty string for password encoding.")
encoded_password = urllib.parse.quote_plus(str(password))

# Build the DATABASE_URL from individual components
DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{encoded_password}@localhost:5432/{settings.POSTGRES_DB}"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 