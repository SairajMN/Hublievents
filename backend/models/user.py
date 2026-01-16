"""
User model for Hublievents Backend API.
Includes role-based access control and secure password handling.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from passlib.context import CryptContext
from database import Base

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(str, enum.Enum):
    """User role enumeration for role-based access control."""
    GUEST = "guest"
    CUSTOMER = "customer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    """
    User model with comprehensive security features.

    Relationships:
    - One-to-many with Design (designs created by user)
    - One-to-many with Enquiry (enquiries submitted by user)
    - One-to-many with AdminLog (logs of admin actions by user)
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Email verification
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)

    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)

    # Refresh token (for token rotation)
    refresh_token_hash = Column(String(255), nullable=True)
    refresh_token_expires = Column(DateTime(timezone=True), nullable=True)

    # Profile
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    designs = relationship("Design", back_populates="user", cascade="all, delete-orphan")
    enquiries = relationship("Enquiry", back_populates="user", cascade="all, delete-orphan")
    admin_logs = relationship("AdminLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role={self.role})>"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    @property
    def is_super_admin(self) -> bool:
        """Check if user has super admin privileges."""
        return self.role == UserRole.SUPER_ADMIN

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return pwd_context.verify(password, self.password_hash)

    def set_refresh_token(self, token: str, expires_at) -> None:
        """Set and hash the refresh token."""
        self.refresh_token_hash = pwd_context.hash(token)
        self.refresh_token_expires = expires_at

    def verify_refresh_token(self, token: str) -> bool:
        """Verify a refresh token against the stored hash."""
        if not self.refresh_token_hash or not self.refresh_token_expires:
            return False
        return pwd_context.verify(token, self.refresh_token_hash)

    def clear_refresh_token(self) -> None:
        """Clear the refresh token (logout)."""
        self.refresh_token_hash = None
        self.refresh_token_expires = None

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user to dictionary representation."""
        user_dict = {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "phone": self.phone,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

        if include_sensitive and self.is_admin:
            # Include sensitive information only for admins
            user_dict.update({
                "email_verification_token": self.email_verification_token,
                "password_reset_token": self.password_reset_token,
            })

        return user_dict
