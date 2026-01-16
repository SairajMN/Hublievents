"""
Gallery model for Hublievents Backend API.
Manages image uploads, categorization, and metadata.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import os
from database import Base
from config import settings


class GalleryCategory(str, enum.Enum):
    """Gallery image categories."""
    WEDDING = "wedding"
    BIRTHDAY = "birthday"
    CORPORATE = "corporate"
    FESTIVAL = "festival"
    DECORATION = "decoration"
    INSPIRATION = "inspiration"
    PORTFOLIO = "portfolio"


class GalleryImage(Base):
    """
    Gallery image model for storing uploaded images and metadata.

    Relationships:
    - Many-to-one with User (user who uploaded the image, if applicable)
    """

    __tablename__ = "gallery_images"

    id = Column(Integer, primary_key=True, index=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Relative path from uploads directory
    file_size = Column(Integer, nullable=False)     # Size in bytes

    # Image metadata
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=False)
    alt_text = Column(String(255), nullable=True)

    # Content information
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(Enum(GalleryCategory), nullable=True)

    # Tags and search
    tags = Column(JSON, nullable=True)  # Array of tags as JSON

    # Visibility and status
    is_public = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)

    # Admin controls
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Statistics
    view_count = Column(Integer, default=0, nullable=False)
    download_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    uploader = relationship("User", foreign_keys=[uploaded_by])
    approver = relationship("User", foreign_keys=[approved_by])

    def __repr__(self):
        return f"<GalleryImage(id={self.id}, filename='{self.filename}', category={self.category})>"

    @property
    def full_path(self) -> str:
        """Get the full file system path."""
        return os.path.join(settings.UPLOAD_PATH, self.file_path)

    @property
    def url_path(self) -> str:
        """Get the URL path for accessing the image."""
        return f"/uploads/{self.file_path}"

    @property
    def file_size_mb(self) -> float:
        """Get file size in MB."""
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def aspect_ratio(self) -> float:
        """Calculate aspect ratio (width/height)."""
        if self.width and self.height and self.height > 0:
            return round(self.width / self.height, 2)
        return None

    @property
    def is_image(self) -> bool:
        """Check if file is an image based on MIME type."""
        return self.mime_type.startswith("image/")

    @property
    def is_approved(self) -> bool:
        """Check if image is approved for display."""
        return self.approved_by is not None and self.approved_at is not None

    def approve(self, admin_id: int) -> None:
        """Approve image for public display."""
        self.approved_by = admin_id
        self.approved_at = func.now()
        self.is_public = True

    def increment_views(self) -> None:
        """Increment view count."""
        self.view_count += 1

    def increment_downloads(self) -> None:
        """Increment download count."""
        self.download_count += 1

    def add_tag(self, tag: str) -> None:
        """Add a tag to the image."""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the image."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)

    def generate_alt_text(self) -> str:
        """Generate alt text based on title, description, and category."""
        alt_parts = []
        if self.title:
            alt_parts.append(self.title)
        if self.category:
            alt_parts.append(f"{self.category.value} design")
        if self.description:
            # Take first 50 characters of description
            alt_parts.append(self.description[:50].rstrip() + "..." if len(self.description) > 50 else self.description)

        return " - ".join(alt_parts) if alt_parts else f"Gallery image {self.filename}"

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for secure storage."""
        import re
        from unicodedata import normalize

        # Normalize unicode characters
        filename = normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')

        # Remove or replace problematic characters
        filename = re.sub(r'[^\w\.-]', '_', filename)

        # Ensure it doesn't start or end with dots or spaces
        filename = filename.strip('._')

        # Limit length
        name, ext = os.path.splitext(filename)
        if len(filename) > 255:
            filename = name[:255-len(ext)] + ext

        return filename

    def to_dict(self, include_stats: bool = False) -> dict:
        """Convert image to dictionary representation."""
        image_dict = {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "url": self.url_path,
            "file_size": self.file_size,
            "file_size_mb": self.file_size_mb,
            "mime_type": self.mime_type,
            "width": self.width,
            "height": self.height,
            "aspect_ratio": self.aspect_ratio,
            "alt_text": self.alt_text or self.generate_alt_text(),
            "title": self.title,
            "description": self.description,
            "category": self.category.value if self.category else None,
            "tags": self.tags or [],
            "is_public": self.is_public,
            "is_featured": self.is_featured,
            "display_order": self.display_order,
            "is_approved": self.is_approved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_stats:
            image_dict.update({
                "view_count": self.view_count,
                "download_count": self.download_count,
                "uploaded_by": self.uploaded_by,
                "approved_by": self.approved_by,
                "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            })

        return image_dict

    @classmethod
    def get_featured_images(cls, limit: int = 10):
        """Get featured images ordered by display order."""
        # This would be used in queries, not implemented as instance method
        pass

    @classmethod
    def get_by_category(cls, category: GalleryCategory, public_only: bool = True):
        """Get images by category."""
        # This would be used in queries, not implemented as instance method
        pass
