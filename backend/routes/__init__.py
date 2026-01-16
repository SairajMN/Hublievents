"""
API routes package for Hublievents Backend API.
All route modules are imported here for easy access.
"""

from .auth import router as auth_router
# TODO: Uncomment when routes are implemented
# from .users import router as users_router
# from .designs import router as designs_router
# from .enquiries import router as enquiries_router
# from .gallery import router as gallery_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "users_router",
    "designs_router",
    "enquiries_router",
    "gallery_router",
    "admin_router",
]
