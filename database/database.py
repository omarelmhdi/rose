"""
وحدة إدارة قاعدة البيانات مع Supabase
"""
import asyncio
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from supabase import create_client, Client
from config.config import config
from .models import User, Chat, Admin, Warning, Ban, Filter, Note, Settings

class Database:
    """فئة إدارة قاعدة البيانات"""
    
    def __init__(self):
        self.supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    
    async def create_tables(self):
        """إنشاء الجداول في قاعدة البيانات"""
        # سيتم إنشاء الجداول من خلال واجهة Supabase
        # هذا مثال على الـ SQL المطلوب:
        tables_sql = """
        -- جدول المستخدمين
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language_code TEXT DEFAULT 'ar',
            is_bot BOOLEAN DEFAULT FALSE,
            is_premium BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        -- جدول المجموعات
        CREATE TABLE IF NOT EXISTS chats (
            chat_id BIGINT PRIMARY KEY,
            title TEXT,
            chat_type TEXT DEFAULT 'group',
            username TEXT,
            description TEXT,
            welcome_enabled BOOLEAN DEFAULT TRUE,
            welcome_message TEXT,
            antiflood_enabled BOOLEAN DEFAULT TRUE,
            antilink_enabled BOOLEAN DEFAULT FALSE,
            antiword_enabled BOOLEAN DEFAULT FALSE,
            warns_enabled BOOLEAN DEFAULT TRUE,
            max_warns INTEGER DEFAULT 3,
            banned_words JSONB DEFAULT '[]',
            allowed_links JSONB DEFAULT '[]',
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        -- جدول المشرفين
        CREATE TABLE IF NOT EXISTS admins (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            chat_id BIGINT NOT NULL,
            rank TEXT DEFAULT 'admin',
            title TEXT,
            can_delete_messages BOOLEAN DEFAULT TRUE,
            can_restrict_members BOOLEAN DEFAULT TRUE,
            can_promote_members BOOLEAN DEFAULT FALSE,
            can_change_info BOOLEAN DEFAULT FALSE,
            can_invite_users BOOLEAN DEFAULT TRUE,
            can_pin_messages BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(user_id, chat_id)
        );
        
        -- جدول التحذيرات
        CREATE TABLE IF NOT EXISTS warnings (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            chat_id BIGINT NOT NULL,
            admin_id BIGINT NOT NULL,
            reason TEXT,
            warn_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        -- جدول الحظر
        CREATE TABLE IF NOT EXISTS bans (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            chat_id BIGINT NOT NULL,
            admin_id BIGINT NOT NULL,
            reason TEXT,
            ban_type TEXT DEFAULT 'ban',
            duration INTEGER,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        -- جدول الفلاتر
        CREATE TABLE IF NOT EXISTS filters (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT NOT NULL,
            keyword TEXT NOT NULL,
            response TEXT NOT NULL,
            filter_type TEXT DEFAULT 'text',
            media_file_id TEXT,
            created_by BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        -- جدول الملاحظات
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT NOT NULL,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            note_type TEXT DEFAULT 'text',
            media_file_id TEXT,
            created_by BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(chat_id, name)
        );
        
        -- جدول الإعدادات
        CREATE TABLE IF NOT EXISTS settings (
            chat_id BIGINT PRIMARY KEY,
            settings_data JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        pass  # يتم تنفيذ الـ SQL من خلال واجهة Supabase
    
    # وظائف المستخدمين
    async def get_user(self, user_id: int) -> Optional[User]:
        """جلب معلومات المستخدم"""
        try:
            result = self.supabase.table("users").select("*").eq("user_id", user_id).execute()
            if result.data:
                return User(**result.data[0])
            return None
        except Exception as e:
            print(f"خطأ في جلب المستخدم: {e}")
            return None
    
    async def add_or_update_user(self, user: User) -> bool:
        """إضافة أو تحديث المستخدم"""
        try:
            user_data = {
                "user_id": user.user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language_code": user.language_code,
                "is_bot": user.is_bot,
                "is_premium": user.is_premium,
                "updated_at": datetime.now().isoformat()
            }
            
            self.supabase.table("users").upsert(user_data).execute()
            return True
        except Exception as e:
            print(f"خطأ في حفظ المستخدم: {e}")
            return False
    
    # وظائف المجموعات
    async def get_chat(self, chat_id: int) -> Optional[Chat]:
        """جلب معلومات المجموعة"""
        try:
            result = self.supabase.table("chats").select("*").eq("chat_id", chat_id).execute()
            if result.data:
                data = result.data[0]
                # تحويل JSON إلى قوائم
                data["banned_words"] = data.get("banned_words", [])
                data["allowed_links"] = data.get("allowed_links", [])
                return Chat(**data)
            return None
        except Exception as e:
            print(f"خطأ في جلب المجموعة: {e}")
            return None
    
    async def add_or_update_chat(self, chat: Chat) -> bool:
        """إضافة أو تحديث المجموعة"""
        try:
            chat_data = {
                "chat_id": chat.chat_id,
                "title": chat.title,
                "chat_type": chat.chat_type,
                "username": chat.username,
                "description": chat.description,
                "welcome_enabled": chat.welcome_enabled,
                "welcome_message": chat.welcome_message,
                "antiflood_enabled": chat.antiflood_enabled,
                "antilink_enabled": chat.antilink_enabled,
                "antiword_enabled": chat.antiword_enabled,
                "warns_enabled": chat.warns_enabled,
                "max_warns": chat.max_warns,
                "banned_words": json.dumps(chat.banned_words),
                "allowed_links": json.dumps(chat.allowed_links),
                "updated_at": datetime.now().isoformat()
            }
            
            self.supabase.table("chats").upsert(chat_data).execute()
            return True
        except Exception as e:
            print(f"خطأ في حفظ المجموعة: {e}")
            return False
    
    # وظائف المشرفين
    async def get_admins(self, chat_id: int) -> List[Admin]:
        """جلب قائمة المشرفين"""
        try:
            result = self.supabase.table("admins").select("*").eq("chat_id", chat_id).execute()
            return [Admin(**admin) for admin in result.data]
        except Exception as e:
            print(f"خطأ في جلب المشرفين: {e}")
            return []
    
    async def is_admin(self, user_id: int, chat_id: int) -> bool:
        """التحقق من كون المستخدم مشرف"""
        try:
            # التحقق من المطورين أولاً
            if user_id in config.SUDO_USERS:
                return True
            
            result = self.supabase.table("admins").select("*").eq("user_id", user_id).eq("chat_id", chat_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"خطأ في التحقق من الإدارة: {e}")
            return False
    
    async def add_admin(self, admin: Admin) -> bool:
        """إضافة مشرف"""
        try:
            admin_data = {
                "user_id": admin.user_id,
                "chat_id": admin.chat_id,
                "rank": admin.rank,
                "title": admin.title,
                "can_delete_messages": admin.can_delete_messages,
                "can_restrict_members": admin.can_restrict_members,
                "can_promote_members": admin.can_promote_members,
                "can_change_info": admin.can_change_info,
                "can_invite_users": admin.can_invite_users,
                "can_pin_messages": admin.can_pin_messages
            }
            
            self.supabase.table("admins").upsert(admin_data).execute()
            return True
        except Exception as e:
            print(f"خطأ في إضافة المشرف: {e}")
            return False
    
    async def remove_admin(self, user_id: int, chat_id: int) -> bool:
        """حذف مشرف"""
        try:
            self.supabase.table("admins").delete().eq("user_id", user_id).eq("chat_id", chat_id).execute()
            return True
        except Exception as e:
            print(f"خطأ في حذف المشرف: {e}")
            return False
    
    # وظائف التحذيرات
    async def add_warning(self, warning: Warning) -> bool:
        """إضافة تحذير"""
        try:
            warning_data = {
                "user_id": warning.user_id,
                "chat_id": warning.chat_id,
                "admin_id": warning.admin_id,
                "reason": warning.reason,
                "warn_count": warning.warn_count
            }
            
            self.supabase.table("warnings").insert(warning_data).execute()
            return True
        except Exception as e:
            print(f"خطأ في إضافة التحذير: {e}")
            return False
    
    async def get_warnings(self, user_id: int, chat_id: int) -> List[Warning]:
        """جلب تحذيرات المستخدم"""
        try:
            result = self.supabase.table("warnings").select("*").eq("user_id", user_id).eq("chat_id", chat_id).execute()
            return [Warning(**warning) for warning in result.data]
        except Exception as e:
            print(f"خطأ في جلب التحذيرات: {e}")
            return []
    
    async def clear_warnings(self, user_id: int, chat_id: int) -> bool:
        """مسح تحذيرات المستخدم"""
        try:
            self.supabase.table("warnings").delete().eq("user_id", user_id).eq("chat_id", chat_id).execute()
            return True
        except Exception as e:
            print(f"خطأ في مسح التحذيرات: {e}")
            return False
    
    # وظائف الحظر
    async def add_ban(self, ban: Ban) -> bool:
        """إضافة حظر"""
        try:
            ban_data = {
                "user_id": ban.user_id,
                "chat_id": ban.chat_id,
                "admin_id": ban.admin_id,
                "reason": ban.reason,
                "ban_type": ban.ban_type,
                "duration": ban.duration,
                "expires_at": ban.expires_at.isoformat() if ban.expires_at else None,
                "is_active": ban.is_active
            }
            
            self.supabase.table("bans").insert(ban_data).execute()
            return True
        except Exception as e:
            print(f"خطأ في إضافة الحظر: {e}")
            return False
    
    async def is_banned(self, user_id: int, chat_id: int) -> Optional[Ban]:
        """التحقق من حظر المستخدم"""
        try:
            result = self.supabase.table("bans").select("*").eq("user_id", user_id).eq("chat_id", chat_id).eq("is_active", True).execute()
            
            if result.data:
                ban_data = result.data[0]
                # التحقق من انتهاء صلاحية الحظر
                if ban_data.get("expires_at"):
                    expires_at = datetime.fromisoformat(ban_data["expires_at"])
                    if datetime.now() > expires_at:
                        await self.remove_ban(user_id, chat_id)
                        return None
                
                return Ban(**ban_data)
            return None
        except Exception as e:
            print(f"خطأ في التحقق من الحظر: {e}")
            return None
    
    async def remove_ban(self, user_id: int, chat_id: int) -> bool:
        """إلغاء الحظر"""
        try:
            self.supabase.table("bans").update({"is_active": False}).eq("user_id", user_id).eq("chat_id", chat_id).execute()
            return True
        except Exception as e:
            print(f"خطأ في إلغاء الحظر: {e}")
            return False

# إنشاء مثيل قاعدة البيانات
db = Database()
