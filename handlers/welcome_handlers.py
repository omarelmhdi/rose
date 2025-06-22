"""
معالجات رسائل الترحيب والوداع
"""
from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated, CallbackQuery
from aiogram.filters import ChatMemberUpdatedFilter, Command, CommandObject
from database import db, User
from config.config import config
from filters.admin_filter import AdminFilter
from keyboards.admin_keyboards import get_welcome_keyboard

# راوتر الترحيب
welcome_router = Router()

@welcome_router.chat_member(ChatMemberUpdatedFilter(member_status_changed=True))
async def on_user_joined(event: ChatMemberUpdated):
    """التعامل مع انضمام عضو جديد"""
    try:
        # التحقق من انضمام عضو جديد
        if (event.old_chat_member.status == "left" or 
            event.old_chat_member.status == "kicked") and \
           event.new_chat_member.status == "member":
            
            user = event.new_chat_member.user
            
            # تجاهل البوتات
            if user.is_bot:
                return
            
            # حفظ معلومات المستخدم في قاعدة البيانات
            await save_user_info(user)
            
            # جلب إعدادات المجموعة
            chat = await db.get_chat(event.chat.id)
            if not chat or not chat.welcome_enabled:
                return
            
            # إرسال رسالة الترحيب
            await send_welcome_message(event, user, chat)
            
    except Exception as e:
        print(f"خطأ في معالجة انضمام العضو: {e}")

@welcome_router.chat_member(ChatMemberUpdatedFilter(member_status_changed=True))
async def on_user_left(event: ChatMemberUpdated):
    """التعامل مع مغادرة عضو"""
    try:
        # التحقق من مغادرة عضو
        if event.new_chat_member.status in ["left", "kicked"] and \
           event.old_chat_member.status == "member":
            
            user = event.old_chat_member.user
            
            # تجاهل البوتات
            if user.is_bot:
                return
            
            # يمكن إضافة رسالة وداع هنا إذا رغبت
            # await send_goodbye_message(event, user)
            
    except Exception as e:
        print(f"خطأ في معالجة مغادرة العضو: {e}")

async def save_user_info(user):
    """حفظ معلومات المستخدم في قاعدة البيانات"""
    try:
        user_obj = User(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code,
            is_bot=user.is_bot,
            is_premium=getattr(user, 'is_premium', False)
        )
        
        await db.add_or_update_user(user_obj)
        
    except Exception as e:
        print(f"خطأ في حفظ معلومات المستخدم: {e}")

async def send_welcome_message(event: ChatMemberUpdated, user, chat):
    """إرسال رسالة الترحيب"""
    try:
        # النص الافتراضي للترحيب
        welcome_text = chat.welcome_message or config.DEFAULT_WELCOME_MESSAGE
        
        # استبدال المتغيرات في النص
        welcome_text = welcome_text.replace("{first_name}", user.first_name or "")
        welcome_text = welcome_text.replace("{last_name}", user.last_name or "")
        welcome_text = welcome_text.replace("{full_name}", f"{user.first_name or ''} {user.last_name or ''}".strip())
        welcome_text = welcome_text.replace("{username}", f"@{user.username}" if user.username else user.first_name or "العضو الجديد")
        welcome_text = welcome_text.replace("{user_id}", str(user.id))
        welcome_text = welcome_text.replace("{chat_title}", event.chat.title or "المجموعة")
        welcome_text = welcome_text.replace("{chat_id}", str(event.chat.id))
        
        # إضافة منشن للمستخدم
        user_mention = f"<a href='tg://user?id={user.id}'>{user.first_name or 'العضو الجديد'}</a>"
        
        # تنسيق الرسالة النهائية
        final_message = f"{config.EMOJI['welcome']} {welcome_text}"
        
        # إرسال الرسالة
        await event.answer(final_message, parse_mode="HTML")
        
    except Exception as e:
        print(f"خطأ في إرسال رسالة الترحيب: {e}")

@welcome_router.message(Command("welcome"), AdminFilter())
async def welcome_settings(message: Message, command: CommandObject):
    """إعدادات رسالة الترحيب"""
    try:
        if command.args:
            # إذا تم تمرير نص، قم بتحديث رسالة الترحيب
            new_message = command.args
            
            chat = await db.get_chat(message.chat.id)
            if not chat:
                from database.models import Chat
                chat = Chat(chat_id=message.chat.id, title=message.chat.title)
            
            chat.welcome_message = new_message
            await db.add_or_update_chat(chat)
            
            await message.reply(
                f"{config.EMOJI['check']} تم تحديث رسالة الترحيب!\n\n"
                f"📝 الرسالة الجديدة:\n{new_message}\n\n"
                f"💡 يمكنك استخدام المتغيرات التالية:\n"
                f"• <code>{{first_name}}</code> - الاسم الأول\n"
                f"• <code>{{last_name}}</code> - الاسم الأخير\n"
                f"• <code>{{full_name}}</code> - الاسم الكامل\n"
                f"• <code>{{username}}</code> - اسم المستخدم\n"
                f"• <code>{{chat_title}}</code> - اسم المجموعة\n"
                f"• <code>{{user_id}}</code> - معرف المستخدم",
                parse_mode="HTML"
            )
        else:
            # عرض إعدادات الترحيب
            chat = await db.get_chat(message.chat.id)
            current_message = chat.welcome_message if chat else config.DEFAULT_WELCOME_MESSAGE
            status = "مُفعل" if chat and chat.welcome_enabled else "مُعطل"
            
            settings_text = f"{config.EMOJI['welcome']} إعدادات الترحيب\n\n"
            settings_text += f"📊 الحالة: {status}\n\n"
            settings_text += f"📝 الرسالة الحالية:\n{current_message}\n\n"
            settings_text += f"💡 المتغيرات المتاحة:\n"
            settings_text += f"• <code>{{first_name}}</code> - الاسم الأول\n"
            settings_text += f"• <code>{{last_name}}</code> - الاسم الأخير\n"
            settings_text += f"• <code>{{full_name}}</code> - الاسم الكامل\n"
            settings_text += f"• <code>{{username}}</code> - اسم المستخدم\n"
            settings_text += f"• <code>{{chat_title}}</code> - اسم المجموعة\n"
            settings_text += f"• <code>{{user_id}}</code> - معرف المستخدم"
            
            await message.reply(
                settings_text,
                parse_mode="HTML",
                reply_markup=get_welcome_keyboard()
            )
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@welcome_router.message(Command("setwelcome"), AdminFilter())
async def set_welcome_message(message: Message, command: CommandObject):
    """تعيين رسالة ترحيب جديدة"""
    try:
        if not command.args:
            await message.reply(
                f"{config.EMOJI['cross']} يرجى تحديد نص رسالة الترحيب.\n"
                f"مثال: <code>/setwelcome مرحباً {{first_name}} في {{chat_title}}!</code>",
                parse_mode="HTML"
            )
            return
        
        new_message = command.args
        
        chat = await db.get_chat(message.chat.id)
        if not chat:
            from database.models import Chat
            chat = Chat(chat_id=message.chat.id, title=message.chat.title)
        
        chat.welcome_message = new_message
        chat.welcome_enabled = True  # تفعيل الترحيب تلقائياً
        await db.add_or_update_chat(chat)
        
        await message.reply(
            f"{config.EMOJI['check']} تم تحديث رسالة الترحيب وتفعيلها!\n\n"
            f"📝 الرسالة الجديدة:\n{new_message}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@welcome_router.message(Command("resetwelcome"), AdminFilter())
async def reset_welcome_message(message: Message):
    """إعادة تعيين رسالة الترحيب للافتراضية"""
    try:
        chat = await db.get_chat(message.chat.id)
        if not chat:
            from database.models import Chat
            chat = Chat(chat_id=message.chat.id, title=message.chat.title)
        
        chat.welcome_message = config.DEFAULT_WELCOME_MESSAGE
        await db.add_or_update_chat(chat)
        
        await message.reply(
            f"{config.EMOJI['check']} تم إعادة تعيين رسالة الترحيب للنص الافتراضي!\n\n"
            f"📝 الرسالة الافتراضية:\n{config.DEFAULT_WELCOME_MESSAGE}"
        )
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@welcome_router.message(Command("togglewelcome"), AdminFilter())
async def toggle_welcome(message: Message):
    """تشغيل/إيقاف رسائل الترحيب"""
    try:
        chat = await db.get_chat(message.chat.id)
        if not chat:
            from database.models import Chat
            chat = Chat(chat_id=message.chat.id, title=message.chat.title)
        
        chat.welcome_enabled = not chat.welcome_enabled
        await db.add_or_update_chat(chat)
        
        status = "مُفعل" if chat.welcome_enabled else "مُعطل"
        emoji = config.EMOJI['check'] if chat.welcome_enabled else config.EMOJI['cross']
        
        await message.reply(
            f"{emoji} رسائل الترحيب الآن {status}\n"
            f"👮‍♂️ بواسطة: {message.from_user.full_name}"
        )
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@welcome_router.message(Command("testwelcome"))
async def test_welcome_message(message: Message):
    """اختبار رسالة الترحيب"""
    try:
        chat = await db.get_chat(message.chat.id)
        if not chat:
            await message.reply(f"{config.EMOJI['info']} لم يتم تعيين رسالة ترحيب لهذه المجموعة.")
            return
        
        # محاكاة رسالة الترحيب
        welcome_text = chat.welcome_message or config.DEFAULT_WELCOME_MESSAGE
        
        # استبدال المتغيرات
        welcome_text = welcome_text.replace("{first_name}", message.from_user.first_name or "")
        welcome_text = welcome_text.replace("{last_name}", message.from_user.last_name or "")
        welcome_text = welcome_text.replace("{full_name}", message.from_user.full_name)
        welcome_text = welcome_text.replace("{username}", f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name)
        welcome_text = welcome_text.replace("{user_id}", str(message.from_user.id))
        welcome_text = welcome_text.replace("{chat_title}", message.chat.title or "المجموعة")
        welcome_text = welcome_text.replace("{chat_id}", str(message.chat.id))
        
        await message.reply(
            f"🧪 معاينة رسالة الترحيب:\n\n"
            f"{config.EMOJI['welcome']} {welcome_text}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

# معالجات الأزرار الإنلاين للترحيب
@welcome_router.callback_query(F.data == "welcome_enable")
async def enable_welcome_callback(callback: CallbackQuery):
    """تفعيل الترحيب"""
    try:
        chat = await db.get_chat(callback.message.chat.id)
        if not chat:
            from database.models import Chat
            chat = Chat(chat_id=callback.message.chat.id, title=callback.message.chat.title)
        
        chat.welcome_enabled = True
        await db.add_or_update_chat(chat)
        
        await callback.answer(f"{config.EMOJI['check']} تم تفعيل رسائل الترحيب!")
        
        # تحديث الرسالة
        await update_welcome_settings_message(callback.message)
        
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

@welcome_router.callback_query(F.data == "welcome_disable")
async def disable_welcome_callback(callback: CallbackQuery):
    """إيقاف الترحيب"""
    try:
        chat = await db.get_chat(callback.message.chat.id)
        if not chat:
            await callback.answer("لم يتم العثور على إعدادات المجموعة!", show_alert=True)
            return
        
        chat.welcome_enabled = False
        await db.add_or_update_chat(chat)
        
        await callback.answer(f"{config.EMOJI['cross']} تم إيقاف رسائل الترحيب!")
        
        # تحديث الرسالة
        await update_welcome_settings_message(callback.message)
        
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

@welcome_router.callback_query(F.data == "welcome_preview")
async def preview_welcome_callback(callback: CallbackQuery):
    """معاينة رسالة الترحيب"""
    try:
        chat = await db.get_chat(callback.message.chat.id)
        if not chat:
            await callback.answer("لم يتم تعيين رسالة ترحيب!", show_alert=True)
            return
        
        # محاكاة رسالة الترحيب
        welcome_text = chat.welcome_message or config.DEFAULT_WELCOME_MESSAGE
        
        # استبدال المتغيرات
        welcome_text = welcome_text.replace("{first_name}", callback.from_user.first_name or "")
        welcome_text = welcome_text.replace("{last_name}", callback.from_user.last_name or "")
        welcome_text = welcome_text.replace("{full_name}", callback.from_user.full_name)
        welcome_text = welcome_text.replace("{username}", f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.first_name)
        welcome_text = welcome_text.replace("{user_id}", str(callback.from_user.id))
        welcome_text = welcome_text.replace("{chat_title}", callback.message.chat.title or "المجموعة")
        welcome_text = welcome_text.replace("{chat_id}", str(callback.message.chat.id))
        
        preview_text = f"🧪 معاينة رسالة الترحيب:\n\n{config.EMOJI['welcome']} {welcome_text}"
        
        await callback.answer()
        await callback.message.answer(preview_text, parse_mode="HTML")
        
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def update_welcome_settings_message(message: Message):
    """تحديث رسالة إعدادات الترحيب"""
    try:
        chat = await db.get_chat(message.chat.id)
        current_message = chat.welcome_message if chat else config.DEFAULT_WELCOME_MESSAGE
        status = "مُفعل" if chat and chat.welcome_enabled else "مُعطل"
        
        settings_text = f"{config.EMOJI['welcome']} إعدادات الترحيب\n\n"
        settings_text += f"📊 الحالة: {status}\n\n"
        settings_text += f"📝 الرسالة الحالية:\n{current_message}\n\n"
        settings_text += f"💡 المتغيرات المتاحة:\n"
        settings_text += f"• <code>{{first_name}}</code> - الاسم الأول\n"
        settings_text += f"• <code>{{last_name}}</code> - الاسم الأخير\n"
        settings_text += f"• <code>{{full_name}}</code> - الاسم الكامل\n"
        settings_text += f"• <code>{{username}}</code> - اسم المستخدم\n"
        settings_text += f"• <code>{{chat_title}}</code> - اسم المجموعة\n"
        settings_text += f"• <code>{{user_id}}</code> - معرف المستخدم"
        
        await message.edit_text(
            settings_text,
            parse_mode="HTML",
            reply_markup=get_welcome_keyboard()
        )
        
    except Exception as e:
        print(f"خطأ في تحديث رسالة الإعدادات: {e}")
