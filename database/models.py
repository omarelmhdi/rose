"""
نماذج قاعدة البيانات
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

@dataclass
class User:
    """نموذج المستخدم"""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = "ar"
    is_bot: bool = False
    is_premium: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Chat:
    """نموذج الدردشة/المجموعة"""
    chat_id: int
    title: Optional[str] = None
    chat_type: str = "group"  # private, group, supergroup, channel
    username: Optional[str] = None
    description: Optional[str] = None
    
    # إعدادات المجموعة
    welcome_enabled: bool = True
    welcome_message: Optional[str] = None
    antiflood_enabled: bool = True
    antilink_enabled: bool = False
    antiword_enabled: bool = False
    warns_enabled: bool = True
    max_warns: int = 3
    
    # قوائم الحظر والكلمات المحظورة
    banned_words: List[str] = field(default_factory=list)
    allowed_links: List[str] = field(default_factory=list)
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Admin:
    """نموذج المشرف"""
    user_id: int
    chat_id: int
    rank: str = "admin"  # admin, owner, sudo
    title: Optional[str] = None
    can_delete_messages: bool = True
    can_restrict_members: bool = True
    can_promote_members: bool = False
    can_change_info: bool = False
    can_invite_users: bool = True
    can_pin_messages: bool = True
    created_at: Optional[datetime] = None

@dataclass
class Warning:
    """نموذج التحذير"""
    id: Optional[int] = None
    user_id: int = 0
    chat_id: int = 0
    admin_id: int = 0
    reason: Optional[str] = None
    warn_count: int = 1
    created_at: Optional[datetime] = None

@dataclass
class Ban:
    """نموذج الحظر"""
    id: Optional[int] = None
    user_id: int = 0
    chat_id: int = 0
    admin_id: int = 0
    reason: Optional[str] = None
    ban_type: str = "ban"  # ban, mute, kick
    duration: Optional[int] = None  # بالثواني، None = دائم
    expires_at: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

@dataclass
class Filter:
    """نموذج الفلتر المخصص"""
    id: Optional[int] = None
    chat_id: int = 0
    keyword: str = ""
    response: str = ""
    filter_type: str = "text"  # text, sticker, photo, video, etc.
    media_file_id: Optional[str] = None
    created_by: int = 0
    created_at: Optional[datetime] = None

@dataclass
class Note:
    """نموذج الملاحظة المحفوظة"""
    id: Optional[int] = None
    chat_id: int = 0
    name: str = ""
    content: str = ""
    note_type: str = "text"  # text, sticker, photo, video, etc.
    media_file_id: Optional[str] = None
    created_by: int = 0
    created_at: Optional[datetime] = None

@dataclass
class Settings:
    """نموذج إعدادات المجموعة المتقدمة"""
    chat_id: int
    settings_data: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def get_setting(self, key: str, default=None):
        """استرجاع إعداد معين"""
        return self.settings_data.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """تعيين إعداد معين"""
        self.settings_data[key] = value
        self.updated_at = datetime.now()
