from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import urllib.parse
import logging

logger = logging.getLogger(__name__)

# Check if all required Postgres settings are present
required_db_vars = [settings.POSTGRES_USER, settings.POSTGRES_PASSWORD, settings.POSTGRES_DB]
if all(required_db_vars):
    # Defensive: ensure password is a string, even if None
    password = settings.POSTGRES_PASSWORD or ""
    if not password:
        logger.warning("POSTGRES_PASSWORD is not set. Using empty string for password encoding.")
    encoded_password = urllib.parse.quote_plus(str(password))
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
    logger.info("Database engine initialized.")
else:
    engine = None
    AsyncSessionLocal = None
    Base = None
    logger.warning("Postgres environment variables not fully set. Database will not be initialized.")

def get_db():
    if AsyncSessionLocal is None:
        raise RuntimeError("Database is not configured. Please set all required Postgres environment variables.")
    async def _get_db():
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    return _get_db()

def is_db_configured():
    return AsyncSessionLocal is not None 