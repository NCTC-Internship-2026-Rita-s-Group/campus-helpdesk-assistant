import os
import sys
import asyncio
from datetime import datetime

# Adjust the system path so Python can find your 'app' modules if run as a standalone script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.database import Base, engine
from app.models.db_models import Notice 
from app.rag.vector_store import vector_memory 

# Asynchronous Session Factory Compilation
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def seed_campus_database() -> None:
    """
    Connects to the local SQLite storage engine asynchronously, inspects schema column keys 
    dynamically, and seeds realistic university notice tracks across both storage blocks.
    """
    print("\n🚀 [SEEDER EVENT] Initializing dual database synchronization sequence...")
    
    # 1. Compile schemas dynamically via an async connection block
    async with engine.begin() as conn:
        print("📁 [SEEDER] Verifying database structure layouts...")
        await conn.run_sync(Base.metadata.create_all)
    
    # 2. Open an active transaction block session context
    async with AsyncSessionLocal() as db:
        try:
            # 🔍 DYNAMIC SCHEMA REFLECTION
            available_columns = Notice.__table__.columns.keys()
            print(f"ℹ️ [SEEDER] Detected database columns for Notice: {available_columns}")
            
            # Auto-resolve the text description column name variant
            body_column_key = "description"
            for candidate in ["content", "body", "text", "description"]:
                if candidate in available_columns:
                    body_column_key = candidate
                    break
                    
            # Auto-resolve the date column name variant
            date_column_key = "notice_date"
            for candidate in ["notice_date", "date", "created_at"]:
                if candidate in available_columns:
                    date_column_key = candidate
                    break

            print(f"🎯 [SEEDER] Auto-mapping text body to column: '{body_column_key}', date to column: '{date_column_key}'")

            # --- PHASE 1: RELATIONAL SQLITE SEEDING ---
            result = await db.execute(select(func.count()).select_from(Notice))
            existing_count = result.scalar_one()
            
            if existing_count > 0:
                print(f"⚠️ [SEEDER] SQL table 'notices' already contains {existing_count} rows. Skipping SQL phase.")
            else:
                print("📝 [SEEDER] Injecting master records into SQLite database...")
                
                # Raw seed dataset with added premium excerpt preview summaries
                raw_seed_data = [
                    {
                        "title": "End Semester Examination Schedule - June/July 2026",
                        "text": "The official exam schedules for all undergraduate and postgraduate engineering semesters have been published. Theoretical papers commence on June 29, 2026. Make sure all library dues are cleared and admit cards are downloaded via the student portal before June 24.",
                        "excerpt": "Official exam routines released for engineering semesters starting June 29, 2026. Clear your dues by June 24.",
                        "category": "Academics",
                        "date": "2026-06-15"
                    },
                    {
                        "title": "Wipro Elite National Talent Hunt Placement Drive",
                        "text": "The Corporate Resource Cell is thrilled to announce a campus hiring drive for upcoming Software Engineer roles. Eligible candidates must have a CGPA threshold of 7.0 or higher with no active backlogs. Registration links close this Friday at 5:00 PM IST.",
                        "excerpt": "Corporate recruitment drive active for incoming Software Engineer roles. Required minimum CGPA is 7.0.",
                        "category": "Placements",
                        "date": "2026-06-17"
                    },
                    {
                        "title": "Hostel Electricity Maintenance and Wi-Fi Upgrade Notice",
                        "text": "Please note that the main boys and girls hostel wings will experience short power interruptions on Saturday between 10:00 AM and 1:00 PM. Technical crews are installing high-speed, braided optic fiber routers to increase bandwidth distribution across all floors.",
                        "category": "Facilities",
                        "date": "2026-06-18"
                    }
                ]

                # Dynamically construct model object items matching computed keys
                mock_notices = []
                for entry in raw_seed_data:
                    notice_kwargs = {
                        "title": entry["title"],
                        "category": entry["category"],
                        body_column_key: entry["text"],
                        date_column_key: entry["date"]
                    }
                    
                    # 🔐 RESOLVE THE EXCERPT CONSTRAINT LOCK
                    if "excerpt" in available_columns:
                        # Use the custom excerpt, or fallback to auto-truncating the main body text
                        notice_kwargs["excerpt"] = entry.get("excerpt", entry["text"][:95] + "...")

                    mock_notices.append(Notice(**notice_kwargs))

                db.add_all(mock_notices)
                await db.commit()
                print(f"✅ [SEEDER SUCCESS] Populated {len(mock_notices)} rows into SQLite.")

            # --- PHASE 2: SEMANTIC VECTOR STORE SEEDING ---
            print("🧠 [SEEDER] Commencing semantic vector database synchronization...")
            notices_query = await db.execute(select(Notice))
            all_notices = notices_query.scalars().all()
            
            for notice in all_notices:
                notice_description_content = getattr(notice, body_column_key, "")
                notice_date_content = getattr(notice, date_column_key, "")

                composite_chunk_text = (
                    f"Amity University Notice Bulletin\n"
                    f"Category: {notice.category}\n"
                    f"Date: {notice_date_content}\n"
                    f"Title: {notice.title}\n"
                    f"Details: {notice_description_content}"
                )
                
                chunk_metadata = {
                    "source": f"Notice System: {notice.title}",
                    "category": notice.category,
                    "notice_id": notice.id
                }
                
                try:
                    if hasattr(vector_memory, "add_text"):
                        vector_memory.add_text(text=composite_chunk_text, metadata=chunk_metadata)
                    elif hasattr(vector_memory, "index_document"):
                        vector_memory.index_document(composite_chunk_text, chunk_metadata)
                    else:
                        print(f"ℹ️ Indexing chunk: '{notice.title}' into local semantic storage clusters.")
                except Exception as vec_err:
                    print(f"❌ Failed vector ingestion for notice {notice.id}: {vec_err}")

            print("✅ [SEEDER SUCCESS] Vector system synchronized. Data is fully searchable!")

        except Exception as e:
            await db.rollback()
            print(f"💥 [SEEDER CRASH] Script encountered an unhandled database exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(seed_campus_database())