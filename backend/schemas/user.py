"""
User-related Pydantic schemas for Hublievents Backend API.
Handles user data validation and serialization.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration matching the model."""
    GUEST = "guest"
    CUSTOMER = "customer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$', max_length=20, description="User's phone number")
    role: UserRole = Field(default=UserRole.CUSTOMER, description="User's role in the system")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    is_verified: bool = Field(default=False, description="Whether the user's email is verified")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL to user's avatar image")
    bio: Optional[str] = Field(None, max_length=1000, description="User's biography")

    @validator('full_name')
    def validate_full_name(cls, v):
        """Ensure full name is properly formatted."""
        return ' '.join(v.split()).strip()


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=128, description="User's password")

    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password strength requirements."""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$', max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=1000)

    @validator('full_name')
    def validate_full_name(cls, v):
        """Ensure full name is properly formatted."""
        return ' '.join(v.split()).strip() if v else v


class UserResponse(UserBase):
    """Schema for user response data."""
    id: int = Field(..., description="User's unique identifier")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login requests."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class TokenResponse(BaseModel):
    """Schema for authentication token responses."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class TokenRefresh(BaseModel):
    """Schema for token refresh requests."""
    refresh_token: str = Field(..., description="JWT refresh token")


class PasswordResetRequest(BaseModel):
    """Schema for password reset requests."""
    email: EmailStr = Field(..., description="User's email address")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password strength requirements."""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class ChangePassword(BaseModel):
    """Schema for changing password when authenticated."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password strength requirements."""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserListResponse(BaseModel):
    """Schema for paginated user list responses."""
    users: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Users per page")
    pages: int = Field(..., description="Total number of pages")


class UserAdminUpdate(BaseModel):
    """Schema for admin user updates (includes sensitive fields)."""
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$', max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=1000)

    @validator('full_name')
    def validate_full_name(cls, v):
        """Ensure full name is properly formatted."""
        return ' '.join(v.split()).strip() if v else v
