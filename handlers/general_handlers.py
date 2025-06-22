"""
معالجات الأوامر العامة
"""
from aiogram import Router, F
from aiogram.types import Message, User as TgUser
from aiogram.filters import Command, CommandStart
from database import db, User, Chat
from config.config import config
from keyboards.admin_keyboards import get_admin_panel_keyboard
from utils.helpers import format_file_size, format_datetime

# راوتر الأوامر العامة
general_router = Router()

@general_router.message(CommandStart())
async def start_command(message: Message):
    """أمر /start"""
    try:
        # حفظ معلومات المستخدم
        user = User(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code,
            is_bot=message.from_user.is_bot,
            is_premium=getattr(message.from_user, 'is_premium', False)
        )
        await db.add_or_update_user(user)
        
        # حفظ معلومات المجموعة إذا كانت المحادثة في مجموعة
        if message.chat.type in ["group", "supergroup"]:
            chat = Chat(
                chat_id=message.chat.id,
                title=message.chat.title,
                chat_type=message.chat.type,
                username=message.chat.username,
                description=message.chat.description
            )
            await db.add_or_update_chat(chat)
        
        # رسالة الترحيب
        if message.chat.type == "private":
            # في المحادثة الخاصة
            welcome_text = f"""
{config.EMOJI['welcome']} مرحباً {message.from_user.full_name}!

أنا بوت إدارة المجموعات المتقدم 🤖

🔧 أستطيع مساعدتك في:
• إدارة المجموعات والأعضاء
• حماية المجموعة من السبام والروابط
• تخصيص رسائل الترحيب
• نظام التحذيرات والعقوبات
• إحصائيات مفصلة

📖 للمساعدة: /help
⚙️ لوحة الإدارة: /admin (في المجموعات)

🚀 أضفني إلى مجموعتك واجعلني مشرف لتفعيل جميع الميزات!
            """
        else:
            # في المجموعة
            welcome_text = f"""
{config.EMOJI['welcome']} مرحباً! 

أنا بوت إدارة المجموعات الآن جاهز للعمل في {message.chat.title} 🎉

⚙️ لوحة الإدارة: /admin
📖 المساعدة: /help
🛡️ إعدادات الحماية: /protection

تأكد من أن لدي صلاحيات المشرف لأعمل بكامل قدراتي!
            """
        
        await message.reply(welcome_text)
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@general_router.message(Command("help"))
async def help_command(message: Message):
    """أمر المساعدة"""
    try:
        help_text = f"""
📖 دليل استخدام البوت

🔧 الأوامر الإدارية:
• /ban [مستخدم] [سبب] - حظر عضو
• /unban [مستخدم] - إلغاء حظر عضو
• /kick [مستخدم] [سبب] - طرد عضو
• /mute [مستخدم] [مدة] [سبب] - كتم عضو
• /unmute [مستخدم] - إلغاء كتم عضو
• /warn [مستخدم] [سبب] - تحذير عضو
• /unwarn [مستخدم] - إزالة تحذيرات
• /pin - تثبيت رسالة (رد على الرسالة)
• /unpin - إلغاء تثبيت رسالة

🛡️ أوامر الحماية:
• /protection - لوحة إعدادات الحماية
• /antiflood - تشغيل/إيقاف مكافحة السبام
• /antilink - تشغيل/إيقاف منع الروابط
• /antiword - تشغيل/إيقاف منع الكلمات
• /addword [كلمة] - إضافة كلمة محظورة
• /removeword [كلمة] - إزالة كلمة محظورة
• /bannedwords - عرض الكلمات المحظورة

👋 أوامر الترحيب:
• /welcome - إعدادات الترحيب
• /setwelcome [نص] - تعيين رسالة ترحيب
• /resetwelcome - إعادة تعيين للافتراضي
• /togglewelcome - تشغيل/إيقاف الترحيب
• /testwelcome - اختبار رسالة الترحيب

ℹ️ أوامر المعلومات:
• /info - معلومات المجموعة
• /adminlist - قائمة المشرفين
• /stats - إحصائيات المجموعة
• /admin - لوحة الإدارة الرئيسية

💡 المتغيرات في رسائل الترحيب:
• {{first_name}} - الاسم الأول
• {{last_name}} - الاسم الأخير
• {{full_name}} - الاسم الكامل
• {{username}} - اسم المستخدم
• {{chat_title}} - اسم المجموعة
• {{user_id}} - معرف المستخدم

⏰ تنسيقات الوقت:
• s = ثواني، m = دقائق، h = ساعات، d = أيام
• مثال: 30m = 30 دقيقة، 2h = ساعتان

🔐 ملاحظة: معظم الأوامر تتطلب صلاحيات إدارية.
        """
        
        await message.reply(help_text)
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@general_router.message(Command("admin"))
async def admin_panel(message: Message):
    """لوحة الإدارة الرئيسية"""
    try:
        # التحقق من كون المحادثة في مجموعة
        if message.chat.type == "private":
            await message.reply(
                f"{config.EMOJI['info']} لوحة الإدارة متاحة فقط في المجموعات!\n"
                f"أضفني إلى مجموعتك واستخدم /admin هناك."
            )
            return
        
        # التحقق من الصلاحيات
        if not await db.is_admin(message.from_user.id, message.chat.id):
            await message.reply(f"{config.EMOJI['cross']} ليس لديك صلاحية الوصول لهذه اللوحة!")
            return
        
        # جلب معلومات المجموعة
        chat = await db.get_chat(message.chat.id)
        if not chat:
            # إنشاء سجل جديد للمجموعة
            chat = Chat(
                chat_id=message.chat.id,
                title=message.chat.title,
                chat_type=message.chat.type,
                username=message.chat.username,
                description=message.chat.description
            )
            await db.add_or_update_chat(chat)
        
        # إعداد نص لوحة الإدارة
        admin_text = f"""
⚙️ لوحة إدارة {message.chat.title}

👮‍♂️ المشرف: {message.from_user.full_name}
🆔 معرف المجموعة: <code>{message.chat.id}</code>
👥 نوع المجموعة: {chat.chat_type}

📊 حالة الحماية:
• 🌊 مكافحة السبام: {"🟢" if chat.antiflood_enabled else "🔴"}
• 🔗 منع الروابط: {"🟢" if chat.antilink_enabled else "🔴"}
• 🚫 منع الكلمات: {"🟢" if chat.antiword_enabled else "🔴"}
• 👋 رسائل الترحيب: {"🟢" if chat.welcome_enabled else "🔴"}

اختر من الخيارات أدناه:
        """
        
        await message.reply(
            admin_text,
            parse_mode="HTML",
            reply_markup=get_admin_panel_keyboard()
        )
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@general_router.message(Command("info"))
async def group_info(message: Message):
    """معلومات المجموعة"""
    try:
        if message.chat.type == "private":
            # معلومات المستخدم في المحادثة الخاصة
            user_info = f"""
ℹ️ معلوماتك الشخصية:

👤 الاسم: {message.from_user.full_name}
🆔 المعرف: <code>{message.from_user.id}</code>
👤 اسم المستخدم: @{message.from_user.username or 'غير محدد'}
🌐 اللغة: {message.from_user.language_code or 'غير محدد'}
💎 البريميوم: {"نعم" if getattr(message.from_user, 'is_premium', False) else "لا"}
            """
            await message.reply(user_info, parse_mode="HTML")
            return
        
        # معلومات المجموعة
        try:
            chat_member_count = await message.bot.get_chat_member_count(message.chat.id)
            admins = await message.bot.get_chat_administrators(message.chat.id)
            admin_count = len([admin for admin in admins if not admin.user.is_bot])
        except:
            chat_member_count = "غير معروف"
            admin_count = "غير معروف"
        
        # جلب إعدادات المجموعة من قاعدة البيانات
        chat = await db.get_chat(message.chat.id)
        
        group_info_text = f"""
ℹ️ معلومات {message.chat.title}

🆔 معرف المجموعة: <code>{message.chat.id}</code>
👥 عدد الأعضاء: {chat_member_count}
👮‍♂️ عدد المشرفين: {admin_count}
📱 نوع المجموعة: {message.chat.type}
👤 اسم المستخدم: @{message.chat.username or 'غير محدد'}

📝 الوصف: {message.chat.description or 'غير محدد'}

🛡️ إعدادات الحماية:
• مكافحة السبام: {"🟢 مُفعل" if chat and chat.antiflood_enabled else "🔴 مُعطل"}
• منع الروابط: {"🟢 مُفعل" if chat and chat.antilink_enabled else "🔴 مُعطل"}
• منع الكلمات: {"🟢 مُفعل" if chat and chat.antiword_enabled else "🔴 مُعطل"}
• رسائل الترحيب: {"🟢 مُفعل" if chat and chat.welcome_enabled else "🔴 مُعطل"}

📊 إحصائيات:
• الكلمات المحظورة: {len(chat.banned_words) if chat else 0}
• الروابط المسموحة: {len(chat.allowed_links) if chat else 0}
• الحد الأقصى للتحذيرات: {chat.max_warns if chat else config.MAX_WARNS}
        """
        
        await message.reply(group_info_text, parse_mode="HTML")
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@general_router.message(Command("stats"))
async def group_stats(message: Message):
    """إحصائيات المجموعة"""
    try:
        if message.chat.type == "private":
            await message.reply(f"{config.EMOJI['info']} الإحصائيات متاحة فقط في المجموعات!")
            return
        
        # جلب إحصائيات من قاعدة البيانات
        chat_id = message.chat.id
        
        # عدد التحذيرات النشطة
        try:
            warnings_result = await db.supabase.table("warnings").select("*").eq("chat_id", chat_id).execute()
            total_warnings = len(warnings_result.data) if warnings_result.data else 0
        except:
            total_warnings = 0
        
        # عدد الحظر النشط
        try:
            bans_result = await db.supabase.table("bans").select("*").eq("chat_id", chat_id).eq("is_active", True).execute()
            active_bans = len(bans_result.data) if bans_result.data else 0
        except:
            active_bans = 0
        
        # عدد المشرفين في قاعدة البيانات
        try:
            admins_result = await db.supabase.table("admins").select("*").eq("chat_id", chat_id).execute()
            db_admins = len(admins_result.data) if admins_result.data else 0
        except:
            db_admins = 0
        
        # معلومات من تليجرام
        try:
            member_count = await message.bot.get_chat_member_count(chat_id)
            tg_admins = await message.bot.get_chat_administrators(chat_id)
            admin_count = len([admin for admin in tg_admins if not admin.user.is_bot])
        except:
            member_count = "غير معروف"
            admin_count = "غير معروف"
        
        stats_text = f"""
📊 إحصائيات {message.chat.title}

👥 الأعضاء والإدارة:
• إجمالي الأعضاء: {member_count}
• المشرفين النشطين: {admin_count}
• المشرفين في قاعدة البيانات: {db_admins}

⚠️ الإجراءات التأديبية:
• التحذيرات الإجمالية: {total_warnings}
• الحظر النشط: {active_bans}

🛡️ الحماية والأمان:
• حالة مكافحة السبام: {"🟢 نشط" if (await db.get_chat(chat_id)) and (await db.get_chat(chat_id)).antiflood_enabled else "🔴 معطل"}
• حالة منع الروابط: {"🟢 نشط" if (await db.get_chat(chat_id)) and (await db.get_chat(chat_id)).antilink_enabled else "🔴 معطل"}
• حالة منع الكلمات: {"🟢 نشط" if (await db.get_chat(chat_id)) and (await db.get_chat(chat_id)).antiword_enabled else "🔴 معطل"}

📈 الأنشطة:
• عدد الكلمات المحظورة: {len((await db.get_chat(chat_id)).banned_words) if await db.get_chat(chat_id) else 0}
• عدد الروابط المسموحة: {len((await db.get_chat(chat_id)).allowed_links) if await db.get_chat(chat_id) else 0}

🕒 آخر تحديث: الآن
        """
        
        await message.reply(stats_text)
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@general_router.message(Command("id"))
async def get_id(message: Message):
    """الحصول على معرفات مختلفة"""
    try:
        id_text = f"""
🆔 معلومات المعرفات

👤 معرفك: <code>{message.from_user.id}</code>
💬 معرف المحادثة: <code>{message.chat.id}</code>
        """
        
        # إذا كان رد على رسالة
        if message.reply_to_message:
            replied_user = message.reply_to_message.from_user
            id_text += f"\n👤 معرف {replied_user.full_name}: <code>{replied_user.id}</code>"
        
        # إذا كانت في مجموعة
        if message.chat.type in ["group", "supergroup"]:
            id_text += f"\n👥 اسم المجموعة: {message.chat.title}"
            if message.chat.username:
                id_text += f"\n🔗 رابط المجموعة: @{message.chat.username}"
        
        await message.reply(id_text, parse_mode="HTML")
        
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

@general_router.message(Command("ping"))
async def ping_command(message: Message):
    """اختبار استجابة البوت"""
    try:
        await message.reply(f"{config.EMOJI['check']} البوت يعمل بشكل طبيعي! 🏓")
    except Exception as e:
        await message.reply(f"{config.EMOJI['cross']} حدث خطأ: {str(e)}")

# معالج الرسائل العادية (يجب أن يكون في النهاية)
@general_router.message()
async def handle_regular_message(message: Message):
    """معالج الرسائل العادية - لحفظ نشاط المستخدم"""
    try:
        # حفظ نشاط المستخدم في قاعدة البيانات
        if message.from_user and not message.from_user.is_bot:
            user = User(
                user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code,
                is_bot=False,
                is_premium=getattr(message.from_user, 'is_premium', False)
            )
            await db.add_or_update_user(user)
        
        # تحديث معلومات المجموعة
        if message.chat.type in ["group", "supergroup"]:
            chat = await db.get_chat(message.chat.id)
            if not chat:
                chat = Chat(
                    chat_id=message.chat.id,
                    title=message.chat.title,
                    chat_type=message.chat.type,
                    username=message.chat.username,
                    description=message.chat.description
                )
                await db.add_or_update_chat(chat)
        
    except Exception as e:
        # لا نريد إرسال رسائل خطأ للرسائل العادية
        print(f"خطأ في معالجة الرسالة العادية: {e}")
