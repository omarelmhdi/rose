"""
وظائف مساعدة متنوعة
"""
import re
from typing import Optional, Tuple, Union
from aiogram.types import Message, User
from aiogram import Bot

def parse_time(time_str: str) -> Optional[int]:
    """تحليل النص الزمني وإرجاع الثواني"""
    if not time_str:
        return None
    
    # إزالة المسافات
    time_str = time_str.strip().lower()
    
    # التعبيرات النمطية للوقت
    patterns = {
        r'(\d+)s': 1,           # ثواني
        r'(\d+)m': 60,          # دقائق
        r'(\d+)h': 3600,        # ساعات
        r'(\d+)d': 86400,       # أيام
        r'(\d+)w': 604800,      # أسابيع
    }
    
    total_seconds = 0
    
    for pattern, multiplier in patterns.items():
        matches = re.findall(pattern, time_str)
        for match in matches:
            total_seconds += int(match) * multiplier
    
    # إذا لم يتم العثور على أي نمط، جرب رقم فقط (دقائق)
    if total_seconds == 0:
        try:
            number = int(time_str)
            total_seconds = number * 60  # افتراض أنه دقائق
        except ValueError:
            return None
    
    return total_seconds if total_seconds > 0 else None

async def extract_user_and_reason(message: Message, args: str) -> Tuple[Optional[int], Optional[str]]:
    """استخراج معرف المستخدم والسبب من النص"""
    if not args:
        # التحقق من الرد على رسالة
        if message.reply_to_message:
            return message.reply_to_message.from_user.id, None
        return None, None
    
    parts = args.split()
    user_id = None
    reason = None
    
    # محاولة استخراج المستخدم من الجزء الأول
    first_part = parts[0]
    
    # التحقق من معرف رقمي
    if first_part.isdigit():
        user_id = int(first_part)
        reason = " ".join(parts[1:]) if len(parts) > 1 else None
    
    # التحقق من اسم المستخدم
    elif first_part.startswith('@'):
        username = first_part[1:]
        try:
            # محاولة الحصول على معلومات المستخدم
            chat_member = await message.bot.get_chat_member(message.chat.id, f"@{username}")
            user_id = chat_member.user.id
            reason = " ".join(parts[1:]) if len(parts) > 1 else None
        except Exception:
            pass
    
    # التحقق من الرد على رسالة
    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        reason = args  # كامل النص كسبب
    
    return user_id, reason

async def format_user_mention(user_id: int, bot: Bot) -> str:
    """تنسيق منشن المستخدم"""
    try:
        user = await bot.get_chat(user_id)
        if hasattr(user, 'username') and user.username:
            return f"@{user.username}"
        elif hasattr(user, 'first_name'):
            return f"<a href='tg://user?id={user_id}'>{user.first_name}</a>"
        else:
            return f"<a href='tg://user?id={user_id}'>المستخدم</a>"
    except Exception:
        return f"<a href='tg://user?id={user_id}'>المستخدم</a>"

def format_file_size(size: int) -> str:
    """تنسيق حجم الملف"""
    if size < 1024:
        return f"{size} بايت"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} كيلوبايت"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} ميجابايت"
    else:
        return f"{size / (1024 * 1024 * 1024):.1f} جيجابايت"

def escape_html(text: str) -> str:
    """إفلات HTML"""
    if not text:
        return ""
    
    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;"
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def escape_markdown(text: str) -> str:
    """إفلات Markdown"""
    if not text:
        return ""
    
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def is_url(text: str) -> bool:
    """التحقق من كون النص رابط"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return bool(url_pattern.search(text))

def extract_urls(text: str) -> list:
    """استخراج الروابط من النص"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.findall(text)

def clean_text(text: str) -> str:
    """تنظيف النص من الرموز الخاصة"""
    if not text:
        return ""
    
    # إزالة الرموز الخاصة ما عدا المسافات والأرقام والحروف العربية والإنجليزية
    cleaned = re.sub(r'[^\w\s\u0600-\u06FF]', '', text)
    
    # إزالة المسافات الزائدة
    cleaned = ' '.join(cleaned.split())
    
    return cleaned

def format_datetime(dt) -> str:
    """تنسيق التاريخ والوقت"""
    if not dt:
        return "غير محدد"
    
    try:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(dt)

def check_arabic_text(text: str) -> bool:
    """التحقق من وجود نص عربي"""
    if not text:
        return False
    
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))

def get_file_extension(filename: str) -> str:
    """الحصول على امتداد الملف"""
    if not filename or '.' not in filename:
        return ""
    
    return filename.split('.')[-1].lower()

def is_valid_username(username: str) -> bool:
    """التحقق من صحة اسم المستخدم"""
    if not username:
        return False
    
    # إزالة @ إذا كانت موجودة
    username = username.lstrip('@')
    
    # التحقق من الطول والرموز المسموحة
    if len(username) < 5 or len(username) > 32:
        return False
    
    # يجب أن يحتوي فقط على حروف، أرقام، وشرطة سفلية
    pattern = re.compile(r'^[a-zA-Z0-9_]+$')
    return bool(pattern.match(username))

def format_duration(seconds: int) -> str:
    """تنسيق المدة الزمنية بالعربية"""
    if seconds < 60:
        return f"{seconds} ثانية"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds > 0:
            return f"{minutes} دقيقة و {remaining_seconds} ثانية"
        return f"{minutes} دقيقة"
    elif seconds < 86400:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes > 0:
            return f"{hours} ساعة و {remaining_minutes} دقيقة"
        return f"{hours} ساعة"
    else:
        days = seconds // 86400
        remaining_hours = (seconds % 86400) // 3600
        if remaining_hours > 0:
            return f"{days} يوم و {remaining_hours} ساعة"
        return f"{days} يوم"
