"""
معالجات الأزرار الإنلاين (Callbacks)
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import db
from config.config import config
from filters.admin_filter import AdminFilter
from keyboards.admin_keyboards import (
    get_admin_panel_keyboard, get_protection_keyboard, 
    get_welcome_keyboard, get_admin_management_keyboard,
    get_member_management_keyboard, get_notes_keyboard,
    get_stats_keyboard, get_general_settings_keyboard
)

# راوتر الكولباكات
callback_router = Router()

# فلتر للتحقق من صلاحيات الإدارة في الكولباكات
@callback_router.callback_query(F.data.startswith(("admin_", "protection_", "welcome_")))
async def admin_callback_filter(callback: CallbackQuery):
    """فلتر للتحقق من الصلاحيات في الكولباكات الإدارية"""
    if not await db.is_admin(callback.from_user.id, callback.message.chat.id):
        await callback.answer(f"{config.EMOJI['cross']} ليس لديك صلاحية لاستخدام هذا الخيار!", show_alert=True)
        return
    
    # تمرير للمعالج المناسب
    await handle_admin_callbacks(callback)

async def handle_admin_callbacks(callback: CallbackQuery):
    """معالج الكولباكات الإدارية"""
    try:
        data = callback.data
        
        # لوحة الإدارة الرئيسية
        if data == "admin_back":
            await show_admin_panel(callback)
        elif data == "admin_close":
            await callback.message.delete()
            await callback.answer()
            
        # إعدادات الحماية
        elif data == "admin_protection":
            await show_protection_panel(callback)
        elif data.startswith("protection_"):
            await handle_protection_callbacks(callback)
            
        # إدارة المشرفين
        elif data == "admin_admins":
            await show_admin_management(callback)
        elif data.startswith("admins_"):
            await handle_admin_management_callbacks(callback)
            
        # إدارة الأعضاء
        elif data == "admin_members":
            await show_member_management(callback)
        elif data.startswith("members_"):
            await handle_member_management_callbacks(callback)
            
        # الترحيب
        elif data == "admin_welcome":
            await show_welcome_settings(callback)
        elif data.startswith("welcome_"):
            # تم التعامل معها في welcome_handlers.py
            pass
            
        # الملاحظات والفلاتر
        elif data == "admin_notes":
            await show_notes_panel(callback)
        elif data.startswith("notes_"):
            await handle_notes_callbacks(callback)
            
        # الإحصائيات
        elif data == "admin_stats":
            await show_stats_panel(callback)
        elif data.startswith("stats_"):
            await handle_stats_callbacks(callback)
            
        # الإعدادات العامة
        elif data == "admin_general":
            await show_general_settings(callback)
        elif data.startswith("settings_"):
            await handle_settings_callbacks(callback)
            
        else:
            await callback.answer("خيار غير معروف!", show_alert=True)
            
    except Exception as e:
        await callback.answer(f"حدث خطأ: {str(e)}", show_alert=True)

async def show_admin_panel(callback: CallbackQuery):
    """عرض لوحة الإدارة الرئيسية"""
    try:
        chat = await db.get_chat(callback.message.chat.id)
        if not chat:
            from database.models import Chat
            chat = Chat(
                chat_id=callback.message.chat.id,
                title=callback.message.chat.title
            )
            await db.add_or_update_chat(chat)
        
        admin_text = f"""
⚙️ لوحة إدارة {callback.message.chat.title}

👮‍♂️ المشرف: {callback.from_user.full_name}
🆔 معرف المجموعة: <code>{callback.message.chat.id}</code>

📊 حالة الحماية:
• 🌊 مكافحة السبام: {"🟢" if chat.antiflood_enabled else "🔴"}
• 🔗 منع الروابط: {"🟢" if chat.antilink_enabled else "🔴"}
• 🚫 منع الكلمات: {"🟢" if chat.antiword_enabled else "🔴"}
• 👋 رسائل الترحيب: {"🟢" if chat.welcome_enabled else "🔴"}

اختر من الخيارات أدناه:
        """
        
        await callback.message.edit_text(
            admin_text,
            parse_mode="HTML",
            reply_markup=get_admin_panel_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def show_protection_panel(callback: CallbackQuery):
    """عرض لوحة إعدادات الحماية"""
    try:
        chat = await db.get_chat(callback.message.chat.id)
        if not chat:
            from database.models import Chat
            chat = Chat(chat_id=callback.message.chat.id, title=callback.message.chat.title)
            await db.add_or_update_chat(chat)
        
        status_text = f"{config.EMOJI['settings']} إعدادات الحماية - {callback.message.chat.title}\n\n"
        
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
        
        await callback.message.edit_text(
            status_text,
            reply_markup=get_protection_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def handle_protection_callbacks(callback: CallbackQuery):
    """معالجة كولباكات الحماية"""
    try:
        data = callback.data
        chat = await db.get_chat(callback.message.chat.id)
        
        if not chat:
            await callback.answer("لم يتم العثور على إعدادات المجموعة!", show_alert=True)
            return
        
        if data == "protection_antiflood":
            chat.antiflood_enabled = not chat.antiflood_enabled
            await db.add_or_update_chat(chat)
            status = "تم تفعيل" if chat.antiflood_enabled else "تم إيقاف"
            await callback.answer(f"{status} مكافحة السبام!")
            
        elif data == "protection_antilink":
            chat.antilink_enabled = not chat.antilink_enabled
            await db.add_or_update_chat(chat)
            status = "تم تفعيل" if chat.antilink_enabled else "تم إيقاف"
            await callback.answer(f"{status} منع الروابط!")
            
        elif data == "protection_antiword":
            chat.antiword_enabled = not chat.antiword_enabled
            await db.add_or_update_chat(chat)
            status = "تم تفعيل" if chat.antiword_enabled else "تم إيقاف"
            await callback.answer(f"{status} منع الكلمات!")
            
        elif data == "protection_warns":
            chat.warns_enabled = not chat.warns_enabled
            await db.add_or_update_chat(chat)
            status = "تم تفعيل" if chat.warns_enabled else "تم إيقاف"
            await callback.answer(f"{status} نظام التحذيرات!")
            
        elif data == "protection_banned_words":
            words_text = "📝 الكلمات المحظورة:\n\n"
            if chat.banned_words:
                for i, word in enumerate(chat.banned_words, 1):
                    words_text += f"{i}. {word}\n"
                words_text += f"\n📊 العدد الإجمالي: {len(chat.banned_words)}"
            else:
                words_text += "لا توجد كلمات محظورة"
            
            await callback.answer()
            await callback.message.answer(words_text)
            return
            
        elif data == "protection_allowed_links":
            links_text = "✅ الروابط المسموحة:\n\n"
            if chat.allowed_links:
                for i, link in enumerate(chat.allowed_links, 1):
                    links_text += f"{i}. {link}\n"
                links_text += f"\n📊 العدد الإجمالي: {len(chat.allowed_links)}"
            else:
                links_text += "لا توجد روابط مسموحة"
            
            await callback.answer()
            await callback.message.answer(links_text)
            return
        
        # تحديث لوحة الحماية
        await show_protection_panel(callback)
        
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def show_welcome_settings(callback: CallbackQuery):
    """عرض إعدادات الترحيب"""
    try:
        chat = await db.get_chat(callback.message.chat.id)
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
        
        await callback.message.edit_text(
            settings_text,
            parse_mode="HTML",
            reply_markup=get_welcome_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def show_admin_management(callback: CallbackQuery):
    """عرض لوحة إدارة المشرفين"""
    try:
        admin_text = f"""
👮‍♂️ إدارة المشرفين - {callback.message.chat.title}

من هنا يمكنك إدارة المشرفين في المجموعة:
• عرض قائمة المشرفين الحاليين
• إضافة مشرفين جدد إلى قاعدة البيانات
• إزالة مشرفين من قاعدة البيانات
• تعديل رتب ووظائف المشرفين

ملاحظة: هذا يؤثر على قاعدة بيانات البوت، وليس على صلاحيات تليجرام الفعلية.
        """
        
        await callback.message.edit_text(
            admin_text,
            reply_markup=get_admin_management_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def show_member_management(callback: CallbackQuery):
    """عرض لوحة إدارة الأعضاء"""
    try:
        member_text = f"""
👥 إدارة الأعضاء - {callback.message.chat.title}

من هنا يمكنك إدارة الأعضاء في المجموعة:
• عرض قائمة المحظورين
• عرض قائمة المكتومين
• إدارة التحذيرات
• تنظيف الحسابات المحذوفة

اختر الخيار المناسب من الأسفل:
        """
        
        await callback.message.edit_text(
            member_text,
            reply_markup=get_member_management_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def show_notes_panel(callback: CallbackQuery):
    """عرض لوحة الملاحظات والفلاتر"""
    try:
        notes_text = f"""
📝 الملاحظات والفلاتر - {callback.message.chat.title}

من هنا يمكنك إدارة:
• الملاحظات المحفوظة (#note_name)
• الفلاتر المخصصة (كلمة → رد)
• الردود التلقائية

الملاحظات والفلاتر تساعد في تنظيم المحتوى وتوفير معلومات سريعة للأعضاء.
        """
        
        await callback.message.edit_text(
            notes_text,
            reply_markup=get_notes_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def show_stats_panel(callback: CallbackQuery):
    """عرض لوحة الإحصائيات"""
    try:
        stats_text = f"""
📊 الإحصائيات - {callback.message.chat.title}

عرض إحصائيات مفصلة عن:
• الأعضاء والأنشطة
• الإجراءات التأديبية
• استخدام الأوامر
• الإحصائيات الزمنية

اختر نوع الإحصائيات التي تريد عرضها:
        """
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=get_stats_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def show_general_settings(callback: CallbackQuery):
    """عرض الإعدادات العامة"""
    try:
        settings_text = f"""
🔧 الإعدادات العامة - {callback.message.chat.title}

تخصيص البوت وإعداداته:
• تخصيص الرسائل والردود
• إعدادات اللغة والمنطقة الزمنية
• إدارة الوسائط والملفات
• النسخ الاحتياطي والاستعادة

اختر الإعداد الذي تريد تعديله:
        """
        
        await callback.message.edit_text(
            settings_text,
            reply_markup=get_general_settings_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def handle_admin_management_callbacks(callback: CallbackQuery):
    """معالجة كولباكات إدارة المشرفين"""
    try:
        data = callback.data
        
        if data == "admins_list":
            # عرض قائمة المشرفين
            admins = await db.get_admins(callback.message.chat.id)
            
            if not admins:
                await callback.answer("لا توجد مشرفين في قاعدة البيانات", show_alert=True)
                return
            
            admins_text = f"👮‍♂️ المشرفين في قاعدة البيانات:\n\n"
            for admin in admins:
                try:
                    user = await callback.bot.get_chat(admin.user_id)
                    name = user.full_name if hasattr(user, 'full_name') else f"المستخدم {admin.user_id}"
                    admins_text += f"• {name} ({admin.rank})\n"
                except:
                    admins_text += f"• المستخدم {admin.user_id} ({admin.rank})\n"
            
            await callback.answer()
            await callback.message.answer(admins_text)
            
        else:
            await callback.answer("هذه الميزة قيد التطوير", show_alert=True)
            
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def handle_member_management_callbacks(callback: CallbackQuery):
    """معالجة كولباكات إدارة الأعضاء"""
    try:
        data = callback.data
        
        if data == "members_banned":
            # عرض المحظورين
            await callback.answer("عرض قائمة المحظورين...")
            # TODO: تنفيذ عرض المحظورين
            
        elif data == "members_muted":
            # عرض المكتومين
            await callback.answer("عرض قائمة المكتومين...")
            # TODO: تنفيذ عرض المكتومين
            
        elif data == "members_warnings":
            # عرض التحذيرات
            await callback.answer("عرض التحذيرات...")
            # TODO: تنفيذ عرض التحذيرات
            
        else:
            await callback.answer("هذه الميزة قيد التطوير", show_alert=True)
            
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def handle_notes_callbacks(callback: CallbackQuery):
    """معالجة كولباكات الملاحظات"""
    try:
        await callback.answer("هذه الميزة قيد التطوير", show_alert=True)
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def handle_stats_callbacks(callback: CallbackQuery):
    """معالجة كولباكات الإحصائيات"""
    try:
        await callback.answer("هذه الميزة قيد التطوير", show_alert=True)
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

async def handle_settings_callbacks(callback: CallbackQuery):
    """معالجة كولباكات الإعدادات"""
    try:
        await callback.answer("هذه الميزة قيد التطوير", show_alert=True)
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

# كولباك عام لإلغاء الإجراءات
@callback_router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: CallbackQuery):
    """إلغاء الإجراء"""
    try:
        await callback.message.delete()
        await callback.answer("تم إلغاء الإجراء")
    except Exception as e:
        await callback.answer(f"خطأ: {str(e)}", show_alert=True)

# كولباك لمعلومات الصفحة
@callback_router.callback_query(F.data == "page_info")
async def page_info(callback: CallbackQuery):
    """معلومات الصفحة"""
    await callback.answer("معلومات الصفحة الحالية")
