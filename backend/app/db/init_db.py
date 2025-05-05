from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import inspect, text
from app.db.session import DATABASE_URL, Base
from app.models.assessment import AssessmentRecord, VulnerabilityRecord, PriorityAction
import sys
import asyncio

async def get_table_names(engine: AsyncEngine) -> list[str]:
    """Get list of table names using async connection"""
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        return [row[0] for row in result]

async def init_db(force_drop: bool = False):
    """Initialize database tables
    
    Args:
        force_drop: If True, will drop existing tables before creating new ones.
                   If False, will only create tables that don't exist.
    """
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    # Get existing tables
    existing_tables = await get_table_names(engine)
    
    if force_drop:
        if not sys.stdin.isatty():
            print("Cannot drop tables in non-interactive mode")
            return
        
        response = input("Are you sure you want to drop all existing tables? This cannot be undone. [y/N]: ")
        if response.lower() != 'y':
            print("Aborting table drop")
            return
            
        print("Dropping existing tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    print("Creating missing tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Get new tables
    new_tables = set(await get_table_names(engine)) - set(existing_tables)
    if new_tables:
        print(f"Created new tables: {', '.join(new_tables)}")
    else:
        print("No new tables needed to be created")
    
    await engine.dispose()

if __name__ == "__main__":
    force_drop = "--force-drop" in sys.argv
    asyncio.run(init_db(force_drop)) 