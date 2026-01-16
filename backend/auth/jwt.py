"""
JWT token management for Hublievents Backend API.
Handles token creation, verification, and user authentication.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from jwt import PyJWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.user import User
from models.admin_log import AdminLog, AdminAction

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        JWT access token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Data to encode in the token

    Returns:
        JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to verify
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        # Verify token type
        if payload.get("type") != token_type:
            return None

        # Check if token has expired
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            return None

        return payload
    except PyJWTError:
        return None


def get_token_payload(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    Extract and verify JWT token from request headers.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        Token payload or None if invalid
    """
    if not credentials:
        return None

    return verify_token(credentials.credentials)


def get_current_user(
    db: Session = Depends(get_db),
    payload: Optional[Dict[str, Any]] = Depends(get_token_payload)
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        db: Database session
        payload: JWT token payload

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Log admin login attempt
    if user.is_admin:
        AdminLog.log_action(
            db=db,
            admin_id=user.id,
            action=AdminAction.LOGIN_ATTEMPT,
            resource_type="user",
            resource_id=user.id,
            notes="User authenticated via JWT token"
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user (not banned/disabled).

    Args:
        current_user: Current authenticated user

    Returns:
        Active user object

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    if not current_user.is_verified and current_user.role != User.UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not verified"
        )

    return current_user


def get_current_user_optional(
    db: Session = Depends(get_db),
    payload: Optional[Dict[str, Any]] = Depends(get_token_payload)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for optional authentication.

    Args:
        db: Database session
        payload: JWT token payload (optional)

    Returns:
        User object or None
    """
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    return user if user and user.is_active else None


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Require admin privileges for endpoint access.

    Args:
        current_user: Current authenticated user

    Returns:
        User object with admin privileges

    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def require_super_admin(current_user: User = Depends(require_admin)) -> User:
    """
    Require super admin privileges for endpoint access.

    Args:
        current_user: Current authenticated admin user

    Returns:
        User object with super admin privileges

    Raises:
        HTTPException: If user is not a super admin
    """
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required"
        )
    return current_user


def create_token_pair(user: User) -> Dict[str, str]:
    """
    Create access and refresh token pair for user.

    Args:
        user: User object

    Returns:
        Dictionary containing access_token and refresh_token
    """
    access_token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    refresh_token_data = {"sub": str(user.id)}

    access_token = create_access_token(access_token_data)
    refresh_token = create_refresh_token(refresh_token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def refresh_access_token(refresh_token: str, db: Session) -> Optional[Dict[str, str]]:
    """
    Refresh access token using refresh token.

    Args:
        refresh_token: Refresh token string
        db: Database session

    Returns:
        New token pair or None if refresh token is invalid
    """
    payload = verify_token(refresh_token, "refresh")
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.verify_refresh_token(refresh_token):
        return None

    # Create new token pair
    return create_token_pair(user)


def blacklist_token(token: str) -> None:
    """
    Add token to blacklist (for logout).
    Note: In production, implement proper token blacklisting with Redis/database.

    Args:
        token: Token to blacklist
    """
    # TODO: Implement proper token blacklisting
    # For now, this is a placeholder
    # In production, store blacklisted tokens in Redis or database
    pass


def is_token_blacklisted(token: str) -> bool:
    """
    Check if token is blacklisted.

    Args:
        token: Token to check

    Returns:
        True if token is blacklisted, False otherwise
    """
    # TODO: Implement token blacklist checking
    # For now, always return False
    return False
