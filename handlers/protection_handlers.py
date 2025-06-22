"""
معالجات الحماية والفلاتر
"""
import asyncio
import time
from typing import Dict, List
from aiogram import Router, F
from aiogram.types import Message, ContentType
from aiogram.filters import Command, CommandObject
from database import db, Warning, Ban
from config.config import config
from filters.admin_filter import AdminFilter
from utils.helpers import extract_urls, is_url, clean_text, extract_user_and_reason
from keyboards.admin_keyboards import get_protection_keyboard

# راوتر الحماية
protection_router = Router()

# ذاكرة تخزين لمكافحة السبام
flood_storage: Dict[str, List[float]] = {}

@protection_router.message(Command("antiflood"), AdminFilter())
async def toggle_antiflood(message: Message, command: CommandObject):
    """تشغيل/إيقاف مكافحة السبام"""
    try:
        chat = await db.get_chat(message.chat.id)
        if not chat:
            await message.reply(f"{config.EMOJI['cross']} لم يتم العثور على إعدادات المجموعة!")
            return
        
        # تغيير الحالة
        chat.antiflood_enabled = not chat.antiflood_enabled
        await db.add_or_update_chat(chat)
        
        status = "مُفعل" if chat.antiflood_enabled else "مُعطل"
        emoji = config.EMOJI['check'] if chat.antiflood_enabled else config.EMOJI['cross']
        
        await message.reply(
            f"{emoji} مكافحة السبام الآن {status}\n"
            f"👮‍♂️ بواسطة: {message.from_user.full_name}"
        )
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@protection_router.message(Command("antilink"), AdminFilter())
async def toggle_antilink(message: Message, command: CommandObject):
    """تشغيل/إيقاف منع الروابط"""
    try:
        chat = await db.get_chat(message.chat.id)
        if not chat:
            await message.reply(f"{config.EMOJI['cross']} لم يتم العثور على إعدادات المجموعة!")
            return
        
        chat.antilink_enabled = not chat.antilink_enabled
        await db.add_or_update_chat(chat)
        
        status = "مُفعل" if chat.antilink_enabled else "مُعطل"
        emoji = config.EMOJI['check'] if chat.antilink_enabled else config.EMOJI['cross']
        
        await message.reply(
            f"{emoji} منع الروابط الآن {status}\n"
            f"👮‍♂️ بواسطة: {message.from_user.full_name}"
        )
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@protection_router.message(Command("antiword"), AdminFilter())
async def toggle_antiword(message: Message, command: CommandObject):
    """تشغيل/إيقاف منع الكلمات المحظورة"""
    try:
        chat = await db.get_chat(message.chat.id)
        if not chat:
            await message.reply(f"{config.EMOJI['cross']} لم يتم العثور على إعدادات المجموعة!")
            return
        
        chat.antiword_enabled = not chat.antiword_enabled
        await db.add_or_update_chat(chat)
        
        status = "مُفعل" if chat.antiword_enabled else "مُعطل"
        emoji = config.EMOJI['check'] if chat.antiword_enabled else config.EMOJI['cross']
        
        await message.reply(
            f"{emoji} منع الكلمات المحظورة الآن {status}\n"
            f"👮‍♂️ بواسطة: {message.from_user.full_name}"
        )
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@protection_router.message(Command("addword"), AdminFilter())
async def add_banned_word(message: Message, command: CommandObject):
    """إضافة كلمة محظورة"""
    try:
        if not command.args:
            await message.reply(
                f"{config.EMOJI['cross']} يرجى تحديد الكلمة المراد حظرها.\n"
                f"مثال: <code>/addword كلمة_محظورة</code>",
                parse_mode="HTML"
            )
            return
        
        word = command.args.strip().lower()
        
        chat = await db.get_chat(message.chat.id)
        if not chat:
            from database.models import Chat
            chat = Chat(chat_id=message.chat.id, title=message.chat.title)
        
        if word not in chat.banned_words:
            chat.banned_words.append(word)
            await db.add_or_update_chat(chat)
            
            await message.reply(
                f"{config.EMOJI['check']} تم إضافة الكلمة '{word}' إلى قائمة الكلمات المحظورة\n"
                f"👮‍♂️ بواسطة: {message.from_user.full_name}"
            )
        else:
            await message.reply(f"{config.EMOJI['warning']} الكلمة '{word}' موجودة بالفعل في القائمة!")
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@protection_router.message(Command("removeword"), AdminFilter())
async def remove_banned_word(message: Message, command: CommandObject):
    """إزالة كلمة من قائمة الكلمات المحظورة"""
    try:
        if not command.args:
            await message.reply(
                f"{config.EMOJI['cross']} يرجى تحديد الكلمة المراد إزالتها.\n"
                f"مثال: <code>/removeword كلمة_محظورة</code>",
                parse_mode="HTML"
            )
            return
        
        word = command.args.strip().lower()
        
        chat = await db.get_chat(message.chat.id)
        if not chat:
            await message.reply(f"{config.EMOJI['cross']} لم يتم العثور على إعدادات المجموعة!")
            return
        
        if word in chat.banned_words:
            chat.banned_words.remove(word)
            await db.add_or_update_chat(chat)
            
            await message.reply(
                f"{config.EMOJI['check']} تم إزالة الكلمة '{word}' من قائمة الكلمات المحظورة\n"
                f"👮‍♂️ بواسطة: {message.from_user.full_name}"
            )
        else:
            await message.reply(f"{config.EMOJI['warning']} الكلمة '{word}' غير موجودة في القائمة!")
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@protection_router.message(Command("bannedwords"))
async def list_banned_words(message: Message):
    """عرض قائمة الكلمات المحظورة"""
    try:
        chat = await db.get_chat(message.chat.id)
        if not chat or not chat.banned_words:
            await message.reply(f"{config.EMOJI['info']} لا توجد كلمات محظورة في هذه المجموعة.")
            return
        
        words_text = f"{config.EMOJI['warning']} الكلمات المحظورة في {message.chat.title}:\n\n"
        
        for i, word in enumerate(chat.banned_words, 1):
            words_text += f"{i}. {word}\n"
        
        words_text += f"\n📊 العدد الإجمالي: {len(chat.banned_words)} كلمة"
        
        await message.reply(words_text)
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@protection_router.message(Command("addlink"), AdminFilter())
async def add_allowed_link(message: Message, command: CommandObject):
    """إضافة رابط مسموح"""
    try:
        if not command.args:
            await message.reply(
                f"{config.EMOJI['cross']} يرجى تحديد الرابط المراد السماح به.\n"
                f"مثال: <code>/addlink example.com</code>",
                parse_mode="HTML"
            )
            return
        
        link = command.args.strip().lower()
        
        chat = await db.get_chat(message.chat.id)
        if not chat:
            from database.models import Chat
            chat = Chat(chat_id=message.chat.id, title=message.chat.title)
        
        if link not in chat.allowed_links:
            chat.allowed_links.append(link)
            await db.add_or_update_chat(chat)
            
            await message.reply(
                f"{config.EMOJI['check']} تم إضافة الرابط '{link}' إلى قائمة الروابط المسموحة\n"
                f"👮‍♂️ بواسطة: {message.from_user.full_name}"
            )
        else:
            await message.reply(f"{config.EMOJI['warning']} الرابط '{link}' موجود بالفعل في القائمة!")
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@protection_router.message(Command("protection"))
async def protection_panel(message: Message):
    """لوحة إعدادات الحماية"""
    try:
        chat = await db.get_chat(message.chat.id)
        if not chat:
            from database.models import Chat
            chat = Chat(chat_id=message.chat.id, title=message.chat.title)
            await db.add_or_update_chat(chat)
        
        status_text = f"{config.EMOJI['settings']} إعدادات الحماية - {message.chat.title}\n\n"
        
        # حالة مكافحة السبام
        flood_status = "🟢 مُفعل" if chat.antiflood_enabled else "🔴 مُعطل"
        status_text += f"🌊 مكافحة السبام: {flood_status}\n"
        
        # حالة منع الروابط
        link_status = "🟢 مُفعل" if chat.antilink_enabled else "🔴 مُعطل"
        status_text += f"🔗 منع الروابط: {link_status}\n"
        
        # حالة منع الكلمات
        word_status = "🟢 مُفعل" if chat.antiword_enabled else "🔴 مُعطل"
        status_text += f"🚫 منع الكلمات: {word_status}\n"
        
        # حالة التحذيرات
        warn_status = "🟢 مُفعل" if chat.warns_enabled else "🔴 مُعطل"
        status_text += f"⚠️ نظام التحذيرات: {warn_status}\n"
        
        status_text += f"\n📊 إحصائيات:\n"
        status_text += f"• الكلمات المحظورة: {len(chat.banned_words)}\n"
        status_text += f"• الروابط المسموحة: {len(chat.allowed_links)}\n"
        status_text += f"• الحد الأقصى للتحذيرات: {chat.max_warns}\n"
        
        await message.reply(
            status_text,
            reply_markup=get_protection_keyboard()
        )
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

# فلتر الرسائل للحماية
@protection_router.message(F.content_type == ContentType.TEXT)
async def message_filter(message: Message):
    """فلتر الرسائل للحماية من السبام والكلمات والروابط"""
    try:
        # تجاهل رسائل المشرفين والمطورين
        if await db.is_admin(message.from_user.id, message.chat.id) or message.from_user.id in config.SUDO_USERS:
            return
        
        chat = await db.get_chat(message.chat.id)
        if not chat:
            return
        
        # التحقق من السبام
        if chat.antiflood_enabled:
            if await check_flood(message):
                return  # تم التعامل مع السبام
        
        # التحقق من الروابط
        if chat.antilink_enabled:
            if await check_links(message, chat):
                return  # تم حذف الرسالة بسبب الرابط
        
        # التحقق من الكلمات المحظورة
        if chat.antiword_enabled:
            if await check_banned_words(message, chat):
                return  # تم حذف الرسالة بسبب كلمة محظورة
        
    except Exception as e:
        print(f"خطأ في فلتر الرسائل: {e}")

async def check_flood(message: Message) -> bool:
    """التحقق من السبام"""
    try:
        user_key = f"{message.chat.id}:{message.from_user.id}"
        current_time = time.time()
        
        # إنشاء أو تحديث قائمة الرسائل للمستخدم
        if user_key not in flood_storage:
            flood_storage[user_key] = []
        
        # إزالة الرسائل القديمة (أكبر من دقيقة)
        flood_storage[user_key] = [
            msg_time for msg_time in flood_storage[user_key]
            if current_time - msg_time < 60
        ]
        
        # إضافة الرسالة الحالية
        flood_storage[user_key].append(current_time)
        
        # التحقق من تجاوز الحد المسموح
        if len(flood_storage[user_key]) > config.FLOOD_LIMIT:
            # كتم المستخدم
            from aiogram.types import ChatPermissions
            await message.bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=message.from_user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=int(current_time + config.FLOOD_TIME)
            )
            
            # حذف الرسالة
            try:
                await message.delete()
            except:
                pass
            
            # إرسال تحذير
            await message.answer(
                f"{config.EMOJI['spam']} تم كتم {message.from_user.full_name} لمدة دقيقة بسبب السبام!",
                disable_notification=True
            )
            
            # تسجيل الحظر في قاعدة البيانات
            ban = Ban(
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                admin_id=message.bot.id,
                reason="السبام التلقائي",
                ban_type="mute",
                duration=config.FLOOD_TIME
            )
            await db.add_ban(ban)
            
            # مسح قائمة الرسائل
            flood_storage[user_key] = []
            
            return True
        
        return False
        
    except Exception as e:
        print(f"خطأ في فحص السبام: {e}")
        return False

async def check_links(message: Message, chat) -> bool:
    """التحقق من الروابط"""
    try:
        text = message.text or message.caption or ""
        
        # البحث عن روابط
        urls = extract_urls(text)
        if not urls and not is_url(text):
            return False
        
        # التحقق من الروابط المسموحة
        for url in urls:
            url_domain = url.lower()
            is_allowed = False
            
            for allowed_link in chat.allowed_links:
                if allowed_link in url_domain:
                    is_allowed = True
                    break
            
            if not is_allowed:
                # حذف الرسالة
                try:
                    await message.delete()
                except:
                    pass
                
                # إرسال تحذير
                warning_msg = await message.answer(
                    f"{config.EMOJI['cross']} {message.from_user.full_name}، الروابط غير مسموحة في هذه المجموعة!",
                    disable_notification=True
                )
                
                # حذف رسالة التحذير بعد 5 ثواني
                asyncio.create_task(delete_message_after(warning_msg, 5))
                
                return True
        
        return False
        
    except Exception as e:
        print(f"خطأ في فحص الروابط: {e}")
        return False

async def check_banned_words(message: Message, chat) -> bool:
    """التحقق من الكلمات المحظورة"""
    try:
        text = (message.text or message.caption or "").lower()
        
        if not text or not chat.banned_words:
            return False
        
        # البحث عن كلمات محظورة
        for banned_word in chat.banned_words:
            if banned_word in text:
                # حذف الرسالة
                try:
                    await message.delete()
                except:
                    pass
                
                # إرسال تحذير
                warning_msg = await message.answer(
                    f"{config.EMOJI['warning']} {message.from_user.full_name}، رسالتك تحتوي على كلمات غير مناسبة!",
                    disable_notification=True
                )
                
                # حذف رسالة التحذير بعد 5 ثواني
                asyncio.create_task(delete_message_after(warning_msg, 5))
                
                return True
        
        return False
        
    except Exception as e:
        print(f"خطأ في فحص الكلمات المحظورة: {e}")
        return False

async def delete_message_after(message: Message, seconds: int):
    """حذف الرسالة بعد وقت محدد"""
    try:
        await asyncio.sleep(seconds)
        await message.delete()
    except:
        pass
