from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models.schemas import APIResponse
from app.services.seed import seed_initial_notices

# Import your entire modular routing layer mesh
from app.api import notice_routes, ticket_routes, reminder_routes, document_routes, chat_routes, admin_routes

import app.models.db_models as db_models

# Initialize SQL Relational Tables
Base.metadata.create_all(bind=engine)

# Trigger Seeding Layer for Campus Announcements
db = SessionLocal()
try:
    seed_initial_notices(db)
finally:
    db.close()

app = FastAPI(title=settings.PROJECT_NAME)

# ==========================================
# SYSTEM MIDDLEWARE: CORS SECURITY CONFIG
# ==========================================
origins = [
    "http://localhost:3000",      # Common React build environment port
    "http://localhost:5173",      # Vite's default dev environment engine port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# PRODUCTION HARDENING: GLOBAL ERROR HANDLERS
# ==========================================
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Catch any bad data payloads sent by the frontend and wrap them 
    cleanly in our branded APIResponse envelope.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Data validation failed. Please check your request parameters.",
            "data": None,
            "error": exc.errors()
        }
    )

@app.exception_handler(Exception)
def universal_exception_handler(request: Request, exc: Exception):
    """
    Catch any unhandled runtime crashes across the backend layers 
    and disguise them cleanly to protect application stability.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected server-side operational error occurred.",
            "data": None,
            "error": str(exc)
        }
    )

# ==========================================
# SYSTEM CORE APIRUTER MOUNTINGS
# ==========================================
app.include_router(chat_routes.router, prefix="/api/chat", tags=["Core Conversational Core"])
app.include_router(notice_routes.router, prefix="/api/notices", tags=["Notice Board Operations"])
app.include_router(ticket_routes.router, prefix="/api/tickets", tags=["Student Grievance Operations"])
app.include_router(reminder_routes.router, prefix="/api/reminders", tags=["Student Reminder Operations"])
app.include_router(document_routes.router, prefix="/api/documents", tags=["Admin Document Knowledge Management"])
app.include_router(admin_routes.router, prefix="/api/admin", tags=["Administrative Monitoring Control"])

@app.get("/health")
def health_check():
    return APIResponse(
        success=True,
        message="System is healthy, configurations loaded, and SQLite tables initialized!",
        data={"project": settings.PROJECT_NAME, "status": "Online"}
    )