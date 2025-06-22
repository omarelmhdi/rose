"""
ملف الإعدادات الرئيسي للبوت
"""
import os
from typing import List
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

class Config:
    """فئة الإعدادات الرئيسية"""
    
    # إعدادات البوت الأساسية
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "")
    
    # إعدادات قاعدة البيانات
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # إعدادات Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # إعدادات المطورين
    SUDO_USERS: List[int] = [
        int(user_id) for user_id in os.getenv("SUDO_USERS", "").split(",")
        if user_id.strip().isdigit()
    ]
    
    # إعدادات الويب هوك
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "/webhook")
    WEBAPP_HOST: str = os.getenv("WEBAPP_HOST", "0.0.0.0")
    WEBAPP_PORT: int = int(os.getenv("WEBAPP_PORT", 8080))
    
    # إعدادات الحماية
    MAX_WARNS: int = 3
    FLOOD_LIMIT: int = 5  # عدد الرسائل المسموح بها في الثانية
    FLOOD_TIME: int = 60  # مدة الحظر بالثواني
    
    # إعدادات الرسائل
    DEFAULT_WELCOME_MESSAGE: str = """
🌟 أهلاً وسهلاً {first_name}!

مرحباً بك في {chat_title}
نتمنى لك وقتاً ممتعاً معنا 🎉

يرجى قراءة قواعد المجموعة والالتزام بها.
    """
    
    # رموز الحالة
    EMOJI = {
        "check": "✅",
        "cross": "❌", 
        "warning": "⚠️",
        "info": "ℹ️",
        "ban": "🚫",
        "mute": "🔇",
        "warn": "⚠️",
        "admin": "👑",
        "user": "👤",
        "group": "👥",
        "link": "🔗",
        "spam": "⚡",
        "welcome": "👋",
        "settings": "⚙️"
    }

# إنشاء مثيل من الإعدادات
config = Config()

# التحقق من صحة الإعدادات
def validate_config():
    """التحقق من صحة الإعدادات المطلوبة"""
    if not config.BOT_TOKEN:
        raise ValueError("BOT_TOKEN غير موجود في متغيرات البيئة")
    
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        raise ValueError("إعدادات Supabase غير مكتملة")
    
    return True
