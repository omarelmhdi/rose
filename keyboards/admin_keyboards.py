"""
لوحات مفاتيح الإدارة
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config.config import config

def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """لوحة مفاتيح لوحة الإدارة الرئيسية"""
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{config.EMOJI['settings']} إعدادات الحماية",
                callback_data="admin_protection"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{config.EMOJI['admin']} إدارة المشرفين",
                callback_data="admin_admins"
            ),
            InlineKeyboardButton(
                text=f"{config.EMOJI['user']} إدارة الأعضاء",
                callback_data="admin_members"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{config.EMOJI['welcome']} رسالة الترحيب",
                callback_data="admin_welcome"
            ),
            InlineKeyboardButton(
                text="📝 الملاحظات والفلاتر",
                callback_data="admin_notes"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 الإحصائيات",
                callback_data="admin_stats"
            ),
            InlineKeyboardButton(
                text="🔧 الإعدادات العامة",
                callback_data="admin_general"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ إغلاق",
                callback_data="admin_close"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_protection_keyboard() -> InlineKeyboardMarkup:
    """لوحة مفاتيح إعدادات الحماية"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="🌊 مكافحة السبام",
                callback_data="protection_antiflood"
            ),
            InlineKeyboardButton(
                text="🔗 منع الروابط",
                callback_data="protection_antilink"
            )
        ],
        [
            InlineKeyboardButton(
                text="🚫 منع الكلمات",
                callback_data="protection_antiword"
            ),
            InlineKeyboardButton(
                text="⚠️ نظام التحذيرات",
                callback_data="protection_warns"
            )
        ],
        [
            InlineKeyboardButton(
                text="📝 الكلمات المحظورة",
                callback_data="protection_banned_words"
            ),
            InlineKeyboardButton(
                text="✅ الروابط المسموحة",
                callback_data="protection_allowed_links"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 العودة",
                callback_data="admin_back"
            ),
            InlineKeyboardButton(
                text="❌ إغلاق",
                callback_data="admin_close"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confirm_keyboard(action: str, user_id: int = None) -> InlineKeyboardMarkup:
    """لوحة مفاتيح التأكيد"""
    callback_data = f"confirm_{action}"
    if user_id:
        callback_data += f"_{user_id}"
    
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ تأكيد",
                callback_data=callback_data
            ),
            InlineKeyboardButton(
                text="❌ إلغاء",
                callback_data="cancel_action"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_welcome_keyboard() -> InlineKeyboardMarkup:
    """لوحة مفاتيح إعدادات الترحيب"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="🔧 تخصيص الرسالة",
                callback_data="welcome_customize"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ تفعيل الترحيب",
                callback_data="welcome_enable"
            ),
            InlineKeyboardButton(
                text="❌ إيقاف الترحيب",
                callback_data="welcome_disable"
            )
        ],
        [
            InlineKeyboardButton(
                text="👀 معاينة الرسالة",
                callback_data="welcome_preview"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 العودة",
                callback_data="admin_back"
            ),
            InlineKeyboardButton(
                text="❌ إغلاق",
                callback_data="admin_close"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_management_keyboard() -> InlineKeyboardMarkup:
    """لوحة مفاتيح إدارة المشرفين"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="👥 قائمة المشرفين",
                callback_data="admins_list"
            )
        ],
        [
            InlineKeyboardButton(
                text="➕ إضافة مشرف",
                callback_data="admins_add"
            ),
            InlineKeyboardButton(
                text="➖ إزالة مشرف",
                callback_data="admins_remove"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏷️ تعديل الرتب",
                callback_data="admins_ranks"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 العودة",
                callback_data="admin_back"
            ),
            InlineKeyboardButton(
                text="❌ إغلاق",
                callback_data="admin_close"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_member_management_keyboard() -> InlineKeyboardMarkup:
    """لوحة مفاتيح إدارة الأعضاء"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="🚫 المحظورين",
                callback_data="members_banned"
            ),
            InlineKeyboardButton(
                text="🔇 المكتومين",
                callback_data="members_muted"
            )
        ],
        [
            InlineKeyboardButton(
                text="⚠️ التحذيرات",
                callback_data="members_warnings"
            )
        ],
        [
            InlineKeyboardButton(
                text="🧹 تنظيف الحسابات المحذوفة",
                callback_data="members_cleanup"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 العودة",
                callback_data="admin_back"
            ),
            InlineKeyboardButton(
                text="❌ إغلاق",
                callback_data="admin_close"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_notes_keyboard() -> InlineKeyboardMarkup:
    """لوحة مفاتيح الملاحظات والفلاتر"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📝 قائمة الملاحظات",
                callback_data="notes_list"
            )
        ],
        [
            InlineKeyboardButton(
                text="➕ إضافة ملاحظة",
                callback_data="notes_add"
            ),
            InlineKeyboardButton(
                text="➖ حذف ملاحظة",
                callback_data="notes_delete"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔍 الفلاتر المخصصة",
                callback_data="filters_custom"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 العودة",
                callback_data="admin_back"
            ),
            InlineKeyboardButton(
                text="❌ إغلاق",
                callback_data="admin_close"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_stats_keyboard() -> InlineKeyboardMarkup:
    """لوحة مفاتيح الإحصائيات"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📊 إحصائيات عامة",
                callback_data="stats_general"
            )
        ],
        [
            InlineKeyboardButton(
                text="📈 إحصائيات الأعضاء",
                callback_data="stats_members"
            ),
            InlineKeyboardButton(
                text="📉 إحصائيات الأنشطة",
                callback_data="stats_activity"
            )
        ],
        [
            InlineKeyboardButton(
                text="🕒 إحصائيات يومية",
                callback_data="stats_daily"
            ),
            InlineKeyboardButton(
                text="📅 إحصائيات شهرية",
                callback_data="stats_monthly"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 العودة",
                callback_data="admin_back"
            ),
            InlineKeyboardButton(
                text="❌ إغلاق",
                callback_data="admin_close"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_general_settings_keyboard() -> InlineKeyboardMarkup:
    """لوحة مفاتيح الإعدادات العامة"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="🎨 تخصيص الرسائل",
                callback_data="settings_messages"
            )
        ],
        [
            InlineKeyboardButton(
                text="🌐 اللغة",
                callback_data="settings_language"
            ),
            InlineKeyboardButton(
                text="🕒 المنطقة الزمنية",
                callback_data="settings_timezone"
            )
        ],
        [
            InlineKeyboardButton(
                text="📱 إعدادات الوسائط",
                callback_data="settings_media"
            )
        ],
        [
            InlineKeyboardButton(
                text="💾 نسخ احتياطي",
                callback_data="settings_backup"
            ),
            InlineKeyboardButton(
                text="🔄 استعادة",
                callback_data="settings_restore"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 العودة",
                callback_data="admin_back"
            ),
            InlineKeyboardButton(
                text="❌ إغلاق",
                callback_data="admin_close"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_user_action_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """لوحة مفاتيح إجراءات المستخدم"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="🚫 حظر",
                callback_data=f"user_ban_{user_id}"
            ),
            InlineKeyboardButton(
                text="🔇 كتم",
                callback_data=f"user_mute_{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⚠️ تحذير",
                callback_data=f"user_warn_{user_id}"
            ),
            InlineKeyboardButton(
                text="👢 طرد",
                callback_data=f"user_kick_{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="ℹ️ معلومات",
                callback_data=f"user_info_{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ إلغاء",
                callback_data="cancel_action"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_pagination_keyboard(current_page: int, total_pages: int, callback_prefix: str) -> InlineKeyboardMarkup:
    """لوحة مفاتيح الصفحات"""
    keyboard = []
    
    nav_buttons = []
    
    # زر الصفحة السابقة
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="◀️ السابق",
                callback_data=f"{callback_prefix}_page_{current_page - 1}"
            )
        )
    
    # عرض رقم الصفحة
    nav_buttons.append(
        InlineKeyboardButton(
            text=f"{current_page}/{total_pages}",
            callback_data="page_info"
        )
    )
    
    # زر الصفحة التالية
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="▶️ التالي",
                callback_data=f"{callback_prefix}_page_{current_page + 1}"
            )
        )
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # زر العودة
    keyboard.append([
        InlineKeyboardButton(
            text="🔙 العودة",
            callback_data="admin_back"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
