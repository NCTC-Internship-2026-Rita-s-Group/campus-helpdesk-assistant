from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from app.config import settings

# ⚙️ Environment-Aware Engine Initialization
if settings.DATABASE_URL.startswith("sqlite"):
    # 🪶 Local Lightweight Async SQLite Engine Config
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False
    )
else:
    # 🚀 High-Capacity Production PostgreSQL Config (Supabase/Render)
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=20,             # Maintains 20 continuous connections alive
        max_overflow=10,          # Scales up dynamically during peak traffic
        pool_pre_ping=True,       # Recycles dropped connection paths safely
        connect_args={"ssl": True} # Enforces encrypted data transfers natively
    )

# Operational Asynchronous Session Factory bound to the active engine layer
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Master declarative inheritance class mapping schemas inside backend/app/models/
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Input Parameter Injection Factory (Dependency)
    Ensures every active API endpoint path runs on an isolated transaction thread,
    guaranteeing automated rollbacks on failures and clean closing lifecycles.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()