"""
Design model for Hublievents Backend API.
Manages design customizations with versioning and validation.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database import Base


class DesignStatus(str, enum.Enum):
    """Design status enumeration."""
    DRAFT = "draft"
    SAVED = "saved"
    SHARED = "shared"
    BOOKED = "booked"  # Immutable once booked
    ARCHIVED = "archived"


class Design(Base):
    """
    Design model for storing customization data.

    Relationships:
    - Many-to-one with User (user who created the design)
    - One-to-many with Enquiry (enquiries that reference this design)
    """

    __tablename__ = "designs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Design metadata
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(DesignStatus), default=DesignStatus.DRAFT, nullable=False)

    # Design data (stored as JSON)
    design_data = Column(JSON, nullable=False)  # Complete design configuration

    # Versioning (for tracking changes)
    version = Column(Integer, default=1, nullable=False)
    parent_design_id = Column(Integer, ForeignKey("designs.id"), nullable=True)  # For cloned designs

    # Sharing
    share_token = Column(String(255), unique=True, nullable=True, index=True)
    share_expires = Column(DateTime(timezone=True), nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)

    # Constraints
    is_locked = Column(Boolean, default=False, nullable=False)  # Prevent further edits

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    booked_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="designs")
    enquiries = relationship("Enquiry", back_populates="design")

    # Self-referential relationship for cloning
    parent_design = relationship("Design", remote_side=[id], backref="cloned_designs")

    def __repr__(self):
        return f"<Design(id={self.id}, title='{self.title}', status={self.status}, user_id={self.user_id})>"

    @property
    def is_booked(self) -> bool:
        """Check if design is booked (immutable)."""
        return self.status == DesignStatus.BOOKED

    @property
    def can_edit(self) -> bool:
        """Check if design can still be edited."""
        return not self.is_locked and self.status != DesignStatus.BOOKED

    @property
    def share_url(self) -> str:
        """Generate share URL if design is shareable."""
        if self.share_token:
            return f"/share/design/{self.share_token}"
        return None

    def lock_design(self) -> None:
        """Lock design to prevent further edits."""
        self.is_locked = True

    def mark_as_booked(self) -> None:
        """Mark design as booked (makes it immutable)."""
        self.status = DesignStatus.BOOKED
        self.is_locked = True
        self.booked_at = func.now()

    def create_new_version(self, new_data: dict) -> 'Design':
        """Create a new version of this design."""
        new_design = Design(
            user_id=self.user_id,
            title=self.title,
            description=self.description,
            design_data=new_data,
            version=self.version + 1,
            parent_design_id=self.id
        )
        return new_design

    def generate_share_token(self) -> str:
        """Generate a unique share token."""
        import secrets
        self.share_token = secrets.token_urlsafe(32)
        return self.share_token

    def clone_for_user(self, new_user_id: int, new_title: str = None) -> 'Design':
        """Clone this design for another user."""
        cloned_design = Design(
            user_id=new_user_id,
            title=new_title or f"Copy of {self.title}",
            description=self.description,
            design_data=self.design_data.copy(),  # Deep copy of design data
            parent_design_id=self.id
        )
        return cloned_design

    def to_dict(self, include_data: bool = True) -> dict:
        """Convert design to dictionary representation."""
        design_dict = {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "version": self.version,
            "is_locked": self.is_locked,
            "is_public": self.is_public,
            "share_url": self.share_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "booked_at": self.booked_at.isoformat() if self.booked_at else None,
        }

        if include_data:
            design_dict["design_data"] = self.design_data

        return design_dict

    def validate_design_data(self) -> bool:
        """
        Validate design data structure.
        Add more validation logic as needed based on design schema.
        """
        if not isinstance(self.design_data, dict):
            return False

        # Basic validation - ensure required top-level keys exist
        required_keys = ["canvas", "elements"]  # Adjust based on your design structure
        for key in required_keys:
            if key not in self.design_data:
                return False

        return True
