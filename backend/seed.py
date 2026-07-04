import asyncio
import sys
import os

# Adjust sys.path automatically so Python can discover modules inside the app directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal, engine, Base
from app.models import db_models 
from app.services.seed import seed_system_data

async def run_seeding_engine():
    """
    🏗️ Development-Grade Clean Force-Migration & Seeding Tool
    Drops existing tables to clear old entries and builds clean tables 
    to guarantee a fresh, rich data state for the frontend interface.
    """
    print("🏗️ Connecting to PostgreSQL instance wire...")
    
    async with engine.begin() as conn:
        # 🗑️ Clear out any existing data blocks to prevent collision flags
        print("🗑️ Wiping out legacy database tables to ensure a clean slate...")
        await conn.run_sync(Base.metadata.drop_all)
        
        # 🔨 Build structural schemas completely brand new
        print("🔨 Re-synchronizing fresh database tables (users, tickets, notices)...")
        await conn.run_sync(Base.metadata.create_all)
        
    print("✨ Relational database tables generated flawlessly.")

    # Open a clean transactional worker thread to inject the 2026 data matrices
    async with AsyncSessionLocal() as session:
        success = await seed_system_data(session)
        if success:
            print("🚀 🟢 Database seeding execution finalized completely!")
        else:
            print("🟡 Seeding sequence skipped by internal guard rails.")

    # Safely close down connection pool infrastructure trackers
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_seeding_engine())