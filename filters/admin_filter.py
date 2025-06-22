"""
فلاتر التحقق من صلاحيات الإدارة
"""
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from aiogram.types import ChatMemberOwner, ChatMemberAdministrator
from database import db
from config.config import config

class AdminFilter(BaseFilter):
    """فلتر للتحقق من صلاحيات الإدارة"""
    
    def __init__(self, check_can_restrict: bool = True):
        self.check_can_restrict = check_can_restrict
    
    async def __call__(self, obj) -> bool:
        """التحقق من صلاحيات المستخدم"""
        if isinstance(obj, Message):
            message = obj
        elif isinstance(obj, CallbackQuery):
            message = obj.message
        else:
            return False
        
        user_id = obj.from_user.id
        chat_id = message.chat.id
        
        # التحقق من كون المستخدم مطور
        if user_id in config.SUDO_USERS:
            return True
        
        # التحقق من كون المستخدم مشرف في قاعدة البيانات
        if await db.is_admin(user_id, chat_id):
            return True
        
        try:
            # التحقق من صلاحيات تليجرام
            member = await message.bot.get_chat_member(chat_id, user_id)
            
            # التحقق من كون المستخدم منشئ المجموعة
            if isinstance(member, ChatMemberOwner):
                return True
            
            # التحقق من كون المستخدم مشرف
            if isinstance(member, ChatMemberAdministrator):
                # إذا كان مطلوب التحقق من صلاحية تقييد الأعضاء
                if self.check_can_restrict:
                    return member.can_restrict_members
                return True
            
            return False
            
        except Exception:
            return False

class OwnerFilter(BaseFilter):
    """فلتر للتحقق من كون المستخدم منشئ المجموعة"""
    
    async def __call__(self, obj) -> bool:
        if isinstance(obj, Message):
            message = obj
        elif isinstance(obj, CallbackQuery):
            message = obj.message
        else:
            return False
        
        user_id = obj.from_user.id
        chat_id = message.chat.id
        
        # التحقق من كون المستخدم مطور
        if user_id in config.SUDO_USERS:
            return True
        
        try:
            member = await message.bot.get_chat_member(chat_id, user_id)
            return isinstance(member, ChatMemberOwner)
        except Exception:
            return False

class CanDeleteFilter(BaseFilter):
    """فلتر للتحقق من صلاحية حذف الرسائل"""
    
    async def __call__(self, obj) -> bool:
        if isinstance(obj, Message):
            message = obj
        elif isinstance(obj, CallbackQuery):
            message = obj.message
        else:
            return False
        
        user_id = obj.from_user.id
        chat_id = message.chat.id
        
        # التحقق من كون المستخدم مطور
        if user_id in config.SUDO_USERS:
            return True
        
        try:
            member = await message.bot.get_chat_member(chat_id, user_id)
            
            if isinstance(member, ChatMemberOwner):
                return True
            
            if isinstance(member, ChatMemberAdministrator):
                return member.can_delete_messages
            
            return False
            
        except Exception:
            return False

class CanPinFilter(BaseFilter):
    """فلتر للتحقق من صلاحية تثبيت الرسائل"""
    
    async def __call__(self, obj) -> bool:
        if isinstance(obj, Message):
            message = obj
        elif isinstance(obj, CallbackQuery):
            message = obj.message
        else:
            return False
        
        user_id = obj.from_user.id
        chat_id = message.chat.id
        
        # التحقق من كون المستخدم مطور
        if user_id in config.SUDO_USERS:
            return True
        
        try:
            member = await message.bot.get_chat_member(chat_id, user_id)
            
            if isinstance(member, ChatMemberOwner):
                return True
            
            if isinstance(member, ChatMemberAdministrator):
                return member.can_pin_messages
            
            return False
            
        except Exception:
            return False
