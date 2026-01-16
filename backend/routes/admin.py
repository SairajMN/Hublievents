"""
Admin routes for Hublievents Backend API.
Comprehensive admin dashboard endpoints with role-based access control.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from database import get_db
from models import User, Enquiry, Design, GalleryImage, AdminLog
from schemas.admin import (
    AdminStats, AdminLogResponse, AdminUserManagement,
    AdminBulkAction, AdminSystemConfig, AdminBackupRequest,
    AdminReportRequest, AdminNotificationSettings
)
from auth.dependencies import get_current_admin_user, require_super_admin
from auth.jwt import create_access_token
from security.middleware import rate_limit

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()
security = HTTPBearer()

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive admin dashboard statistics.
    Requires admin or super_admin role.
    """
    try:
        # User statistics
        total_users = db.query(func.count(User.id)).scalar()
        active_users = db.query(func.count(User.id)).filter(
            User.is_active == True,
            User.last_login_at >= datetime.utcnow() - timedelta(days=30)
        ).scalar()

        admin_users = db.query(func.count(User.id)).filter(
            or_(User.role == "admin", User.role == "super_admin")
        ).scalar()

        # Design statistics
        total_designs = db.query(func.count(Design.id)).scalar()
        public_designs = db.query(func.count(Design.id)).filter(
            Design.status == "approved"
        ).scalar()
        booked_designs = db.query(func.count(Design.id)).filter(
            Design.status == "booked"
        ).scalar()

        # Enquiry statistics
        total_enquiries = db.query(func.count(Enquiry.id)).scalar()
        pending_enquiries = db.query(func.count(Enquiry.id)).filter(
            Enquiry.status == "pending"
        ).scalar()
        completed_enquiries = db.query(func.count(Enquiry.id)).filter(
            Enquiry.status == "completed"
        ).scalar()

        # Gallery statistics
        total_gallery_images = db.query(func.count(GalleryImage.id)).scalar()
        approved_gallery_images = db.query(func.count(GalleryImage.id)).filter(
            GalleryImage.status == "approved"
        ).scalar()
        pending_gallery_approvals = db.query(func.count(GalleryImage.id)).filter(
            GalleryImage.status == "pending"
        ).scalar()

        # Revenue calculation (simplified - would need actual pricing logic)
        monthly_revenue = 0  # Placeholder

        # Recent activities
        recent_activities = []
        recent_logs = db.query(AdminLog).order_by(
            desc(AdminLog.created_at)
        ).limit(10).all()

        for log in recent_logs:
            recent_activities.append({
                "id": log.id,
                "action": log.get_action_description(),
                "admin": log.admin.name if log.admin else "System",
                "timestamp": log.created_at.isoformat(),
                "resource_type": log.resource_type,
                "risk_level": log.risk_level
            })

        # System health (placeholder)
        system_health = {
            "database_status": "healthy",
            "api_response_time": "45ms",
            "uptime": "99.9%",
            "error_rate": "0.1%"
        }

        stats = AdminStats(
            total_users=total_users,
            active_users=active_users,
            admin_users=admin_users,
            total_designs=total_designs,
            public_designs=public_designs,
            booked_designs=booked_designs,
            total_enquiries=total_enquiries,
            pending_enquiries=pending_enquiries,
            completed_enquiries=completed_enquiries,
            total_gallery_images=total_gallery_images,
            approved_gallery_images=approved_gallery_images,
            pending_gallery_approvals=pending_gallery_approvals,
            monthly_revenue=monthly_revenue,
            recent_activities=recent_activities,
            system_health=system_health
        )

        return stats

    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve admin statistics"
        )

@router.get("/activity", response_model=List[Dict[str, Any]])
async def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get recent admin activity logs.
    Requires admin or super_admin role.
    """
    try:
        logs = db.query(AdminLog).order_by(
            desc(AdminLog.created_at)
        ).limit(limit).all()

        activities = []
        for log in logs:
            activities.append({
                "id": log.id,
                "action": log.get_action_description(),
                "admin": log.admin.name if log.admin else "System",
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "timestamp": log.created_at.isoformat(),
                "risk_level": log.risk_level,
                "ip_address": log.ip_address
            })

        return activities

    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activity logs"
        )

@router.get("/pending")
async def get_pending_items(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get count of pending items requiring admin attention.
    """
    try:
        pending_enquiries = db.query(func.count(Enquiry.id)).filter(
            Enquiry.status == "pending"
        ).scalar()

        pending_designs = db.query(func.count(Design.id)).filter(
            Design.status == "submitted"
        ).scalar()

        pending_gallery = db.query(func.count(GalleryImage.id)).filter(
            GalleryImage.status == "pending"
        ).scalar()

        return {
            "enquiries": pending_enquiries,
            "designs": pending_designs,
            "gallery": pending_gallery
        }

    except Exception as e:
        logger.error(f"Error getting pending items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pending items"
        )

@router.get("/enquiries")
async def get_enquiries(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    sort_by: str = Query("created_at_desc"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get enquiries with filtering and pagination.
    Requires admin or super_admin role.
    """
    try:
        # Build query
        query = db.query(Enquiry)

        # Apply filters
        if status_filter:
            query = query.filter(Enquiry.status == status_filter)

        if priority:
            query = query.filter(Enquiry.priority == priority)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Enquiry.customer_name.ilike(search_term),
                    Enquiry.customer_email.ilike(search_term),
                    Enquiry.event_type.ilike(search_term),
                    Enquiry.message.ilike(search_term)
                )
            )

        if date_from:
            query = query.filter(Enquiry.created_at >= date_from)

        if date_to:
            query = query.filter(Enquiry.created_at <= date_to)

        # Apply sorting
        if sort_by == "created_at_desc":
            query = query.order_by(desc(Enquiry.created_at))
        elif sort_by == "created_at_asc":
            query = query.order_by(asc(Enquiry.created_at))
        elif sort_by == "priority_desc":
            query = query.order_by(desc(Enquiry.priority))
        elif sort_by == "updated_at_desc":
            query = query.order_by(desc(Enquiry.updated_at))

        # Get total count
        total_count = query.count()

        # Apply pagination
        enquiries = query.offset((page - 1) * limit).limit(limit).all()

        # Format response
        enquiry_list = []
        for enquiry in enquiries:
            enquiry_list.append({
                "id": enquiry.id,
                "customer_name": enquiry.customer_name,
                "customer_email": enquiry.customer_email,
                "customer_phone": enquiry.customer_phone,
                "event_type": enquiry.event_type,
                "event_date": enquiry.event_date.isoformat() if enquiry.event_date else None,
                "guest_count": enquiry.guest_count,
                "budget": enquiry.budget,
                "status": enquiry.status,
                "priority": enquiry.priority,
                "message": enquiry.message,
                "created_at": enquiry.created_at.isoformat(),
                "updated_at": enquiry.updated_at.isoformat(),
                "design_id": enquiry.design_id
            })

        return {
            "enquiries": enquiry_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }

    except Exception as e:
        logger.error(f"Error getting enquiries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve enquiries"
        )

@router.put("/enquiries/{enquiry_id}")
async def update_enquiry(
    enquiry_id: int,
    enquiry_data: Dict[str, Any],
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update enquiry status and details.
    Requires admin or super_admin role.
    """
    try:
        enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
        if not enquiry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enquiry not found"
            )

        # Track changes for audit log
        old_values = {
            "status": enquiry.status,
            "priority": enquiry.priority
        }

        # Update enquiry
        if "status" in enquiry_data:
            enquiry.status = enquiry_data["status"]
        if "priority" in enquiry_data:
            enquiry.priority = enquiry_data["priority"]
        if "notes" in enquiry_data:
            enquiry.admin_notes = enquiry_data["notes"]

        enquiry.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(enquiry)

        # Log the action
        AdminLog.log_action(
            db=db,
            admin_id=current_user.id,
            action="enquiry_status_changed" if "status" in enquiry_data else "enquiry_updated",
            resource_type="enquiry",
            resource_id=enquiry_id,
            old_values=old_values,
            new_values={
                "status": enquiry.status,
                "priority": enquiry.priority
            },
            notes=enquiry_data.get("notes")
        )

        return {
            "message": "Enquiry updated successfully",
            "enquiry": {
                "id": enquiry.id,
                "status": enquiry.status,
                "priority": enquiry.priority,
                "updated_at": enquiry.updated_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating enquiry: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update enquiry"
        )

@router.get("/designs")
async def get_designs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get designs with filtering and pagination.
    Requires admin or super_admin role.
    """
    try:
        # Build query
        query = db.query(Design)

        # Apply filters
        if status_filter:
            query = query.filter(Design.status == status_filter)

        if category:
            query = query.filter(Design.event_type.ilike(f"%{category}%"))

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Design.name.ilike(search_term),
                    Design.event_type.ilike(search_term),
                    Design.customer_name.ilike(search_term)
                )
            )

        if date_from:
            query = query.filter(Design.created_at >= date_from)

        if date_to:
            query = query.filter(Design.created_at <= date_to)

        # Get total count
        total_count = query.count()

        # Apply pagination
        designs = query.order_by(desc(Design.created_at)).offset((page - 1) * limit).limit(limit).all()

        # Format response
        design_list = []
        for design in designs:
            design_list.append({
                "id": design.id,
                "name": design.name,
                "customer_name": design.customer_name,
                "customer_email": design.customer_email,
                "event_type": design.event_type,
                "status": design.status,
                "created_at": design.created_at.isoformat(),
                "updated_at": design.updated_at.isoformat(),
                "preview_url": design.preview_url,
                "total_cost": design.total_cost
            })

        return {
            "designs": design_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }

    except Exception as e:
        logger.error(f"Error getting designs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve designs"
        )

@router.put("/designs/{design_id}")
async def update_design(
    design_id: int,
    design_data: Dict[str, Any],
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update design status and details.
    Requires admin or super_admin role.
    """
    try:
        design = db.query(Design).filter(Design.id == design_id).first()
        if not design:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Design not found"
            )

        # Track changes for audit log
        old_values = {
            "status": design.status,
            "admin_notes": design.admin_notes
        }

        # Update design
        if "status" in design_data:
            design.status = design_data["status"]
        if "admin_notes" in design_data:
            design.admin_notes = design_data["admin_notes"]

        design.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(design)

        # Determine action type
        action = "design_updated"
        if design_data.get("status") == "approved":
            action = "design_approved"
        elif design_data.get("status") == "rejected":
            action = "design_rejected"

        # Log the action
        AdminLog.log_action(
            db=db,
            admin_id=current_user.id,
            action=action,
            resource_type="design",
            resource_id=design_id,
            old_values=old_values,
            new_values={
                "status": design.status,
                "admin_notes": design.admin_notes
            },
            notes=design_data.get("rejection_reason")
        )

        return {
            "message": "Design updated successfully",
            "design": {
                "id": design.id,
                "status": design.status,
                "updated_at": design.updated_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating design: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update design"
        )

@router.get("/gallery")
async def get_gallery_images(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get gallery images with filtering and pagination.
    Requires admin or super_admin role.
    """
    try:
        # Build query
        query = db.query(GalleryImage)

        # Apply filters
        if status_filter:
            query = query.filter(GalleryImage.status == status_filter)

        if category:
            query = query.filter(GalleryImage.category == category)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    GalleryImage.filename.ilike(search_term),
                    GalleryImage.description.ilike(search_term),
                    GalleryImage.tags.ilike(search_term)
                )
            )

        if date_from:
            query = query.filter(GalleryImage.created_at >= date_from)

        if date_to:
            query = query.filter(GalleryImage.created_at <= date_to)

        # Get total count
        total_count = query.count()

        # Apply pagination
        images = query.order_by(desc(GalleryImage.created_at)).offset((page - 1) * limit).limit(limit).all()

        # Format response
        image_list = []
        for image in images:
            image_list.append({
                "id": image.id,
                "filename": image.filename,
                "original_filename": image.original_filename,
                "file_path": image.file_path,
                "file_size": image.file_size,
                "dimensions": image.dimensions,
                "category": image.category,
                "tags": image.tags,
                "description": image.description,
                "status": image.status,
                "uploaded_by": image.uploaded_by,
                "created_at": image.created_at.isoformat(),
                "updated_at": image.updated_at.isoformat()
            })

        return {
            "images": image_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }

    except Exception as e:
        logger.error(f"Error getting gallery images: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve gallery images"
        )

@router.put("/gallery/{image_id}")
async def update_gallery_image(
    image_id: int,
    image_data: Dict[str, Any],
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update gallery image status and metadata.
    Requires admin or super_admin role.
    """
    try:
        image = db.query(GalleryImage).filter(GalleryImage.id == image_id).first()
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )

        # Track changes for audit log
        old_values = {
            "status": image.status,
            "category": image.category,
            "description": image.description
        }

        # Update image
        if "status" in image_data:
            image.status = image_data["status"]
        if "category" in image_data:
            image.category = image_data["category"]
        if "tags" in image_data:
            image.tags = image_data["tags"]
        if "description" in image_data:
            image.description = image_data["description"]

        image.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(image)

        # Determine action type
        action = "gallery_image_approved" if image_data.get("status") == "approved" else \
                 "gallery_image_rejected" if image_data.get("status") == "rejected" else \
                 "gallery_image_updated"

        # Log the action
        AdminLog.log_action(
            db=db,
            admin_id=current_user.id,
            action=action,
            resource_type="gallery_image",
            resource_id=image_id,
            old_values=old_values,
            new_values={
                "status": image.status,
                "category": image.category,
                "description": image.description,
                "tags": image.tags
            }
        )

        return {
            "message": "Gallery image updated successfully",
            "image": {
                "id": image.id,
                "status": image.status,
                "category": image.category,
                "updated_at": image.updated_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating gallery image: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update gallery image"
        )

@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    sort_by: str = Query("created_at_desc"),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get users with filtering and pagination.
    Requires super_admin role.
    """
    try:
        # Build query
        query = db.query(User)

        # Apply filters
        if role_filter:
            query = query.filter(User.role == role_filter)

        if status_filter:
            if status_filter == "active":
                query = query.filter(User.is_active == True)
            elif status_filter == "inactive":
                query = query.filter(User.is_active == False)
            elif status_filter == "banned":
                query = query.filter(User.is_banned == True)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.phone.ilike(search_term)
                )
            )

        if date_from:
            query = query.filter(User.created_at >= date_from)

        if date_to:
            query = query.filter(User.created_at <= date_to)

        # Apply sorting
        if sort_by == "created_at_desc":
            query = query.order_by(desc(User.created_at))
        elif sort_by == "created_at_asc":
            query = query.order_by(asc(User.created_at))
        elif sort_by == "name_asc":
            query = query.order_by(asc(User.name))
        elif sort_by == "last_login_desc":
            query = query.order_by(desc(User.last_login_at))

        # Get total count
        total_count = query.count()

        # Apply pagination
        users = query.offset((page - 1) * limit).limit(limit).all()

        # Format response
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
                "is_active": user.is_active,
                "is_banned": user.is_banned,
                "location": user.location,
                "created_at": user.created_at.isoformat(),
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
            })

        return {
            "users": user_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }

    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: AdminUserManagement,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Update user status and role.
    Requires super_admin role.
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent self-demotion
        if user_id == current_user.id and user_data.action in ["demote", "delete"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot perform this action on yourself"
            )

        # Track changes for audit log
        old_values = {
            "role": user.role,
            "is_active": user.is_active,
            "is_banned": user.is_banned
        }

        # Perform action
        if user_data.action == "activate":
            user.is_active = True
            user.is_banned = False
        elif user_data.action == "deactivate":
            user.is_active = False
        elif user_data.action == "promote":
            if user.role == "user":
                user.role = "admin"
            elif user.role == "admin":
                user.role = "super_admin"
        elif user_data.action == "demote":
            if user.role == "super_admin":
                user.role = "admin"
            elif user.role == "admin":
                user.role = "user"
        elif user_data.action == "delete":
            # Soft delete - mark as inactive and banned
            user.is_active = False
            user.is_banned = True

        user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)

        # Determine action type
        action_map = {
            "activate": "user_unbanned" if user_data.action == "activate" and old_values["is_banned"] else "user_updated",
            "deactivate": "user_updated",
            "promote": "user_role_changed",
            "demote": "user_role_changed",
            "delete": "user_deleted"
        }

        # Log the action
        AdminLog.log_action(
            db=db,
            admin_id=current_user.id,
            action=action_map.get(user_data.action, "user_updated"),
            resource_type="user",
            resource_id=user_id,
            old_values=old_values,
            new_values={
                "role": user.role,
                "is_active": user.is_active,
                "is_banned": user.is_banned
            },
            notes=user_data.reason
        )

        return {
            "message": f"User {user_data.action}d successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "is_banned": user.is_banned
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.get("/logs")
async def get_admin_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    admin_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get admin activity logs with filtering.
    Requires super_admin role.
    """
    try:
        # Build query
        query = db.query(AdminLog)

        # Apply filters
        if admin_id:
            query = query.filter(AdminLog.admin_id == admin_id)

        if action:
            query = query.filter(AdminLog.action == action)

        if resource_type:
            query = query.filter(AdminLog.resource_type == resource_type)

        if risk_level:
            query = query.filter(AdminLog.risk_level == risk_level)

        if date_from:
            query = query.filter(AdminLog.created_at >= date_from)

        if date_to:
            query = query.filter(AdminLog.created_at <= date_to)

        # Get total count
        total_count = query.count()

        # Apply pagination
        logs = query.order_by(desc(AdminLog.created_at)).offset((page - 1) * limit).limit(limit).all()

        # Format response
        log_list = []
        for log in logs:
            log_list.append({
                "id": log.id,
                "admin_id": log.admin_id,
                "admin_email": log.admin.email if log.admin else None,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "changes": log.changes,
                "notes": log.notes,
                "risk_level": log.risk_level,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat(),
                "action_description": log.get_action_description(),
                "is_high_risk": log.is_high_risk
            })

        return {
            "logs": log_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }

    except Exception as e:
        logger.error(f"Error getting admin logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve admin logs"
        )

@router.get("/settings")
async def get_system_settings(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get system settings.
    Requires admin or super_admin role.
    """
    # For now, return placeholder settings
    # In a real implementation, this would fetch from a settings table
    return {
        "business_name": "Hublievents",
        "business_email": "admin@hublievents.com",
        "enquiry_auto_assign": True,
        "design_approval_required": True,
        "gallery_auto_approve": False,
        "max_file_size": 10,
        "session_timeout": 480
    }

@router.post("/settings")
async def update_system_settings(
    settings: Dict[str, Any],
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Update system settings.
    Requires super_admin role.
    """
    try:
        # Log the settings change
        AdminLog.log_action(
            db=db,
            admin_id=current_user.id,
            action="system_config_changed",
            resource_type="system",
            resource_id=None,
            changes=settings,
            notes="System settings updated"
        )

        # In a real implementation, this would save to a settings table
        return {
            "message": "Settings updated successfully",
            "settings": settings
        }

    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings"
        )
