"""
Design-related Pydantic schemas for Hublievents Backend API.
Handles design customization data validation and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class DesignStatus(str, Enum):
    """Design status enumeration matching the model."""
    DRAFT = "draft"
    SAVED = "saved"
    SHARED = "shared"
    BOOKED = "booked"
    ARCHIVED = "archived"


class DesignBase(BaseModel):
    """Base design schema with common fields."""
    title: str = Field(..., min_length=1, max_length=255, description="Design title")
    description: Optional[str] = Field(None, max_length=1000, description="Design description")
    status: DesignStatus = Field(default=DesignStatus.DRAFT, description="Design status")
    design_data: Dict[str, Any] = Field(..., description="Complete design configuration data")
    is_public: bool = Field(default=False, description="Whether design is publicly visible")

    @validator('design_data')
    def validate_design_data(cls, v):
        """Validate that design data is a proper dictionary."""
        if not isinstance(v, dict):
            raise ValueError('Design data must be a valid JSON object')

        # Basic validation - ensure required top-level keys exist
        required_keys = ["canvas", "elements"]
        for key in required_keys:
            if key not in v:
                raise ValueError(f'Design data must contain "{key}" key')

        return v


class DesignCreate(DesignBase):
    """Schema for creating a new design."""
    pass  # Inherits all fields from DesignBase


class DesignUpdate(BaseModel):
    """Schema for updating design information."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    design_data: Optional[Dict[str, Any]] = Field(None)
    is_public: Optional[bool] = None

    @validator('design_data')
    def validate_design_data(cls, v):
        """Validate that design data is a proper dictionary."""
        if v is not None and not isinstance(v, dict):
            raise ValueError('Design data must be a valid JSON object')

        # Basic validation if design_data is provided
        if v is not None:
            required_keys = ["canvas", "elements"]
            for key in required_keys:
                if key not in v:
                    raise ValueError(f'Design data must contain "{key}" key')

        return v


class DesignResponse(DesignBase):
    """Schema for design response data."""
    id: int = Field(..., description="Design's unique identifier")
    user_id: int = Field(..., description="ID of the user who created the design")
    version: int = Field(..., description="Design version number")
    parent_design_id: Optional[int] = Field(None, description="ID of parent design if cloned")
    share_token: Optional[str] = Field(None, description="Token for sharing design")
    share_expires: Optional[datetime] = Field(None, description="Share token expiration")
    is_locked: bool = Field(..., description="Whether design is locked for editing")
    created_at: datetime = Field(..., description="Design creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    booked_at: Optional[datetime] = Field(None, description="When design was booked")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class DesignShare(BaseModel):
    """Schema for sharing a design."""
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Days until share expires")


class DesignClone(BaseModel):
    """Schema for cloning a design."""
    title: str = Field(..., min_length=1, max_length=255, description="Title for the cloned design")
    description: Optional[str] = Field(None, max_length=1000, description="Description for the cloned design")


class DesignVersionResponse(BaseModel):
    """Schema for design version information."""
    version: int = Field(..., description="Version number")
    created_at: datetime = Field(..., description="When this version was created")
    changes_summary: Optional[str] = Field(None, description="Summary of changes in this version")


class DesignListResponse(BaseModel):
    """Schema for paginated design list responses."""
    designs: List[DesignResponse] = Field(..., description="List of designs")
    total: int = Field(..., description="Total number of designs")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Designs per page")
    pages: int = Field(..., description="Total number of pages")


class DesignStats(BaseModel):
    """Schema for design statistics."""
    total_designs: int = Field(..., description="Total number of designs")
    draft_designs: int = Field(..., description="Number of draft designs")
    saved_designs: int = Field(..., description="Number of saved designs")
    shared_designs: int = Field(..., description="Number of shared designs")
    booked_designs: int = Field(..., description="Number of booked designs")
    public_designs: int = Field(..., description="Number of public designs")


class DesignValidationError(BaseModel):
    """Schema for design validation errors."""
    field: str = Field(..., description="Field that failed validation")
    error: str = Field(..., description="Error message")
    value: Optional[Any] = Field(None, description="Invalid value")


class DesignValidationResponse(BaseModel):
    """Schema for design validation responses."""
    is_valid: bool = Field(..., description="Whether the design is valid")
    errors: List[DesignValidationError] = Field(default_factory=list, description="List of validation errors")


class PublicDesignResponse(BaseModel):
    """Schema for public design sharing (limited information)."""
    id: int = Field(..., description="Design's unique identifier")
    title: str = Field(..., description="Design title")
    description: Optional[str] = Field(None, description="Design description")
    design_data: Dict[str, Any] = Field(..., description="Design configuration (read-only)")
    created_at: datetime = Field(..., description="Design creation timestamp")
    share_token: str = Field(..., description="Share token used to access this design")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class DesignBulkAction(BaseModel):
    """Schema for bulk design operations."""
    design_ids: List[int] = Field(..., min_items=1, max_items=100, description="List of design IDs")
    action: str = Field(..., pattern=r'^(delete|archive|share|unshare)$', description="Action to perform")


class DesignSearchFilters(BaseModel):
    """Schema for design search and filtering."""
    query: Optional[str] = Field(None, max_length=255, description="Search query")
    status: Optional[DesignStatus] = None
    is_public: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    user_id: Optional[int] = None  # For admin searches
