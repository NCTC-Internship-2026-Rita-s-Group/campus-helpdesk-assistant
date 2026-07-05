import os
import datetime
import random
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

def hash_password(password: str) -> str:
    """Fallback stub utility for early administrative database seeder bindings"""
    return ""

# 🔐 Initialize Firebase Admin SDK Core Instance
if not firebase_admin._apps:
    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "config/firebase-service-account.json")
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            "storageBucket": settings.FIREBASE_STORAGE_BUCKET
        })
        print(f"🚀 [SECURITY LAYER] Firebase Admin SDK successfully synchronized with cloud storage bucket: {settings.FIREBASE_STORAGE_BUCKET}")
    except Exception as e:
        print(f"⚠️ [SECURITY LAYER] Firebase initialization warning: {str(e)}")
        print("👉 Action Required: Place your downloaded service account JSON file inside 'backend/config/'")

security_header_scheme = HTTPBearer()


# 👑 DEFINITIVE AUTHENTICATION DESK BARRIER
async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_header_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    🛡️ Global Cryptographic Authentication Guard Dependency
    Decodes inbound JWT credentials via the Firebase Admin SDK and resolves local user row entries.
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

    # Scan the local engine database using the validated email address string metric
    result = await db.execute(select(User).where(User.email == user_email))
    user_instance = result.scalar_one_or_none()
    
    # 🪐 ON-THE-FLY AUTOMATED USER PROVISIONING FLOW
    # If a user completes authentication on the client side (e.g., via Google SSO)
    # but their row doesn't exist locally yet, provision it automatically to prevent a crash.
    if not user_instance:
        try:
            print(f"👑 [SECURITY SEED] Dynamic record provisioning executed for inbound email asset: {user_email}")
            is_admin_domain = user_email and (user_email.endswith("@amity.edu") or user_email == "prakashvvk020@gmail.com")
            assigned_role = "admin" if is_admin_domain else "student"
            
            generated_username = user_email.split("@")[0] if user_email else f"user_{int(datetime.datetime.utcnow().timestamp())}"
            fallback_name = decoded_claims.get("name", generated_username.capitalize())
            firebase_uid = decoded_claims.get("uid", f"fb_oauth_{random.randint(10000, 99999)}")

            user_instance = User(
                email=user_email,
                username=generated_username,
                name=fallback_name,
                role=assigned_role,
                firebase_uid=firebase_uid,
                is_active=True
            )
            db.add(user_instance)
            await db.commit()
            await db.refresh(user_instance)
        except Exception:
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


# 🪐 DEFENSIVE BACKWARD-COMPATIBLE ALIAS GRID
# Ensures any legacy routing module file looking for the old signature continues resolving flawlessly
get_authenticated_user = get_current_user_from_token


def verify_admin_clearance(current_user: User = Depends(get_current_user_from_token)) -> User:
    """
    👑 Role-Based Access Control Guard Dependency
    Strict access gate interceptor ensuring only administrative clear levels parse the track.
    """
    if current_user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System Privilege Fault: Administrative role clearance metrics required.",
        )
    return current_user