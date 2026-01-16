"""
Admin-related Pydantic schemas for Hublievents Backend API.
Handles admin operations, statistics, and logging.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AdminAction(str, Enum):
    """Admin action enumeration matching the model."""
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


class AdminStats(BaseModel):
    """Schema for comprehensive admin dashboard statistics."""
    total_users: int = Field(..., description="Total number of registered users")
    active_users: int = Field(..., description="Number of active users")
    admin_users: int = Field(..., description="Number of admin users")
    total_designs: int = Field(..., description="Total number of designs")
    public_designs: int = Field(..., description="Number of public designs")
    booked_designs: int = Field(..., description="Number of booked designs")
    total_enquiries: int = Field(..., description="Total number of enquiries")
    pending_enquiries: int = Field(..., description="Number of pending enquiries")
    completed_enquiries: int = Field(..., description="Number of completed enquiries")
    total_gallery_images: int = Field(..., description="Total number of gallery images")
    approved_gallery_images: int = Field(..., description="Number of approved gallery images")
    pending_gallery_approvals: int = Field(..., description="Number of images pending approval")
    total_revenue: Optional[float] = Field(None, description="Total revenue from completed enquiries")
    monthly_revenue: Optional[float] = Field(None, description="Revenue for current month")
    recent_activities: List[Dict[str, Any]] = Field(..., description="Recent admin activities")
    system_health: Dict[str, Any] = Field(..., description="System health metrics")


class AdminLogResponse(BaseModel):
    """Schema for admin log entries."""
    id: int = Field(..., description="Log entry ID")
    admin_id: Optional[int] = Field(None, description="ID of admin who performed action")
    admin_email: Optional[str] = Field(None, description="Email of admin who performed action")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[int] = Field(None, description="ID of affected resource")
    changes: Optional[Dict[str, Any]] = Field(None, description="Changes made")
    notes: Optional[str] = Field(None, description="Admin notes")
    risk_level: str = Field(..., description="Risk level of action")
    ip_address: Optional[str] = Field(None, description="IP address of admin")
    user_agent: Optional[str] = Field(None, description="User agent string")
    created_at: datetime = Field(..., description="Timestamp of action")
    action_description: str = Field(..., description="Human-readable action description")
    is_high_risk: bool = Field(..., description="Whether action is high risk")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class AdminUserManagement(BaseModel):
    """Schema for admin user management operations."""
    user_id: int = Field(..., description="User ID to manage")
    action: str = Field(..., pattern=r'^(activate|deactivate|promote|demote|delete)$', description="Action to perform")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for action")


class AdminBulkAction(BaseModel):
    """Schema for bulk admin operations."""
    resource_type: str = Field(..., pattern=r'^(users|designs|enquiries|gallery_images)$', description="Type of resources")
    resource_ids: List[int] = Field(..., min_items=1, max_items=100, description="List of resource IDs")
    action: str = Field(..., description="Action to perform on resources")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters for action")


class AdminSystemConfig(BaseModel):
    """Schema for system configuration management."""
    setting_key: str = Field(..., min_length=1, max_length=255, description="Configuration key")
    setting_value: Any = Field(..., description="Configuration value")
    description: Optional[str] = Field(None, max_length=500, description="Setting description")
    is_sensitive: bool = Field(default=False, description="Whether setting contains sensitive data")


class AdminBackupRequest(BaseModel):
    """Schema for backup creation requests."""
    backup_type: str = Field(..., pattern=r'^(full|incremental|database_only)$', description="Type of backup")
    include_uploads: bool = Field(default=True, description="Include uploaded files in backup")
    compression_level: int = Field(default=6, ge=0, le=9, description="Compression level (0-9)")
    retention_days: int = Field(default=30, ge=1, description="Days to retain backup")


class AdminSecurityAlert(BaseModel):
    """Schema for security alerts."""
    alert_type: str = Field(..., description="Type of security alert")
    severity: str = Field(..., pattern=r'^(low|medium|high|critical)$', description="Alert severity")
    description: str = Field(..., description="Alert description")
    affected_resources: Optional[List[str]] = Field(None, description="Affected resources")
    recommended_actions: Optional[List[str]] = Field(None, description="Recommended actions")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="When alert was detected")


class AdminReportRequest(BaseModel):
    """Schema for generating admin reports."""
    report_type: str = Field(..., pattern=r'^(user_activity|enquiry_summary|revenue|gallery_stats|system_usage)$', description="Type of report")
    date_from: datetime = Field(..., description="Start date for report")
    date_to: datetime = Field(..., description="End date for report")
    format: str = Field(..., pattern=r'^(json|csv|pdf|excel)$', description="Report format")
    include_charts: bool = Field(default=False, description="Include charts in report")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")


class AdminNotificationSettings(BaseModel):
    """Schema for admin notification preferences."""
    email_notifications: bool = Field(default=True, description="Enable email notifications")
    enquiry_alerts: bool = Field(default=True, description="Alert for new enquiries")
    security_alerts: bool = Field(default=True, description="Alert for security events")
    system_alerts: bool = Field(default=True, description="Alert for system events")
    weekly_reports: bool = Field(default=True, description="Send weekly summary reports")
    notification_email: Optional[str] = Field(None, description="Email for notifications")


class AdminDashboardWidget(BaseModel):
    """Schema for dashboard widget configuration."""
    widget_id: str = Field(..., description="Unique widget identifier")
    widget_type: str = Field(..., pattern=r'^(chart|metric|table|list)$', description="Type of widget")
    title: str = Field(..., description="Widget title")
    position: Dict[str, int] = Field(..., description="Widget position (x, y, width, height)")
    config: Dict[str, Any] = Field(..., description="Widget-specific configuration")
    is_visible: bool = Field(default=True, description="Whether widget is visible")


class AdminAuditLogFilters(BaseModel):
    """Schema for filtering audit logs."""
    admin_id: Optional[int] = None
    action: Optional[AdminAction] = None
    resource_type: Optional[str] = None
    risk_level: Optional[str] = Field(None, pattern=r'^(low|medium|high|critical)$')
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    ip_address: Optional[str] = None
