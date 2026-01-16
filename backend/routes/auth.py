"""
Authentication routes for Hublievents Backend API.
Handles user registration, login, token refresh, and logout.
"""

from datetime import timedelta
from typing import Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.user import User, UserRole
from models.admin_log import AdminLog, AdminAction
from schemas.user import (
    UserCreate, UserLogin, TokenResponse, TokenRefresh,
    PasswordResetRequest, PasswordResetConfirm, ChangePassword,
    UserResponse
)
from auth.jwt import create_token_pair, refresh_access_token, get_current_active_user
from auth.password import get_password_hash, verify_password, validate_password_strength
from auth.dependencies import get_request_ip, get_request_user_agent, log_admin_action

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.

    - **email**: User's email address (unique)
    - **password**: User's password (must meet strength requirements)
    - **full_name**: User's full name
    - **phone**: Optional phone number
    """
    # Validate password strength
    password_validation = validate_password_strength(user_data.password)
    if not password_validation["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Password does not meet security requirements",
                "errors": password_validation["feedback"]
            }
        )

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    try:
        # Create new user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            phone=user_data.phone,
            role=user_data.role
        )
        user.set_password(user_data.password)

        db.add(user)
        db.commit()
        db.refresh(user)

        # Log admin action if user registered as admin
        if user.is_admin:
            ip_address = get_request_ip(request)
            user_agent = get_request_user_agent(request)

            AdminLog.log_action(
                db=db,
                admin_id=user.id,
                action=AdminAction.USER_CREATED,
                resource_type="user",
                resource_id=user.id,
                notes=f"User registered as {user.role.value}",
                ip_address=ip_address,
                user_agent=user_agent
            )

        logger.info(f"New user registered: {user.email} (ID: {user.id})")

        # TODO: Send verification email in background
        # background_tasks.add_task(send_verification_email, user.email, user.email_verification_token)

        return user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User registration failed due to data conflict"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"User registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access tokens.

    - **email**: User's email address
    - **password**: User's password
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not user.verify_password(login_data.password):
        # Log failed login attempt for admin accounts
        if user.is_admin:
            ip_address = get_request_ip(request)
            user_agent = get_request_user_agent(request)

            AdminLog.log_action(
                db=db,
                admin_id=user.id,
                action=AdminAction.LOGIN_ATTEMPT,
                resource_type="user",
                resource_id=user.id,
                notes="Failed login attempt",
                ip_address=ip_address,
                user_agent=user_agent,
                risk_level="low"
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    # Update last login
    user.last_login = db.func.now()
    db.commit()

    # Create token pair
    token_data = create_token_pair(user)

    # Set refresh token hash for rotation
    expires_at = db.func.now() + timedelta(days=7)  # 7 days
    user.set_refresh_token(token_data["refresh_token"], expires_at)
    db.commit()

    logger.info(f"User logged in: {user.email} (ID: {user.id})")

    return TokenResponse(
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_type="bearer",
        expires_in=30 * 60,  # 30 minutes in seconds
        user=user
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefresh,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    - **refresh_token**: Valid refresh token
    """
    token_data = refresh_access_token(refresh_data.refresh_token, db)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user for response
    payload = refresh_access_token.__wrapped__(refresh_data.refresh_token, db)
    if payload:
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()

        logger.info(f"Token refreshed for user: {user.email if user else 'unknown'}")

        return TokenResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutes in seconds
            user=user
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token refresh failed",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_active_user),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Logout user by clearing refresh token.
    Access token should be discarded by client.
    """
    # Clear refresh token
    current_user.clear_refresh_token()
    db.commit()

    # Log admin logout
    if current_user.is_admin and request:
        ip_address = get_request_ip(request)
        user_agent = get_request_user_agent(request)

        AdminLog.log_action(
            db=db,
            admin_id=current_user.id,
            action=AdminAction.LOGIN_ATTEMPT,  # Reuse for logout
            resource_type="user",
            resource_id=current_user.id,
            notes="User logged out",
            ip_address=ip_address,
            user_agent=user_agent
        )

    logger.info(f"User logged out: {current_user.email} (ID: {current_user.id})")

    return {"message": "Successfully logged out"}


@router.post("/password-reset/request")
async def request_password_reset(
    reset_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset for user account.

    - **email**: Email address of the account
    """
    user = db.query(User).filter(User.email == reset_data.email).first()

    # Always return success for security (don't reveal if email exists)
    if user:
        # Generate reset token
        import secrets
        reset_token = secrets.token_urlsafe(32)
        expires_at = db.func.now() + timedelta(hours=24)  # 24 hours

        user.password_reset_token = reset_token
        user.password_reset_expires = expires_at
        db.commit()

        # TODO: Send password reset email
        # background_tasks.add_task(send_password_reset_email, user.email, reset_token)

        logger.info(f"Password reset requested for: {user.email}")

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token and new password.

    - **token**: Password reset token
    - **new_password**: New password
    """
    # Validate new password
    password_validation = validate_password_strength(reset_data.new_password)
    if not password_validation["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Password does not meet security requirements",
                "errors": password_validation["feedback"]
            }
        )

    # Find user with valid reset token
    user = db.query(User).filter(
        User.password_reset_token == reset_data.token,
        User.password_reset_expires > db.func.now()
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Update password
    user.set_password(reset_data.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.commit()

    logger.info(f"Password reset completed for: {user.email}")

    return {"message": "Password has been reset successfully"}


@router.post("/password/change")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change password for authenticated user.

    - **current_password**: Current password for verification
    - **new_password**: New password
    """
    # Verify current password
    if not current_user.verify_password(password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password
    password_validation = validate_password_strength(password_data.new_password)
    if not password_validation["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "New password does not meet security requirements",
                "errors": password_validation["feedback"]
            }
        )

    # Update password
    current_user.set_password(password_data.new_password)

    # Clear refresh token for security (force re-login on all devices)
    current_user.clear_refresh_token()

    db.commit()

    logger.info(f"Password changed for user: {current_user.email}")

    return {"message": "Password changed successfully. Please login again."}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's information.
    """
    return current_user
