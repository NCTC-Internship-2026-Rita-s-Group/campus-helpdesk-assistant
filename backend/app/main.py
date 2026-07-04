import os
import warnings

# 🛑 1. Disable ChromaDB's telemetry engine completely
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# 🌐 2. Allow Hugging Face to use its local cached embedding models without trying to call home
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# 🔕 3. Suppress the Google API Python 3.10 deprecation warning clutter
warnings.filterwarnings("ignore", category=FutureWarning, module="google.api_core")

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from sqlalchemy import select

from app.config import settings
from app.database import engine, Base, AsyncSessionLocal 
from app.services.limiter import limiter
from app.models import db_models 
from app.api.auth_routes import hash_password 

# 👑 Automated Master Super Admin Seeding Lifecycle Core
async def seed_super_administrator():
    """
    Enforces the automatic setup of the primary system administrator profile
    on server startup without requiring manual database editing tools.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Look for existing user match properties inside the database file
            query = select(db_models.User).where(
                (db_models.User.email == "prakashvvk020@gmail.com") | 
                (db_models.User.username == "prakashprajapati")
            )
            result = await session.execute(query)
            admin_exists = result.scalar_one_or_none()

            if not admin_exists:
                temporary_password = "SuperAdminPassword2026"
                hashed_pass = hash_password(temporary_password)
                
                master_admin = db_models.User(
                    email="prakashvvk020@gmail.com",
                    username="prakashprajapati",
                    name="Prakash Kumar Prajapati",
                    hashed_password=hashed_pass,
                    role="admin",
                    firebase_uid="super_admin_prakash_2026", 
                    is_active=True
                )
                
                session.add(master_admin)
                await session.commit()
                print("\n" + "="*80)
                print("👑 [DATABASE SEED] Master Super Administrator Account Provisioned Flawlessly!")
                print(f"   Email:    prakashvvk020@gmail.com")
                print(f"   Username:  prakashprajapati")
                print(f"   Password:  SuperAdminPassword2026")
                print("   ⚠️ SECURITY NOTICE: Log in and use the 'Security Options' modal to update this password.")
                print("="*80 + "\n")
            else:
                print("👑 [DATABASE CHECK] Master Super Administrator profile active and synchronized.")
        except Exception as e:
            await session.rollback()
            print(f"❌ [DATABASE ERROR] Failed to complete super admin check: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    🏗️ Enterprise System Lifespan Lifecycle Manager
    Handles non-blocking programmatic database table creation on server start,
    seeds the core super administrator, and disposes resource pools on shutdown.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await seed_super_administrator()
    yield 
    await engine.dispose()


# Initialize FastAPI app with modern lifespan tracking
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-ready multi-modal campus RAG helpdesk core processing engine.",
    version=settings.VERSION,
    lifespan=lifespan,
    redirect_slashes=True  # 🌐 Defensive routing mechanism standard
)

# 🔒 RATE LIMITER EXCEPTION LINK LAYER
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 🛡️ CORS MIDDLEWARE ROUTING MATRIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Infrastructure System Health"])
async def root_health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "engine": "FastAPI ASGI Execution Core Layer",
        "database_layer": "Asynchronous Relational Engine Active"
    }


# 🧭 CENTRALIZED ROUTER REGISTRIES CONNECTION GRID
from app.api import notice_routes, ticket_routes, chat_routes, document_routes, admin_routes, auth_routes

# 🌐 DUAL-PREFIX REGISTER ROUTING MATRICES
# Mount routers under both /api and /api/v1 prefixes to completely prevent 404 network mismatch faults
for api_prefix in ["/api/v1", "/api"]:
    app.include_router(notice_routes.router, prefix=api_prefix)
    app.include_router(ticket_routes.router, prefix=api_prefix)
    app.include_router(chat_routes.router, prefix=api_prefix)
    app.include_router(document_routes.router, prefix=api_prefix)
    app.include_router(admin_routes.router, prefix=api_prefix)
    app.include_router(auth_routes.router, prefix=api_prefix)