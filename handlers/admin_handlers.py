"""
معالجات الأوامر الإدارية
"""
import asyncio
from datetime import datetime, timedelta
from typing import Union
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ChatMemberOwner, ChatMemberAdministrator
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramBadRequest
from database import db, Ban, Warning, Admin
from config.config import config
from filters.admin_filter import AdminFilter
from utils.helpers import parse_time, extract_user_and_reason, format_user_mention
from keyboards.admin_keyboards import get_admin_panel_keyboard, get_confirm_keyboard

# إنشاء راوتر للأوامر الإدارية
admin_router = Router()

@admin_router.message(Command("ban"), AdminFilter())
async def ban_user(message: Message, command: CommandObject):
    """أمر حظر المستخدم"""
    try:
        # استخراج المستخدم والسبب
        user_id, reason = await extract_user_and_reason(message, command.args)
        if not user_id:
            await message.reply(
                f"{config.EMOJI['cross']} يرجى تحديد المستخدم المراد حظره.\n"
                f"مثال: <code>/ban @username سبب الحظر</code>",
                parse_mode="HTML"
            )
            return
        
        # التحقق من عدم حظر المشرفين
        if await db.is_admin(user_id, message.chat.id):
            await message.reply(f"{config.EMOJI['cross']} لا يمكن حظر المشرفين!")
            return
        
        # التحقق من عدم حظر المطورين
        if user_id in config.SUDO_USERS:
            await message.reply(f"{config.EMOJI['cross']} لا يمكن حظر المطورين!")
            return
        
        # حظر المستخدم
        try:
            await message.bot.ban_chat_member(message.chat.id, user_id)
            
            # حفظ الحظر في قاعدة البيانات
            ban = Ban(
                user_id=user_id,
                chat_id=message.chat.id,
                admin_id=message.from_user.id,
                reason=reason or "لم يتم تحديد السبب",
                ban_type="ban"
            )
            await db.add_ban(ban)
            
            user_mention = await format_user_mention(user_id, message.bot)
            await message.reply(
                f"{config.EMOJI['ban']} تم حظر {user_mention}\n"
                f"📋 السبب: {reason or 'لم يتم تحديد السبب'}\n"
                f"👮‍♂️ بواسطة: {message.from_user.full_name}",
                parse_mode="HTML"
            )
            
        except TelegramBadRequest as e:
            await message.reply(f"{config.EMOJI['cross']} فشل في حظر المستخدم: {str(e)}")
            
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@admin_router.message(Command("unban"), AdminFilter())
async def unban_user(message: Message, command: CommandObject):
    """أمر إلغاء حظر المستخدم"""
    try:
        user_id, _ = await extract_user_and_reason(message, command.args)
        if not user_id:
            await message.reply(
                f"{config.EMOJI['cross']} يرجى تحديد المستخدم المراد إلغاء حظره.\n"
                f"مثال: <code>/unban @username</code>",
                parse_mode="HTML"
            )
            return
        
        # إلغاء الحظر
        try:
            await message.bot.unban_chat_member(message.chat.id, user_id, only_if_banned=True)
            await db.remove_ban(user_id, message.chat.id)
            
            user_mention = await format_user_mention(user_id, message.bot)
            await message.reply(
                f"{config.EMOJI['check']} تم إلغاء حظر {user_mention}\n"
                f"👮‍♂️ بواسطة: {message.from_user.full_name}",
                parse_mode="HTML"
            )
            
        except TelegramBadRequest as e:
            await message.reply(f"{config.EMOJI['cross']} فشل في إلغاء الحظر: {str(e)}")
            
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@admin_router.message(Command("kick"), AdminFilter())
async def kick_user(message: Message, command: CommandObject):
    """أمر طرد المستخدم"""
    try:
        user_id, reason = await extract_user_and_reason(message, command.args)
        if not user_id:
            await message.reply(
                f"{config.EMOJI['cross']} يرجى تحديد المستخدم المراد طرده.\n"
                f"مثال: <code>/kick @username سبب الطرد</code>",
                parse_mode="HTML"
            )
            return
        
        if await db.is_admin(user_id, message.chat.id):
            await message.reply(f"{config.EMOJI['cross']} لا يمكن طرد المشرفين!")
            return
        
        if user_id in config.SUDO_USERS:
            await message.reply(f"{config.EMOJI['cross']} لا يمكن طرد المطورين!")
            return
        
        try:
            # طرد المستخدم (حظر ثم إلغاء الحظر)
            await message.bot.ban_chat_member(message.chat.id, user_id)
            await asyncio.sleep(1)
            await message.bot.unban_chat_member(message.chat.id, user_id)
            
            user_mention = await format_user_mention(user_id, message.bot)
            await message.reply(
                f"{config.EMOJI['warning']} تم طرد {user_mention}\n"
                f"📋 السبب: {reason or 'لم يتم تحديد السبب'}\n"
                f"👮‍♂️ بواسطة: {message.from_user.full_name}",
                parse_mode="HTML"
            )
            
        except TelegramBadRequest as e:
            await message.reply(f"{config.EMOJI['cross']} فشل في طرد المستخدم: {str(e)}")
            
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@admin_router.message(Command("mute"), AdminFilter())
async def mute_user(message: Message, command: CommandObject):
    """أمر كتم المستخدم"""
    try:
        # تحليل الأمر لاستخراج المستخدم والمدة والسبب
        args = command.args.split() if command.args else []
        
        if len(args) < 1:
            await message.reply(
                f"{config.EMOJI['cross']} يرجى تحديد المستخدم والمدة.\n"
                f"مثال: <code>/mute @username 1h سبب الكتم</code>\n"
                f"أو: <code>/mute @username سبب الكتم</code> (كتم دائم)",
                parse_mode="HTML"
            )
            return
        
        user_id, remaining_args = await extract_user_and_reason(message, command.args)
        if not user_id:
            await message.reply(f"{config.EMOJI['cross']} لم يتم العثور على المستخدم!")
            return
        
        # استخراج المدة والسبب
        duration = None
        reason = None
        
        if remaining_args:
            args_list = remaining_args.split()
            # التحقق من وجود مدة في الأرغومنت الأول
            time_arg = args_list[0] if args_list else None
            parsed_time = parse_time(time_arg) if time_arg else None
            
            if parsed_time:
                duration = parsed_time
                reason = " ".join(args_list[1:]) if len(args_list) > 1 else None
            else:
                reason = remaining_args
        
        if await db.is_admin(user_id, message.chat.id):
            await message.reply(f"{config.EMOJI['cross']} لا يمكن كتم المشرفين!")
            return
        
        if user_id in config.SUDO_USERS:
            await message.reply(f"{config.EMOJI['cross']} لا يمكن كتم المطورين!")
            return
        
        try:
            # تحديد وقت انتهاء الكتم
            until_date = None
            if duration:
                until_date = datetime.now() + timedelta(seconds=duration)
            
            # كتم المستخدم
            from aiogram.types import ChatPermissions
            await message.bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            
            # حفظ الكتم في قاعدة البيانات
            ban = Ban(
                user_id=user_id,
                chat_id=message.chat.id,
                admin_id=message.from_user.id,
                reason=reason or "لم يتم تحديد السبب",
                ban_type="mute",
                duration=duration,
                expires_at=until_date
            )
            await db.add_ban(ban)
            
            user_mention = await format_user_mention(user_id, message.bot)
            duration_text = f"لمدة {format_duration(duration)}" if duration else "بشكل دائم"
            
            await message.reply(
                f"{config.EMOJI['mute']} تم كتم {user_mention} {duration_text}\n"
                f"📋 السبب: {reason or 'لم يتم تحديد السبب'}\n"
                f"👮‍♂️ بواسطة: {message.from_user.full_name}",
                parse_mode="HTML"
            )
            
        except TelegramBadRequest as e:
            await message.reply(f"{config.EMOJI['cross']} فشل في كتم المستخدم: {str(e)}")
            
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@admin_router.message(Command("unmute"), AdminFilter())
async def unmute_user(message: Message, command: CommandObject):
    """أمر إلغاء كتم المستخدم"""
    try:
        user_id, _ = await extract_user_and_reason(message, command.args)
        if not user_id:
            await message.reply(
                f"{config.EMOJI['cross']} يرجى تحديد المستخدم المراد إلغاء كتمه.\n"
                f"مثال: <code>/unmute @username</code>",
                parse_mode="HTML"
            )
            return
        
        try:
            # إلغاء كتم المستخدم
            from aiogram.types import ChatPermissions
            await message.bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=False,
                    can_invite_users=True,
                    can_pin_messages=False
                )
            )
            
            await db.remove_ban(user_id, message.chat.id)
            
            user_mention = await format_user_mention(user_id, message.bot)
            await message.reply(
                f"{config.EMOJI['check']} تم إلغاء كتم {user_mention}\n"
                f"👮‍♂️ بواسطة: {message.from_user.full_name}",
                parse_mode="HTML"
            )
            
        except TelegramBadRequest as e:
            await message.reply(f"{config.EMOJI['cross']} فشل في إلغاء الكتم: {str(e)}")
            
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@admin_router.message(Command("warn"), AdminFilter())
async def warn_user(message: Message, command: CommandObject):
    """أمر تحذير المستخدم"""
    try:
        user_id, reason = await extract_user_and_reason(message, command.args)
        if not user_id:
            await message.reply(
                f"{config.EMOJI['cross']} يرجى تحديد المستخدم المراد تحذيره.\n"
                f"مثال: <code>/warn @username سبب التحذير</code>",
                parse_mode="HTML"
            )
            return
        
        if await db.is_admin(user_id, message.chat.id):
            await message.reply(f"{config.EMOJI['cross']} لا يمكن تحذير المشرفين!")
            return
        
        if user_id in config.SUDO_USERS:
            await message.reply(f"{config.EMOJI['cross']} لا يمكن تحذير المطورين!")
            return
        
        # إضافة التحذير
        warning = Warning(
            user_id=user_id,
            chat_id=message.chat.id,
            admin_id=message.from_user.id,
            reason=reason or "لم يتم تحديد السبب"
        )
        await db.add_warning(warning)
        
        # جلب عدد التحذيرات الحالي
        warnings = await db.get_warnings(user_id, message.chat.id)
        warn_count = len(warnings)
        
        # جلب الحد الأقصى للتحذيرات
        chat = await db.get_chat(message.chat.id)
        max_warns = chat.max_warns if chat else config.MAX_WARNS
        
        user_mention = await format_user_mention(user_id, message.bot)
        
        # التحقق من الوصول للحد الأقصى
        if warn_count >= max_warns:
            # حظر المستخدم
            try:
                await message.bot.ban_chat_member(message.chat.id, user_id)
                
                ban = Ban(
                    user_id=user_id,
                    chat_id=message.chat.id,
                    admin_id=message.from_user.id,
                    reason=f"الوصول للحد الأقصى من التحذيرات ({max_warns})",
                    ban_type="ban"
                )
                await db.add_ban(ban)
                
                await message.reply(
                    f"{config.EMOJI['ban']} تم حظر {user_mention} بسبب الوصول للحد الأقصى من التحذيرات!\n"
                    f"⚠️ التحذيرات: {warn_count}/{max_warns}\n"
                    f"📋 آخر سبب: {reason or 'لم يتم تحديد السبب'}\n"
                    f"👮‍♂️ بواسطة: {message.from_user.full_name}",
                    parse_mode="HTML"
                )
            except TelegramBadRequest as e:
                await message.reply(f"{config.EMOJI['cross']} فشل في حظر المستخدم: {str(e)}")
        else:
            await message.reply(
                f"{config.EMOJI['warn']} تم تحذير {user_mention}\n"
                f"⚠️ التحذيرات: {warn_count}/{max_warns}\n"
                f"📋 السبب: {reason or 'لم يتم تحديد السبب'}\n"
                f"👮‍♂️ بواسطة: {message.from_user.full_name}",
                parse_mode="HTML"
            )
            
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@admin_router.message(Command("unwarn"), AdminFilter())
async def remove_warn(message: Message, command: CommandObject):
    """أمر إزالة تحذير"""
    try:
        user_id, _ = await extract_user_and_reason(message, command.args)
        if not user_id:
            await message.reply(
                f"{config.EMOJI['cross']} يرجى تحديد المستخدم المراد إزالة تحذيراته.\n"
                f"مثال: <code>/unwarn @username</code>",
                parse_mode="HTML"
            )
            return
        
        await db.clear_warnings(user_id, message.chat.id)
        
        user_mention = await format_user_mention(user_id, message.bot)
        await message.reply(
            f"{config.EMOJI['check']} تم مسح جميع تحذيرات {user_mention}\n"
            f"👮‍♂️ بواسطة: {message.from_user.full_name}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@admin_router.message(Command("pin"))
async def pin_message(message: Message):
    """أمر تثبيت الرسالة"""
    try:
        # التحقق من الصلاحيات
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        if not isinstance(member, (ChatMemberOwner, ChatMemberAdministrator)) or not member.can_pin_messages:
            if not await db.is_admin(message.from_user.id, message.chat.id):
                await message.reply(f"{config.EMOJI['cross']} ليس لديك صلاحية تثبيت الرسائل!")
                return
        
        # التحقق من وجود رد على رسالة
        if not message.reply_to_message:
            await message.reply(f"{config.EMOJI['cross']} يرجى الرد على الرسالة المراد تثبيتها!")
            return
        
        # تثبيت الرسالة
        await message.bot.pin_chat_message(
            chat_id=message.chat.id, 
            message_id=message.reply_to_message.message_id,
            disable_notification=True
        )
        
        await message.reply(
            f"{config.EMOJI['check']} تم تثبيت الرسالة!\n"
            f"👮‍♂️ بواسطة: {message.from_user.full_name}"
        )
        
    except TelegramBadRequest as e:
        await message.reply(f"{config.EMOJI['cross']} فشل في تثبيت الرسالة: {str(e)}")
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@admin_router.message(Command("unpin"))
async def unpin_message(message: Message):
    """أمر إلغاء تثبيت الرسالة"""
    try:
        # التحقق من الصلاحيات
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        if not isinstance(member, (ChatMemberOwner, ChatMemberAdministrator)) or not member.can_pin_messages:
            if not await db.is_admin(message.from_user.id, message.chat.id):
                await message.reply(f"{config.EMOJI['cross']} ليس لديك صلاحية إلغاء تثبيت الرسائل!")
                return
        
        # إلغاء تثبيت الرسالة
        if message.reply_to_message:
            await message.bot.unpin_chat_message(
                chat_id=message.chat.id, 
                message_id=message.reply_to_message.message_id
            )
        else:
            await message.bot.unpin_chat_message(chat_id=message.chat.id)
        
        await message.reply(
            f"{config.EMOJI['check']} تم إلغاء تثبيت الرسالة!\n"
            f"👮‍♂️ بواسطة: {message.from_user.full_name}"
        )
        
    except TelegramBadRequest as e:
        await message.reply(f"{config.EMOJI['cross']} فشل في إلغاء تثبيت الرسالة: {str(e)}")
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@admin_router.message(Command("adminlist"))
async def admin_list(message: Message):
    """عرض قائمة المشرفين"""
    try:
        # جلب المشرفين من تليجرام
        admins = await message.bot.get_chat_administrators(message.chat.id)
        
        admin_text = f"{config.EMOJI['admin']} قائمة المشرفين في {message.chat.title}:\n\n"
        
        for admin in admins:
            user = admin.user
            if user.is_bot:
                continue
            
            status = "👑 منشئ المجموعة" if isinstance(admin, ChatMemberOwner) else "👮‍♂️ مشرف"
            title = f" ({admin.custom_title})" if hasattr(admin, 'custom_title') and admin.custom_title else ""
            username = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
            
            admin_text += f"{status} {username}{title}\n"
        
        await message.reply(admin_text, parse_mode="Markdown")
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

def format_duration(seconds: int) -> str:
    """تنسيق المدة الزمنية"""
    if seconds < 60:
        return f"{seconds} ثانية"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} دقيقة"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} ساعة"
    else:
        days = seconds // 86400
        return f"{days} يوم"
