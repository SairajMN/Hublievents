"""
Admin log model for Hublievents Backend API.
Comprehensive audit logging for all admin actions.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database import Base


class AdminAction(str, enum.Enum):
    """Types of admin actions that can be logged."""
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ROLE_CHANGED = "user_role_changed"
    USER_BANNED = "user_banned"
    USER_UNBANNED = "user_unbanned"

    DESIGN_APPROVED = "design_approved"
    DESIGN_REJECTED = "design_rejected"
    DESIGN_DELETED = "design_deleted"

    ENQUIRY_ASSIGNED = "enquiry_assigned"
    ENQUIRY_STATUS_CHANGED = "enquiry_status_changed"
    ENQUIRY_UPDATED = "enquiry_updated"
    ENQUIRY_DELETED = "enquiry_deleted"

    GALLERY_IMAGE_UPLOADED = "gallery_image_uploaded"
    GALLERY_IMAGE_APPROVED = "gallery_image_approved"
    GALLERY_IMAGE_REJECTED = "gallery_image_rejected"
    GALLERY_IMAGE_DELETED = "gallery_image_deleted"

    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    BACKUP_CREATED = "backup_created"
    LOGIN_ATTEMPT = "login_attempt"
    SECURITY_ALERT = "security_alert"


class AdminLog(Base):
    """
    Admin log model for comprehensive audit logging.

    Relationships:
    - Many-to-one with User (admin who performed the action)
    """

    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Action details
    action = Column(Enum(AdminAction), nullable=False)
    resource_type = Column(String(50), nullable=False)  # e.g., "user", "design", "enquiry"
    resource_id = Column(Integer, nullable=True)       # ID of the affected resource

    # Change details
    old_values = Column(JSON, nullable=True)  # Previous state as JSON
    new_values = Column(JSON, nullable=True)  # New state as JSON
    changes = Column(JSON, nullable=True)     # Specific changes made

    # Context
    ip_address = Column(String(45), nullable=True)     # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)

    # Additional information
    notes = Column(Text, nullable=True)       # Admin notes about the action
    action_metadata = Column(JSON, nullable=True)    # Additional structured data

    # Risk assessment
    risk_level = Column(String(20), default="low", nullable=False)  # low, medium, high, critical

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    admin = relationship("User", back_populates="admin_logs")

    def __repr__(self):
        return f"<AdminLog(id={self.id}, action={self.action}, admin_id={self.admin_id}, resource_type='{self.resource_type}')>"

    @property
    def is_high_risk(self) -> bool:
        """Check if this action is considered high risk."""
        high_risk_actions = [
            AdminAction.USER_DELETED,
            AdminAction.USER_ROLE_CHANGED,
            AdminAction.SYSTEM_CONFIG_CHANGED,
            AdminAction.SECURITY_ALERT,
        ]
        return self.action in high_risk_actions or self.risk_level in ["high", "critical"]

    def get_action_description(self) -> str:
        """Get a human-readable description of the action."""
        descriptions = {
            AdminAction.USER_CREATED: "Created new user",
            AdminAction.USER_UPDATED: "Updated user information",
            AdminAction.USER_DELETED: "Deleted user account",
            AdminAction.USER_ROLE_CHANGED: "Changed user role",
            AdminAction.USER_BANNED: "Banned user account",
            AdminAction.USER_UNBANNED: "Unbanned user account",
            AdminAction.DESIGN_APPROVED: "Approved design",
            AdminAction.DESIGN_REJECTED: "Rejected design",
            AdminAction.DESIGN_DELETED: "Deleted design",
            AdminAction.ENQUIRY_ASSIGNED: "Assigned enquiry to admin",
            AdminAction.ENQUIRY_STATUS_CHANGED: "Changed enquiry status",
            AdminAction.ENQUIRY_UPDATED: "Updated enquiry details",
            AdminAction.ENQUIRY_DELETED: "Deleted enquiry",
            AdminAction.GALLERY_IMAGE_UPLOADED: "Uploaded gallery image",
            AdminAction.GALLERY_IMAGE_APPROVED: "Approved gallery image",
            AdminAction.GALLERY_IMAGE_REJECTED: "Rejected gallery image",
            AdminAction.GALLERY_IMAGE_DELETED: "Deleted gallery image",
            AdminAction.SYSTEM_CONFIG_CHANGED: "Changed system configuration",
            AdminAction.BACKUP_CREATED: "Created system backup",
            AdminAction.LOGIN_ATTEMPT: "Admin login attempt",
            AdminAction.SECURITY_ALERT: "Security alert triggered",
        }
        return descriptions.get(self.action, f"Performed {self.action.value}")

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert log entry to dictionary representation."""
        log_dict = {
            "id": self.id,
            "admin_id": self.admin_id,
            "action": self.action.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "changes": self.changes,
            "notes": self.notes,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "action_description": self.get_action_description(),
            "is_high_risk": self.is_high_risk,
        }

        if include_sensitive:
            log_dict.update({
                "old_values": self.old_values,
                "new_values": self.new_values,
                "ip_address": self.ip_address,
                "user_agent": self.user_agent,
                "session_id": self.session_id,
                "action_metadata": self.action_metadata,
            })

        return log_dict

    @classmethod
    def log_action(cls, db, admin_id: int, action: AdminAction, resource_type: str,
                   resource_id: int = None, old_values: dict = None, new_values: dict = None,
                   changes: dict = None, notes: str = None, metadata: dict = None,
                   ip_address: str = None, user_agent: str = None, session_id: str = None):
        """
        Class method to create and save a log entry.

        Args:
            db: Database session
            admin_id: ID of the admin performing the action
            action: The action being performed
            resource_type: Type of resource affected
            resource_id: ID of the affected resource (optional)
            old_values: Previous state of the resource (optional)
            new_values: New state of the resource (optional)
            changes: Specific changes made (optional)
            notes: Additional notes (optional)
            metadata: Additional structured data (optional)
            ip_address: IP address of the admin (optional)
            user_agent: User agent string (optional)
            session_id: Session ID (optional)
        """

        # Determine risk level based on action
        risk_levels = {
            "low": [AdminAction.GALLERY_IMAGE_UPLOADED, AdminAction.LOGIN_ATTEMPT],
            "medium": [AdminAction.USER_UPDATED, AdminAction.ENQUIRY_STATUS_CHANGED,
                      AdminAction.GALLERY_IMAGE_APPROVED],
            "high": [AdminAction.USER_DELETED, AdminAction.USER_BANNED,
                    AdminAction.DESIGN_DELETED, AdminAction.ENQUIRY_DELETED],
            "critical": [AdminAction.USER_ROLE_CHANGED, AdminAction.SYSTEM_CONFIG_CHANGED,
                        AdminAction.SECURITY_ALERT],
        }

        risk_level = "medium"  # default
        for level, actions in risk_levels.items():
            if action in actions:
                risk_level = level
                break

        log_entry = cls(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            notes=notes,
            action_metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            risk_level=risk_level,
        )

        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

        return log_entry
