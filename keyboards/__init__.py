"""
حزمة لوحات المفاتيح
"""
from .admin_keyboards import (
    get_admin_panel_keyboard, get_protection_keyboard, get_confirm_keyboard,
    get_welcome_keyboard, get_admin_management_keyboard, get_member_management_keyboard,
    get_notes_keyboard, get_stats_keyboard, get_general_settings_keyboard,
    get_user_action_keyboard, get_pagination_keyboard
)

__all__ = [
    "get_admin_panel_keyboard", "get_protection_keyboard", "get_confirm_keyboard",
    "get_welcome_keyboard", "get_admin_management_keyboard", "get_member_management_keyboard",
    "get_notes_keyboard", "get_stats_keyboard", "get_general_settings_keyboard",
    "get_user_action_keyboard", "get_pagination_keyboard"
]
