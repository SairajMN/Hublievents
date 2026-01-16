"""
Authentication dependencies for Hublievents Backend API.
Provides reusable authentication dependencies for FastAPI routes.
"""

from typing import Optional
from fastapi import Request, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from .jwt import get_current_user, get_current_active_user, require_admin, require_super_admin


def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Get current user with admin privileges.

    Args:
        current_user: Current authenticated user

    Returns:
        User object with admin privileges

    Raises:
        HTTPException: If user is not an admin
    """
    from fastapi import HTTPException, status

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def get_current_user_optional(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    This is a wrapper around the JWT get_current_user_optional function.

    Args:
        db: Database session
        current_user: Current authenticated user (may be None)

    Returns:
        User object or None
    """
    return current_user


def get_request_user_agent(request: Request) -> Optional[str]:
    """
    Extract user agent from request headers.

    Args:
        request: FastAPI request object

    Returns:
        User agent string or None
    """
    return request.headers.get("User-Agent")


def get_request_ip(request: Request) -> str:
    """
    Extract client IP address from request.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address
    """
    # Check for forwarded headers (useful behind load balancers/proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP if multiple are present
        return forwarded_for.split(",")[0].strip()

    # Check for other proxy headers
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct client IP
    return request.client.host if request.client else "unknown"


def require_ownership_or_admin(
    resource_user_id: int,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require that current user owns the resource or is an admin.

    Args:
        resource_user_id: User ID that owns the resource
        current_user: Current authenticated user

    Returns:
        Current user if authorized

    Raises:
        HTTPException: If user is not authorized
    """
    from fastapi import HTTPException, status

    if current_user.id != resource_user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )

    return current_user


def require_admin_or_owner(
    resource_user_id: int,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require that current user is an admin or owns the resource.

    Args:
        resource_user_id: User ID that owns the resource
        current_user: Current authenticated user

    Returns:
        Current user if authorized

    Raises:
        HTTPException: If user is not authorized
    """
    return require_ownership_or_admin(resource_user_id, current_user)


def require_customer_or_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require that current user is a customer or admin (not guest).

    Args:
        current_user: Current authenticated user

    Returns:
        Current user if authorized

    Raises:
        HTTPException: If user is not authorized
    """
    from fastapi import HTTPException, status

    if current_user.role == User.UserRole.GUEST and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires a customer account"
        )

    return current_user


def log_admin_action(
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    notes: Optional[str] = None,
    request: Request = None,
    current_user: User = Depends(require_admin)
):
    """
    Log an admin action for audit purposes.

    Args:
        action: Action performed
        resource_type: Type of resource affected
        resource_id: ID of affected resource
        notes: Additional notes
        request: FastAPI request object
        current_user: Current admin user

    Returns:
        AdminLog entry
    """
    from models.admin_log import AdminLog, AdminAction

    db = next(get_db())
    try:
        ip_address = get_request_ip(request) if request else None
        user_agent = get_request_user_agent(request) if request else None

        # Convert string action to enum
        try:
            action_enum = AdminAction(action)
        except ValueError:
            action_enum = AdminAction.SECURITY_ALERT  # Default for unknown actions

        return AdminLog.log_action(
            db=db,
            admin_id=current_user.id,
            action=action_enum,
            resource_type=resource_type,
            resource_id=resource_id,
            notes=notes,
            ip_address=ip_address,
            user_agent=user_agent
        )
    finally:
        db.close()


# Re-export key dependencies for convenience
__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    "get_current_user_optional",
    "require_admin",
    "require_super_admin",
    "require_ownership_or_admin",
    "require_admin_or_owner",
    "require_customer_or_admin",
    "get_request_user_agent",
    "get_request_ip",
    "log_admin_action",
]
