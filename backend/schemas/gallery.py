"""
Gallery-related Pydantic schemas for Hublievents Backend API.
Handles image upload and gallery management validation and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class GalleryCategory(str, Enum):
    """Gallery category enumeration matching the model."""
    WEDDING = "wedding"
    BIRTHDAY = "birthday"
    CORPORATE = "corporate"
    FESTIVAL = "festival"
    DECORATION = "decoration"
    INSPIRATION = "inspiration"
    PORTFOLIO = "portfolio"


class GalleryImageBase(BaseModel):
    """Base gallery image schema with common fields."""
    title: Optional[str] = Field(None, max_length=255, description="Image title")
    description: Optional[str] = Field(None, max_length=1000, description="Image description")
    category: Optional[GalleryCategory] = Field(None, description="Image category")
    tags: Optional[List[str]] = Field(None, description="Image tags")
    is_featured: bool = Field(default=False, description="Whether image is featured")
    display_order: int = Field(default=0, ge=0, description="Display order for sorting")


class GalleryImageCreate(BaseModel):
    """Schema for creating a new gallery image."""
    title: Optional[str] = Field(None, max_length=255, description="Image title")
    description: Optional[str] = Field(None, max_length=1000, description="Image description")
    category: Optional[GalleryCategory] = Field(None, description="Image category")
    tags: Optional[List[str]] = Field(None, description="Image tags")
    is_public: bool = Field(default=True, description="Whether image is publicly visible")

    @validator('tags')
    def validate_tags(cls, v):
        """Validate and clean tags."""
        if v:
            # Remove duplicates and empty tags
            cleaned_tags = list(set(tag.strip().lower() for tag in v if tag.strip()))
            return cleaned_tags[:10]  # Limit to 10 tags
        return v


class GalleryImageUpdate(BaseModel):
    """Schema for updating gallery image information."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[GalleryCategory] = None
    tags: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)

    @validator('tags')
    def validate_tags(cls, v):
        """Validate and clean tags."""
        if v:
            # Remove duplicates and empty tags
            cleaned_tags = list(set(tag.strip().lower() for tag in v if tag.strip()))
            return cleaned_tags[:10]  # Limit to 10 tags
        return v


class GalleryImageResponse(GalleryImageBase):
    """Schema for gallery image response data."""
    id: int = Field(..., description="Image's unique identifier")
    filename: str = Field(..., description="Original filename")
    original_filename: str = Field(..., description="Original uploaded filename")
    url: str = Field(..., description="Image URL")
    file_size: int = Field(..., description="File size in bytes")
    file_size_mb: float = Field(..., description="File size in MB")
    mime_type: str = Field(..., description="MIME type")
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")
    aspect_ratio: Optional[float] = Field(None, description="Image aspect ratio")
    alt_text: str = Field(..., description="Alt text for accessibility")
    is_public: bool = Field(..., description="Whether image is publicly visible")
    is_approved: bool = Field(..., description="Whether image is approved for display")
    view_count: int = Field(..., description="Number of views")
    download_count: int = Field(..., description="Number of downloads")
    created_at: datetime = Field(..., description="Upload timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class GalleryImageAdminUpdate(BaseModel):
    """Schema for admin gallery image updates."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[GalleryCategory] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)

    @validator('tags')
    def validate_tags(cls, v):
        """Validate and clean tags."""
        if v:
            # Remove duplicates and empty tags
            cleaned_tags = list(set(tag.strip().lower() for tag in v if tag.strip()))
            return cleaned_tags[:10]  # Limit to 10 tags
        return v


class GalleryImageListResponse(BaseModel):
    """Schema for paginated gallery image list responses."""
    images: List[GalleryImageResponse] = Field(..., description="List of gallery images")
    total: int = Field(..., description="Total number of images")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Images per page")
    pages: int = Field(..., description="Total number of pages")


class GalleryImageUploadResponse(BaseModel):
    """Schema for image upload responses."""
    image: GalleryImageResponse = Field(..., description="Uploaded image data")
    upload_url: str = Field(..., description="URL for accessing the uploaded image")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL if generated")


class GalleryImageBulkAction(BaseModel):
    """Schema for bulk gallery image operations."""
    image_ids: List[int] = Field(..., min_items=1, max_items=100, description="List of image IDs")
    action: str = Field(..., pattern=r'^(delete|approve|feature|unfeature|categorize)$', description="Action to perform")
    category: Optional[GalleryCategory] = None
    tags: Optional[List[str]] = None


class GallerySearchFilters(BaseModel):
    """Schema for gallery image search and filtering."""
    query: Optional[str] = Field(None, max_length=255, description="Search query")
    category: Optional[GalleryCategory] = None
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_approved: Optional[bool] = None
    uploaded_by: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    min_width: Optional[int] = Field(None, ge=1)
    max_width: Optional[int] = Field(None, ge=1)
    min_height: Optional[int] = Field(None, ge=1)
    max_height: Optional[int] = Field(None, ge=1)


class GalleryStats(BaseModel):
    """Schema for gallery statistics."""
    total_images: int = Field(..., description="Total number of images")
    public_images: int = Field(..., description="Number of public images")
    featured_images: int = Field(..., description="Number of featured images")
    approved_images: int = Field(..., description="Number of approved images")
    pending_approval: int = Field(..., description="Number of images pending approval")
    total_file_size: int = Field(..., description="Total file size in bytes")
    total_file_size_gb: float = Field(..., description="Total file size in GB")
    images_by_category: Dict[str, int] = Field(..., description="Image count by category")


class GalleryImageMetadata(BaseModel):
    """Schema for image metadata extraction."""
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    format: str = Field(..., description="Image format (JPEG, PNG, etc.)")
    color_space: Optional[str] = Field(None, description="Color space information")
    has_alpha: bool = Field(..., description="Whether image has alpha channel")
    dpi: Optional[int] = Field(None, description="Image DPI")
    dominant_colors: Optional[List[str]] = Field(None, description="Dominant colors (hex codes)")


class GalleryUploadConfig(BaseModel):
    """Schema for upload configuration."""
    max_file_size: int = Field(..., description="Maximum file size in bytes")
    allowed_types: List[str] = Field(..., description="Allowed MIME types")
    max_width: Optional[int] = Field(None, description="Maximum image width")
    max_height: Optional[int] = Field(None, description="Maximum image height")
    generate_thumbnails: bool = Field(..., description="Whether to generate thumbnails")
    thumbnail_sizes: Optional[List[Dict[str, int]]] = Field(None, description="Thumbnail size configurations")
