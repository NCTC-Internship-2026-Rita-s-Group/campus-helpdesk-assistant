import re
import hashlib
import secrets
import logging
import datetime
import os  # 👑 Direct environmental path checker to bypass strict Pydantic rules
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from firebase_admin import auth as firebase_auth

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.database import get_db
from app.models.db_models import User
from app.services.security import verify_admin_clearance  # 🛡️ Protected administrative access guard
from app.config import settings                           # 📁 Centralized config registry

router = APIRouter(prefix="/auth", tags=["Unified Identity & Access Management"])

# 💾 STATEFUL IN-MEMORY TRANSACTION LEDGER MATRIX
otp_transaction_ledger = {}

# ==============================================================================
# 🔑 CRYPTOGRAPHIC PASSWORD SECURITY & BULLETPROOF ENVIRONMENT FILE PARSER
# ==============================================================================
def hash_password(password: str) -> str:
    """Hashes a password using built-in secure PBKDF2-HMAC-SHA256 with a unique salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${key.hex()}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a password against an existing PBKDF2 token hash string."""
    if "$" not in hashed_password or hashed_password == "OAUTH_EXTERNAL_MANAGED_IDENTITY":
        return False
    salt, hex_key = hashed_password.split("$", 1)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return key.hex() == hex_key

def load_env_file_manually() -> dict:
    """
    👑 FILE SYSTEM FALLBACK STREAM PARSER
    Directly extracts credentials from the physical .env file on disk to bypass
    Pydantic config schema restrictions and ensure immediate environmental connectivity.
    """
    env_dict = {}
    current_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(current_dir, ".env"),
        os.path.join(current_dir, "..", ".env"),
        os.path.join(current_dir, "..", "..", ".env"),
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "backend", ".env")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            env_dict[key.strip()] = val.strip().strip('"').strip("'")
                break
            except Exception:
                pass
    return env_dict

def dispatch_secure_otp_email(recipient_email: str, otp_code: str) -> bool:
    """
    📧 Elite Enterprise Email Transportation Engine
    👑 UPGRADED: Renders a premium, university-branded HTML interface incorporating
    the absolute corporate logo asset with an instant double-click selection grid box.
    """
    fallback_env = load_env_file_manually()
    
    smtp_host = os.getenv("SMTP_HOST") or fallback_env.get("SMTP_HOST") or getattr(settings, "SMTP_HOST", "smtp.gmail.com")
    smtp_port_raw = os.getenv("SMTP_PORT") or fallback_env.get("SMTP_PORT") or str(getattr(settings, "SMTP_PORT", 465))
    smtp_port = int(smtp_port_raw)
    
    smtp_user = os.getenv("SMTP_USER") or fallback_env.get("SMTP_USER") or getattr(settings, "SMTP_USER", None)
    smtp_pass = os.getenv("SMTP_PASSWORD") or os.getenv("SMTP_PASS") or fallback_env.get("SMTP_PASSWORD") or fallback_env.get("SMTP_PASS") or getattr(settings, "SMTP_PASSWORD", None)

    if not smtp_user or not smtp_pass:
        print(f"⚠️ [SMTP UNCONFIGURED] Falling back to log trace. Core OTP: {otp_code}")
        return False

    message = MIMEMultipart("alternative")
    message["Subject"] = f"Verification Code: {otp_code} for Amity University Account Recovery"
    message["From"] = f"Amity University Jharkhand Support <{smtp_user}>"
    message["To"] = recipient_email

    # 👑 BRANDED LOGO HOOK: Update the image src link below to your deployment CDN domain asset when going live!
    logo_url = "https://raw.githubusercontent.com/NathCorp-Internship/assets/main/logo.png"

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Account Security Verification — Amity University Jharkhand</title>
</head>
<body style="margin:0; padding:0; background-color:#030712; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#030712; padding:40px 16px;">
    <tr>
      <td align="center" style="padding:0;">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px; width:100%; background-color:#090f20; border:1px solid #1e293b; border-radius:16px; padding:48px 40px; box-shadow:0 20px 60px rgba(0,0,0,0.5);">

          <tr>
            <td align="center" style="padding:0 0 32px 0;">
              <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td align="center" style="padding-bottom:16px;">
                    <img src="LOGO_URL_PLACEHOLDER" alt="Amity University Logo" width="56" height="56" style="display:block; width:56px; height:56px; border:0; outline:none; text-decoration:none; filter: drop-shadow(0px 4px 10px rgba(0,0,0,0.3));">
                  </td>
                </tr>
                <tr>
                  <td align="center">
                    <span style="display:inline-block; padding:8px 20px; background-color:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.35); border-radius:999px; color:#f59e0b; font-size:11px; font-weight:700; letter-spacing:3px; text-transform:uppercase; line-height:1;">
                      Amity University Jharkhand
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <tr>
            <td align="center" style="padding:0 0 20px 0;">
              <h1 style="margin:0; color:#ffffff; font-size:28px; font-weight:700; line-height:1.3; letter-spacing:-0.5px; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
                Account Security Verification
              </h1>
            </td>
          </tr>

          <tr>
            <td align="center" style="padding:0 0 36px 0;">
              <p style="margin:0; color:#94a3b8; font-size:15px; line-height:1.65; max-width:460px;">
                A request has been initialized to securely verify your identity and establish protected access credentials on the Amity University Jharkhand network. Please use the verification code below to continue.
              </p>
            </td>
          </tr>

          <tr>
            <td align="center" style="padding:0 0 16px 0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#020617; border:1px solid #1e293b; border-radius:12px;">
                <tr>
                  <td align="center" style="padding:32px 20px;">
                    <div style="color:#64748b; font-size:11px; font-weight:600; letter-spacing:2.5px; text-transform:uppercase; margin-bottom:14px; line-height:1;">
                      Verification Code
                    </div>
                    <div style="user-select:all; -webkit-user-select:all; -moz-user-select:all; -ms-user-select:all; color:#f59e0b; font-family:Consolas, Menlo, 'Courier New', Courier, monospace; font-size:42px; font-weight:700; letter-spacing:12px; line-height:1.1; padding:4px 0 0 12px; cursor:text;">
                      123456
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <tr>
            <td align="center" style="padding:0 0 40px 0;">
              <p style="margin:0; color:#64748b; font-size:12px; font-style:italic; line-height:1.5;">
                Double-click or hold code to select and copy instantly.
              </p>
            </td>
          </tr>

          <tr>
            <td style="padding:0 0 24px 0;">
              <hr style="border:none; border-top:1px solid #1e293b; margin:0; height:1px;">
            </td>
          </tr>

          <tr>
            <td align="center" style="padding:0;">
              <p style="margin:0 0 10px 0; color:#64748b; font-size:12px; line-height:1.6;">
                This security window will expire in <span style="color:#94a3b8; font-weight:600;">5 minutes</span>.
              </p>
              <p style="margin:0; color:#475569; font-size:12px; line-height:1.6;">
                If you did not initiate this request, please change your security parameters immediately.
              </p>
            </td>
          </tr>

        </table>

        <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px; width:100%; padding:24px 40px 0 40px;">
          <tr>
            <td align="center">
              <p style="margin:0; color:#334155; font-size:11px; line-height:1.5; letter-spacing:0.3px;">
                © Amity University Jharkhand · Information Security Office
              </p>
            </td>
          </tr>
        </table>

      </td>
    </tr>
  </table>
</body>
</html>"""

    # Dynamically inject logo path string and OTP variable values securely
    html_body = html_template.replace("LOGO_URL_PLACEHOLDER", logo_url).replace("123456", otp_code)
    message.attach(MIMEText(html_body, "html"))

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, recipient_email, message.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, recipient_email, message.as_string())
                
        print(f"🚀 [SMTP SUCCESS] Enterprise verification email delivered successfully to user: {recipient_email}")
        return True
    except Exception as mail_err:
        print(f"❌ [SMTP CRITICAL TRANSMIT FAILURE] Transport failed to hand off data packet: {str(mail_err)}")
        return False


# ==============================================================================
# 📊 AUTHENTICATION DATA TRANSFER SCHEMAS
# ==============================================================================
class TokenExchangePayload(BaseModel):
    id_token: str  

class UserIdentityProfileResponse(BaseModel):
    uid: Optional[str]
    email: str
    name: str
    role: str
    redirect_target: str  
    is_active: bool

class PromoteUserPayload(BaseModel):
    target_email: EmailStr
    target_role: str = "admin"

class AdminLoginPayload(BaseModel):
    username: str  
    password: str

class AdminLoginResponse(BaseModel):
    uid: Optional[str]
    email: str
    name: str
    role: str
    custom_token: str  
    redirect_target: str

class RequestOtpPayload(BaseModel):
    email: EmailStr

class VerifyOtpPayload(BaseModel):
    email: EmailStr
    otp_code: str

class CommitPasswordResetPayload(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str


# ==============================================================================
# 🔄 ENDPOINT 1: THE UNIFIED ROLE-DISCOVERY IDENTITY SYNC (STUDENT GATEWAY)
# ==============================================================================
@router.post("/sync", response_model=UserIdentityProfileResponse)
async def synchronize_and_discover_user_role(
    payload: TokenExchangePayload,
    db: AsyncSession = Depends(get_db)
):
    try:
        decoded_token = firebase_auth.verify_id_token(payload.id_token)
        fb_uid = decoded_token.get("uid")
        fb_email = decoded_token.get("email") or decoded_token.get("claims", {}).get("email")
        fb_name = decoded_token.get("name", fb_email.split("@")[0] if fb_email else "Campus User")
        
    except Exception as token_err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Identity verification failed. Secure token rejected: {str(token_err)}"
        )

    try:
        user_query = select(User).where((User.firebase_uid == fb_uid) | (User.email == fb_email))
        query_result = await db.execute(user_query)
        existing_user = query_result.scalar_one_or_none()

        if not existing_user:
            if not fb_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Identity provider token configuration error: Email attribute missing."
                )
            existing_user = User(
                email=fb_email,
                hashed_password="OAUTH_EXTERNAL_MANAGED_IDENTITY",  
                name=fb_name,
                role="student",  
                username=None,   
                firebase_uid=fb_uid,
                is_active=True
            )
            db.add(existing_user)
            await db.commit()
            await db.refresh(existing_user)
            print(f"👤 [IDENTITY AUTO-PROVISIONED] Created profile row for {fb_email} as 'student'.")
            
        elif not existing_user.firebase_uid:
            existing_user.firebase_uid = fb_uid
            db.add(existing_user)
            await db.commit()
            await db.refresh(existing_user)

        if not existing_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This campus account infrastructure profile has been administratively deactivated."
            )

        redirect_map = {
            "admin": "/admin/dashboard",
            "helpdesk": "/admin/dashboard",
            "faculty": "/admin/dashboard",
            "student": "/student/chat"
        }
        target_route = redirect_map.get(existing_user.role, "/student/chat")

        return {
            "uid": existing_user.firebase_uid,
            "email": existing_user.email,
            "name": existing_user.name,
            "role": existing_user.role,
            "redirect_target": target_route,
            "is_active": existing_user.is_active
        }

    except HTTPException:
        raise
    except Exception as system_fault:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal database mapping fault during synchronization: {str(system_fault)}"
        )


# ==============================================================================
# 🏢 ENDPOINT 2: SECURE USERNAME/PASSWORD ADMINISTRATIVE LOGIN GATEWAY
# ==============================================================================
@router.post("/admin-login", response_model=AdminLoginResponse)
async def administrative_credentials_login(
    payload: AdminLoginPayload,
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where((User.username == payload.username) | (User.email == payload.username))
    result = await db.execute(query)
    admin_user = result.scalar_one_or_none()

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Denied: Invalid administrative credentials configuration."
        )

    if not verify_password(payload.password, admin_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Denied: Invalid administrative credentials configuration."
        )

    if not admin_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This administrative workspace context profile has been deactivated."
        )

    if admin_user.role not in ["admin", "helpdesk", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Security Violation: Insufficient role credentials clearance mapping."
        )

    try:
        developer_claims = {
            "email": admin_user.email,
            "role": admin_user.role
        }
        custom_token = firebase_auth.create_custom_token(admin_user.firebase_uid, developer_claims)
        custom_token_str = custom_token.decode("utf-8") if isinstance(custom_token, bytes) else custom_token
    except Exception as token_err:
        raise HTTPException(
            status_code=settings.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Identity pipeline critical error: Failed to mint session context: {str(token_err)}"
        )

    redirect_map = {
        "admin": "/admin/dashboard",
        "helpdesk": "/admin/dashboard",
        "faculty": "/admin/dashboard"
    }

    return {
        "uid": admin_user.firebase_uid,
        "email": admin_user.email,
        "name": admin_user.name,
        "role": admin_user.role,
        "custom_token": custom_token_str,
        "redirect_target": redirect_map.get(admin_user.role, "/admin/dashboard")
    }


# ==============================================================================
# ➕ ENDPOINT 3: ATOMIC ADMINISTRATIVE ACCOUNT PROVISIONING
# ==============================================================================
@router.post("/create-admin")
async def create_new_administrative_user(
    payload: dict,  
    current_admin: User = Depends(verify_admin_clearance),  
    db: AsyncSession = Depends(get_db)
):
    full_name = payload.get("full_name", payload.get("fullName", payload.get("adminFullName", ""))).strip()
    email_address = payload.get("email", payload.get("adminEmail", "")).strip()
    username_text = payload.get("username", payload.get("adminUsername", "")).strip()
    raw_password = payload.get("password", payload.get("adminPassword", ""))

    if not full_name or not email_address or not username_text or not raw_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input Validation Error: Full Name, Institutional Email, Username, and Password are required."
        )

    if len(raw_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firebase Policy Fault: Password string must consist of at least 6 characters."
        )

    username_regex = r"^[a-z][a-z0-9_.]{3,19}$"
    if not re.match(username_regex, username_text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format Validation Failed: Usernames must start with a lowercase letter, contain only lowercase letters, digits, underscores, or periods, and be 4 to 20 characters long."
        )

    username_check = await db.execute(select(User).where(User.username == username_text))
    if username_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The administrative username '{username_text}' is already allocated inside system records."
        )

    email_check = await db.execute(select(User).where(User.email == email_address))
    if email_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The institutional address '{email_address}' is already mapped to an active profile."
        )

    firebase_uid_token = None
    try:
        fb_user = firebase_auth.create_user(
            email=email_address,
            password=raw_password,
            display_name=full_name,
            disabled=False
        )
        firebase_uid_token = fb_user.uid
        firebase_auth.set_custom_user_claims(firebase_uid_token, {"role": "admin"})
        
    except Exception as cloud_err:
        print(f"❌ [FIREBASE AUTH REGJECTION] Cloud provider blocked account deployment: {str(cloud_err)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Identity Provider Error: {str(cloud_err)}"
        )

    try:
        new_admin = User(
            email=email_address,
            username=username_text,
            name=full_name,
            role="admin",
            firebase_uid=firebase_uid_token,
            is_active=True,
            hashed_password=hash_password(raw_password)
        )
        db.add(new_admin)
        
        try:
            audit_query = text("""
                INSERT INTO chat_audit_logs (user_query, ai_response, latency_seconds, estimated_tokens, is_safe, triggered_rules)
                VALUES (:user_query, :ai_response, :latency_seconds, :estimated_tokens, :is_safe, :triggered_rules)
            """)
            await db.execute(audit_query, {
                "user_query": "ADMIN_PROVISION_OPERATOR",
                "ai_response": f"Successfully initialized administrative profile for operator username '{username_text}' ({email_address}).",
                "latency_seconds": 0.0,
                "estimated_tokens": 0,
                "is_safe": True,
                "triggered_rules": "None"
            })
        except Exception:
            pass

        await db.commit()
        print(f"👑 [ADMIN PROVISIONED] New operator '{username_text}' generated successfully by supervisor {current_admin.email}.")
        return {
            "success": True, 
            "message": f"Administrative operator profile '{username_text}' successfully registered."
        }
        
    except Exception as db_err:
        await db.rollback()
        if firebase_uid_token:
            try:
                firebase_auth.delete_user(firebase_uid_token)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Relational persistent storage write block failed: {str(db_err)}"
        )


# ==============================================================================
# 🔼 ENDPOINT 4: ADMINISTRATIVE ROLE PROMOTION ELEVATION
# ==============================================================================
@router.post("/promote", status_code=status.HTTP_200_OK)
async def elevate_user_access_clearance(
    payload: PromoteUserPayload,
    current_admin: User = Depends(verify_admin_clearance),  
    db: AsyncSession = Depends(get_db)
):
    if payload.target_role not in ["admin", "student", "helpdesk", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target promotion value '{payload.target_role}' is not a recognized campus role archetype."
        )

    user_lookup = select(User).where(User.email == payload.target_email)
    lookup_result = await db.execute(user_lookup)
    target_user = lookup_result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operation aborted: No user profile row exists matching address '{payload.target_email}'."
        )

    if target_user.email == current_admin.email and payload.target_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security Violations: An administrator cannot strip away their own structural clearance codes."
        )

    try:
        old_role = target_user.role
        target_user.role = payload.target_role
        
        if target_user.firebase_uid:
            try:
                firebase_auth.set_custom_user_claims(target_user.firebase_uid, {"role": payload.target_role})
            except Exception as claims_err:
                print(f"⚠️ Firebase claims sync delayed: {claims_err}")

        db.add(target_user)
        await db.commit()
        return {
            "success": True,
            "message": "Account profile authorization updated completely.",
            "target_user_email": target_user.email,
            "previous_clearance": old_role,
            "assigned_clearance": target_user.role,
            "authorizing_operator": current_admin.email
        }

    except Exception as write_fault:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to modify target authorization parameter settings: {str(write_fault)}"
        )


# ==============================================================================
# 📧 PRODUCTION HIGH-SECURITY OTP LIFE-CYCLE ENDPOINTS (GOOGLE OAUTH COMPATIBLE)
# ==============================================================================
@router.post("/request-otp")
async def request_password_reset_otp(
    payload: RequestOtpPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    🔢 STEP 1: OTP Generation & Secure Inbox Dispatch Gateway
    """
    target_email = payload.email.strip().lower()

    user_check = await db.execute(select(User).where(User.email == target_email))
    local_user = user_check.scalar_one_or_none()

    fb_uid = None
    if local_user:
        fb_uid = local_user.firebase_uid
    else:
        try:
            fb_user_node = firebase_auth.get_user_by_email(target_email)
            fb_uid = fb_user_node.uid
        except Exception:
            return {"success": True, "message": "Verification code has been dispatched if a linked profile exists."}

    generated_otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    secure_hash = hashlib.sha256(generated_otp.encode('utf-8')).hexdigest()

    otp_transaction_ledger[target_email] = {
        "token_hash": secure_hash,
        "expiration": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        "firebase_uid": fb_uid
    }

    dispatch_secure_otp_email(target_email, generated_otp)

    return {"success": True, "message": "A high-security 6-digit verification code has been dispatched to your email address."}


@router.post("/verify-otp")
async def verify_password_reset_otp(payload: VerifyOtpPayload):
    """
    🔢 STEP 2: Real-Time Code Verification
    """
    target_email = payload.email.strip().lower()
    active_record = otp_transaction_ledger.get(target_email)

    if not active_record:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No verification parameters found for this email coordinate.")

    if datetime.datetime.utcnow() > active_record["expiration"]:
        if target_email in otp_transaction_ledger:
            del otp_transaction_ledger[target_email]
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code timeout: Security key has expired.")

    computed_hash = hashlib.sha256(payload.otp_code.strip().encode('utf-8')).hexdigest()
    if computed_hash != active_record["token_hash"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification failed: Incorrect 6-digit security sequence code.")

    return {"success": True, "message": "Verification code matched successfully. Proceeding to password re-assignment."}


@router.post("/reset-password-with-otp")
async def commit_password_reset_via_otp(
    payload: CommitPasswordResetPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    🔢 STEP 3: Cryptographic Access Key Modification & Provider Linking
    """
    target_email = payload.email.strip().lower()
    active_record = otp_transaction_ledger.get(target_email)

    if not active_record:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Security verification reference lost. Please request a new code.")

    computed_hash = hashlib.sha256(payload.otp_code.strip().encode('utf-8')).hexdigest()
    if computed_hash != active_record["token_hash"] or datetime.datetime.utcnow() > active_record["expiration"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Security validation checkpoint rejected transaction metrics.")

    new_password_raw = payload.new_password
    if len(new_password_raw) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password length violation: Input criteria requires at least 6 characters.")

    resolved_uid = active_record["firebase_uid"]

    try:
        firebase_auth.update_user(resolved_uid, password=new_password_raw)
        print(f"🔒 [FIREBASE SECURE ALIGNMENT] Linked provider password updated for account: {target_email}")

        user_query = select(User).where(User.email == target_email)
        query_result = await db.execute(user_query)
        local_user = query_result.scalar_one_or_none()

        if local_user:
            local_user.hashed_password = hash_password(new_password_raw)
            db.add(local_user)
        else:
            fb_cloud_user = firebase_auth.get_user(resolved_uid)
            local_user = User(
                email=target_email,
                username=target_email.split("@")[0],
                name=fb_cloud_user.display_name or "Campus Student",
                role="student",
                firebase_uid=resolved_uid,
                is_active=True,
                hashed_password=hash_password(new_password_raw)
            )
            db.add(local_user)

        try:
            audit_query = text("""
                INSERT INTO chat_audit_logs (user_query, ai_response, latency_seconds, estimated_tokens, is_safe, triggered_rules)
                VALUES (:user_query, :ai_response, :latency_seconds, :estimated_tokens, :is_safe, :triggered_rules)
            """)
            await db.execute(audit_query, {
                "user_query": "USER_PASSWORD_RESET_OTP",
                "ai_response": f"Access key reset verified and synced cleanly for profile: {target_email}.",
                "latency_seconds": 0.0,
                "estimated_tokens": 0,
                "is_safe": True,
                "triggered_rules": "None"
            })
        except Exception:
            pass

        await db.commit()

        if target_email in otp_transaction_ledger:
            del otp_transaction_ledger[target_email]

        return {"success": True, "message": "Security password update successfully processed and matched."}

    except Exception as general_fault:
        await db.rollback()
        print(f"❌ [CRITICAL CREDENTIAL RESET CRASH] Reset aborted: {str(general_fault)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Identity provider update failed.")