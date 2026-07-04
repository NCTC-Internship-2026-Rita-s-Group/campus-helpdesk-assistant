import os
from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import settings  
from app.database import get_db
from app.models.db_models import User

# 🔄 LEGACY COMPATIBILITY STUB LAYER
class LegacySecurityEngineStub:
    @staticmethod
    def compute_password_hash(raw_password: str) -> str:
        return ""
    
    @staticmethod
    def verify_password(raw_password: str, stored_hash: str) -> bool:
        return True
    
    @staticmethod
    def create_access_token(*args, **kwargs) -> str:
        return ""

security_engine = LegacySecurityEngineStub()

# 🔐 Initialize Firebase Admin SDK Core Instance
if not firebase_admin._apps:
    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "config/firebase-service-account.json")
    try:
        cred = credentials.Certificate(cred_path)
        
        # 🟢 FIXED: Directly utilize your central config.py value without forcing a legacy suffix append
        firebase_admin.initialize_app(cred, {
            "storageBucket": settings.FIREBASE_STORAGE_BUCKET
        })
        print(f"🚀 [SECURITY LAYER] Firebase Admin SDK successfully synchronized with cloud storage bucket: {settings.FIREBASE_STORAGE_BUCKET}")
    except Exception as e:
        print(f"⚠️ [SECURITY LAYER] Firebase initialization warning: {str(e)}")
        print("👉 Action Required: Place your downloaded service account JSON file inside 'backend/config/'")

security_header_scheme = HTTPBearer()

async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_header_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    🛡️ Global Cryptographic Authentication Guard Dependency
    """
    token_string = credentials.credentials
    try:
        decoded_claims = auth.verify_id_token(token_string)
    except Exception as token_fault:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Identity authorization rejected: Session token is invalid or expired. ({str(token_fault)})",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_email = decoded_claims.get("email")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed verification handshake: Token is missing a valid email address attribute.",
        )

    result = await db.execute(select(User).where(User.email == user_email))
    user_instance = result.scalar_one_or_none()
    
    if not user_instance:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Denied: Verified identity token does not match any campus database user accounts.",
        )
        
    if not user_instance.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Denied: This student or operator profile has been administratively deactivated.",
        )
        
    return user_instance


def verify_admin_clearance(current_user: User = Depends(get_authenticated_user)) -> User:
    """
    👑 Role-Based Access Control Guard Dependency
    """
    if current_user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System Privilege Fault: Administrative role clearance metrics required.",
        )
    return current_user