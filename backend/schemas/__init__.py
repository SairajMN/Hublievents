"""
Pydantic schemas package for Hublievents Backend API.
All request/response schemas are imported here for easy access.
"""

from .user import (
    UserBase, UserCreate, UserUpdate, UserResponse,
    UserLogin, TokenResponse, TokenRefresh
)
from .design import (
    DesignBase, DesignCreate, DesignUpdate, DesignResponse,
    DesignShare, DesignClone
)
from .enquiry import (
    EnquiryBase, EnquiryCreate, EnquiryUpdate, EnquiryResponse,
    EnquiryAdminUpdate
)
from .gallery import (
    GalleryImageBase, GalleryImageCreate, GalleryImageUpdate,
    GalleryImageResponse, GalleryImageAdminUpdate
)
from .admin import (
    AdminStats, AdminLogResponse, AdminUserManagement
)

__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserResponse",
    "UserLogin", "TokenResponse", "TokenRefresh",

    # Design schemas
    "DesignBase", "DesignCreate", "DesignUpdate", "DesignResponse",
    "DesignShare", "DesignClone",

    # Enquiry schemas
    "EnquiryBase", "EnquiryCreate", "EnquiryUpdate", "EnquiryResponse",
    "EnquiryAdminUpdate",

    # Gallery schemas
    "GalleryImageBase", "GalleryImageCreate", "GalleryImageUpdate",
    "GalleryImageResponse", "GalleryImageAdminUpdate",

    # Admin schemas
    "AdminStats", "AdminLogResponse", "AdminUserManagement",
]
