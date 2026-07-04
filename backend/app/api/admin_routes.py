from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.db_models import User
from app.models.schemas import UserCreate, UserResponse, UserLoginPayload, TokenResponse
from app.services.security import security_engine, verify_admin_clearance, get_authenticated_user

router = APIRouter(prefix="/auth", tags=["System Authentication & Access Controls"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def onboard_new_campus_identity(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    📝 User Onboarding Endpoint
    Verifies data uniqueness, hashes user credentials via Bcrypt, and creates the account.
    """
    # Verify if identity email intersection matrix exists to prevent duplications
    duplicate_check = await db.execute(select(User).where(User.email == payload.email))
    if duplicate_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account is already registered with this institutional email address."
        )

    # Transform plaintext credentials safely down into a Bcrypt string hash
    hashed_pass_string = security_engine.compute_password_hash(payload.password)

    new_user = User(
        email=payload.email,
        hashed_password=hashed_pass_string,
        name=payload.name,
        role=payload.role,
        is_active=True
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
async def authenticate_user_session(payload: UserLoginPayload, db: AsyncSession = Depends(get_db)):
    """
    🔑 User Authentication Session Gateway
    Validates Bcrypt credentials and yields a signed 7-day cryptographic JWT bearer token matrix.
    """
    result = await db.execute(select(User).where(User.email == payload.email))
    user_instance = result.scalar_one_or_none()

    # Unified general failure error layout preventing username/email harvesting exposure vectors
    auth_failure_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect institutional email address or access password criteria.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user_instance or not user_instance.is_active:
        raise auth_failure_exception

    # Execute password verification match checks
    is_valid_match = security_engine.verify_password(payload.password, user_instance.hashed_password)
    if not is_valid_match:
        raise auth_failure_exception

    # Generate cryptographic JWT authentication string token payload
    signed_token = security_engine.create_access_token(
        user_id=user_instance.id,
        email=user_instance.email,
        role=user_instance.role
    )

    return {
        "access_token": signed_token,
        "token_type": "bearer",
        "user": user_instance
    }


@router.get("/me", response_model=UserResponse)
async def fetch_current_session_profile(current_user: User = Depends(get_authenticated_user)):
    """
    🔍 Token Verification Helper Endpoint
    Allows the frontend interface to instantly verify token validity and retrieve user details upon reload.
    """
    return current_user