"""
Enquiry model for Hublievents Backend API.
Manages customer enquiries with status tracking and admin notes.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database import Base


class EnquiryStatus(str, enum.Enum):
    """Enquiry status enumeration."""
    PENDING = "pending"
    REVIEWED = "reviewed"
    CONTACTED = "contacted"
    QUOTED = "quoted"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EnquiryPriority(str, enum.Enum):
    """Enquiry priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Enquiry(Base):
    """
    Enquiry model for customer inquiries and bookings.

    Relationships:
    - Many-to-one with User (user who submitted the enquiry)
    - Many-to-one with Design (design attached to the enquiry)
    - One-to-many with AdminLog (admin actions on this enquiry)
    """

    __tablename__ = "enquiries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    design_id = Column(Integer, ForeignKey("designs.id", ondelete="SET NULL"), nullable=True, index=True)

    # Enquiry details
    event_type = Column(String(255), nullable=False)  # Wedding, Birthday, Corporate, etc.
    event_date = Column(DateTime(timezone=True), nullable=False)
    guest_count = Column(Integer, nullable=True)
    budget_range = Column(String(100), nullable=True)  # e.g., "50k-1L", "1L-5L"

    # Contact information (may differ from user profile)
    contact_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(20), nullable=False)

    # Location
    venue_name = Column(String(255), nullable=True)
    venue_address = Column(Text, nullable=True)
    city = Column(String(255), nullable=True)
    state = Column(String(255), nullable=True)

    # Enquiry content
    message = Column(Text, nullable=False)
    requirements = Column(JSON, nullable=True)  # Additional requirements as JSON

    # Status and priority
    status = Column(Enum(EnquiryStatus), default=EnquiryStatus.PENDING, nullable=False)
    priority = Column(Enum(EnquiryPriority), default=EnquiryPriority.MEDIUM, nullable=False)

    # Admin handling
    assigned_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    admin_notes = Column(Text, nullable=True)

    # Communication tracking
    email_sent = Column(Boolean, default=False, nullable=False)
    whatsapp_sent = Column(Boolean, default=False, nullable=False)
    last_contacted = Column(DateTime(timezone=True), nullable=True)

    # Financial
    estimated_amount = Column(Integer, nullable=True)  # In rupees
    final_amount = Column(Integer, nullable=True)     # In rupees

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="enquiries", foreign_keys=[user_id])
    design = relationship("Design", back_populates="enquiries")
    assigned_admin = relationship("User", foreign_keys=[assigned_admin_id])

    def __repr__(self):
        return f"<Enquiry(id={self.id}, event_type='{self.event_type}', status={self.status}, user_id={self.user_id})>"

    @property
    def is_completed(self) -> bool:
        """Check if enquiry is completed."""
        return self.status == EnquiryStatus.COMPLETED

    @property
    def is_cancelled(self) -> bool:
        """Check if enquiry is cancelled."""
        return self.status == EnquiryStatus.CANCELLED

    @property
    def days_until_event(self) -> int:
        """Calculate days until the event date."""
        from datetime import datetime, timezone
        if not self.event_date:
            return None
        now = datetime.now(timezone.utc)
        delta = self.event_date - now
        return max(0, delta.days)

    def assign_admin(self, admin_id: int) -> None:
        """Assign an admin to handle this enquiry."""
        self.assigned_admin_id = admin_id

    def update_status(self, new_status: EnquiryStatus, admin_notes: str = None) -> None:
        """Update enquiry status with optional admin notes."""
        self.status = new_status
        if admin_notes:
            if self.admin_notes:
                self.admin_notes += f"\n\n[{func.now()}]: {admin_notes}"
            else:
                self.admin_notes = admin_notes

        if new_status == EnquiryStatus.COMPLETED:
            self.completed_at = func.now()

    def mark_contacted(self, method: str = "email") -> None:
        """Mark enquiry as contacted via specified method."""
        self.last_contacted = func.now()
        if method.lower() == "email":
            self.email_sent = True
        elif method.lower() == "whatsapp":
            self.whatsapp_sent = True

    def set_budget_range(self, min_budget: int, max_budget: int) -> None:
        """Set budget range in lakhs."""
        if min_budget >= 0 and max_budget > min_budget:
            self.budget_range = f"{min_budget}L-{max_budget}L"
        else:
            raise ValueError("Invalid budget range")

    def to_dict(self, include_admin_data: bool = False) -> dict:
        """Convert enquiry to dictionary representation."""
        enquiry_dict = {
            "id": self.id,
            "user_id": self.user_id,
            "design_id": self.design_id,
            "event_type": self.event_type,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "guest_count": self.guest_count,
            "budget_range": self.budget_range,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "venue_name": self.venue_name,
            "venue_address": self.venue_address,
            "city": self.city,
            "state": self.state,
            "message": self.message,
            "requirements": self.requirements,
            "status": self.status.value,
            "priority": self.priority.value,
            "email_sent": self.email_sent,
            "whatsapp_sent": self.whatsapp_sent,
            "last_contacted": self.last_contacted.isoformat() if self.last_contacted else None,
            "estimated_amount": self.estimated_amount,
            "final_amount": self.final_amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "days_until_event": self.days_until_event,
        }

        if include_admin_data:
            enquiry_dict.update({
                "assigned_admin_id": self.assigned_admin_id,
                "admin_notes": self.admin_notes,
            })

        return enquiry_dict

    def get_status_color(self) -> str:
        """Get color code for status display."""
        status_colors = {
            EnquiryStatus.PENDING: "#FFA500",    # Orange
            EnquiryStatus.REVIEWED: "#0000FF",   # Blue
            EnquiryStatus.CONTACTED: "#800080",  # Purple
            EnquiryStatus.QUOTED: "#008000",     # Green
            EnquiryStatus.CONFIRMED: "#006400",  # Dark Green
            EnquiryStatus.COMPLETED: "#228B22",  # Forest Green
            EnquiryStatus.CANCELLED: "#FF0000",  # Red
        }
        return status_colors.get(self.status, "#808080")  # Default gray
