"""
حزمة معالجات البوت
"""
from .admin_handlers import admin_router
from .protection_handlers import protection_router
from .welcome_handlers import welcome_router
from .general_handlers import general_router
from .callback_handlers import callback_router

__all__ = [
    "admin_router",
    "protection_router", 
    "welcome_router",
    "general_router",
    "callback_router"
]
