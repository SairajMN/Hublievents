"""
Enquiry-related Pydantic schemas for Hublievents Backend API.
Handles customer enquiry data validation and serialization.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class EnquiryStatus(str, Enum):
    """Enquiry status enumeration matching the model."""
    PENDING = "pending"
    REVIEWED = "reviewed"
    CONTACTED = "contacted"
    QUOTED = "quoted"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EnquiryPriority(str, Enum):
    """Enquiry priority enumeration matching the model."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EnquiryBase(BaseModel):
    """Base enquiry schema with common fields."""
    event_type: str = Field(..., min_length=1, max_length=255, description="Type of event (Wedding, Birthday, etc.)")
    event_date: datetime = Field(..., description="Date and time of the event")
    guest_count: Optional[int] = Field(None, ge=1, le=10000, description="Number of expected guests")
    budget_range: Optional[str] = Field(None, max_length=100, description="Budget range (e.g., '50k-1L')")
    contact_name: str = Field(..., min_length=1, max_length=255, description="Contact person's full name")
    contact_email: EmailStr = Field(..., description="Contact email address")
    contact_phone: str = Field(..., pattern=r'^\+?[\d\s\-\(\)]+$', max_length=20, description="Contact phone number")
    venue_name: Optional[str] = Field(None, max_length=255, description="Venue name")
    venue_address: Optional[str] = Field(None, max_length=1000, description="Venue address")
    city: Optional[str] = Field(None, max_length=255, description="City")
    state: Optional[str] = Field(None, max_length=255, description="State")
    message: str = Field(..., min_length=10, max_length=5000, description="Enquiry message/details")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Additional requirements as JSON")
    priority: EnquiryPriority = Field(default=EnquiryPriority.MEDIUM, description="Enquiry priority level")

    @validator('event_date')
    def validate_event_date(cls, v):
        """Ensure event date is in the future."""
        if v <= datetime.now(v.tzinfo or datetime.timezone.utc):
            raise ValueError('Event date must be in the future')
        return v

    @validator('contact_name')
    def validate_contact_name(cls, v):
        """Ensure contact name is properly formatted."""
        return ' '.join(v.split()).strip()


class EnquiryCreate(EnquiryBase):
    """Schema for creating a new enquiry."""
    design_id: Optional[int] = Field(None, description="ID of attached design (optional)")


class EnquiryUpdate(BaseModel):
    """Schema for updating enquiry information."""
    event_type: Optional[str] = Field(None, min_length=1, max_length=255)
    event_date: Optional[datetime] = None
    guest_count: Optional[int] = Field(None, ge=1, le=10000)
    budget_range: Optional[str] = Field(None, max_length=100)
    contact_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$', max_length=20)
    venue_name: Optional[str] = Field(None, max_length=255)
    venue_address: Optional[str] = Field(None, max_length=1000)
    city: Optional[str] = Field(None, max_length=255)
    state: Optional[str] = Field(None, max_length=255)
    message: Optional[str] = Field(None, min_length=10, max_length=5000)
    requirements: Optional[Dict[str, Any]] = None
    priority: Optional[EnquiryPriority] = None

    @validator('event_date')
    def validate_event_date(cls, v):
        """Ensure event date is in the future."""
        if v and v <= datetime.now(v.tzinfo or datetime.timezone.utc):
            raise ValueError('Event date must be in the future')
        return v

    @validator('contact_name')
    def validate_contact_name(cls, v):
        """Ensure contact name is properly formatted."""
        return ' '.join(v.split()).strip() if v else v


class EnquiryResponse(EnquiryBase):
    """Schema for enquiry response data."""
    id: int = Field(..., description="Enquiry's unique identifier")
    user_id: int = Field(..., description="ID of the user who submitted the enquiry")
    design_id: Optional[int] = Field(None, description="ID of attached design")
    status: EnquiryStatus = Field(..., description="Current enquiry status")
    assigned_admin_id: Optional[int] = Field(None, description="ID of assigned admin")
    email_sent: bool = Field(..., description="Whether email notification was sent")
    whatsapp_sent: bool = Field(..., description="Whether WhatsApp notification was sent")
    last_contacted: Optional[datetime] = Field(None, description="Last contact timestamp")
    estimated_amount: Optional[int] = Field(None, description="Estimated amount in rupees")
    final_amount: Optional[int] = Field(None, description="Final amount in rupees")
    created_at: datetime = Field(..., description="Enquiry creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    days_until_event: Optional[int] = Field(None, description="Days until event")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class EnquiryAdminUpdate(BaseModel):
    """Schema for admin enquiry updates."""
    status: Optional[EnquiryStatus] = None
    priority: Optional[EnquiryPriority] = None
    assigned_admin_id: Optional[int] = None
    admin_notes: Optional[str] = Field(None, max_length=5000, description="Admin notes")
    estimated_amount: Optional[int] = Field(None, ge=0, description="Estimated amount in rupees")
    final_amount: Optional[int] = Field(None, ge=0, description="Final amount in rupees")

    @validator('final_amount')
    def validate_final_amount(cls, v, values):
        """Ensure final amount is not less than estimated amount."""
        if v and values.get('estimated_amount') and v < values['estimated_amount']:
            raise ValueError('Final amount cannot be less than estimated amount')
        return v


class EnquiryListResponse(BaseModel):
    """Schema for paginated enquiry list responses."""
    enquiries: List[EnquiryResponse] = Field(..., description="List of enquiries")
    total: int = Field(..., description="Total number of enquiries")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Enquiries per page")
    pages: int = Field(..., description="Total number of pages")


class EnquiryStats(BaseModel):
    """Schema for enquiry statistics."""
    total_enquiries: int = Field(..., description="Total number of enquiries")
    pending_enquiries: int = Field(..., description="Number of pending enquiries")
    reviewed_enquiries: int = Field(..., description="Number of reviewed enquiries")
    contacted_enquiries: int = Field(..., description="Number of contacted enquiries")
    quoted_enquiries: int = Field(..., description="Number of quoted enquiries")
    confirmed_enquiries: int = Field(..., description="Number of confirmed enquiries")
    completed_enquiries: int = Field(..., description="Number of completed enquiries")
    cancelled_enquiries: int = Field(..., description="Number of cancelled enquiries")


class EnquiryCommunicationLog(BaseModel):
    """Schema for enquiry communication tracking."""
    enquiry_id: int = Field(..., description="Enquiry ID")
    method: str = Field(..., pattern=r'^(email|whatsapp|phone|in_person)$', description="Communication method")
    direction: str = Field(..., pattern=r'^(outbound|inbound)$', description="Communication direction")
    notes: Optional[str] = Field(None, max_length=1000, description="Communication notes")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Communication timestamp")


class EnquiryBulkAction(BaseModel):
    """Schema for bulk enquiry operations."""
    enquiry_ids: List[int] = Field(..., min_items=1, max_items=100, description="List of enquiry IDs")
    action: str = Field(..., pattern=r'^(assign_admin|change_status|change_priority|delete)$', description="Action to perform")
    admin_id: Optional[int] = Field(None, description="Admin ID for assignment")
    status: Optional[EnquiryStatus] = None
    priority: Optional[EnquiryPriority] = None


class EnquirySearchFilters(BaseModel):
    """Schema for enquiry search and filtering."""
    query: Optional[str] = Field(None, max_length=255, description="Search query")
    status: Optional[EnquiryStatus] = None
    priority: Optional[EnquiryPriority] = None
    event_type: Optional[str] = Field(None, max_length=255)
    assigned_admin_id: Optional[int] = None
    user_id: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    event_date_after: Optional[datetime] = None
    event_date_before: Optional[datetime] = None
    has_design: Optional[bool] = Field(None, description="Filter enquiries with/without designs")


class EnquiryTimelineEvent(BaseModel):
    """Schema for enquiry timeline events."""
    event_type: str = Field(..., description="Type of timeline event")
    description: str = Field(..., description="Event description")
    timestamp: datetime = Field(..., description="Event timestamp")
    user_id: Optional[int] = Field(None, description="User who triggered the event")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional event metadata")


class EnquiryTimelineResponse(BaseModel):
    """Schema for enquiry timeline responses."""
    enquiry_id: int = Field(..., description="Enquiry ID")
    timeline: List[EnquiryTimelineEvent] = Field(..., description="List of timeline events")


class EnquiryExportData(BaseModel):
    """Schema for enquiry export data."""
    format: str = Field(..., pattern=r'^(csv|excel|pdf)$', description="Export format")
    include_admin_notes: bool = Field(default=False, description="Include admin notes in export")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range for export")
    filters: Optional[EnquirySearchFilters] = None
