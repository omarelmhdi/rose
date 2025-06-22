"""
ملف البوت الرئيسي
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, BotCommand
from config.config import config, validate_config
from database import db
from handlers.admin_handlers import admin_router
from handlers.protection_handlers import protection_router
from handlers.welcome_handlers import welcome_router
from handlers.general_handlers import general_router
from handlers.callback_handlers import callback_router

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# إنشاء البوت والديسباتشر
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

async def set_bot_commands():
    """تعيين أوامر البوت"""
    commands = [
        # الأوامر العامة
        BotCommand(command="start", description="🚀 بدء البوت"),
        BotCommand(command="help", description="❓ المساعدة"),
        BotCommand(command="admin", description="⚙️ لوحة الإدارة"),
        
        # أوامر الإدارة
        BotCommand(command="ban", description="🚫 حظر عضو"),
        BotCommand(command="unban", description="✅ إلغاء حظر عضو"),
        BotCommand(command="kick", description="👢 طرد عضو"),
        BotCommand(command="mute", description="🔇 كتم عضو"),
        BotCommand(command="unmute", description="🔊 إلغاء كتم عضو"),
        BotCommand(command="warn", description="⚠️ تحذير عضو"),
        BotCommand(command="unwarn", description="✅ إزالة تحذيرات"),
        BotCommand(command="pin", description="📌 تثبيت رسالة"),
        BotCommand(command="unpin", description="📌 إلغاء تثبيت"),
        
        # أوامر الحماية
        BotCommand(command="protection", description="🛡️ إعدادات الحماية"),
        BotCommand(command="antiflood", description="🌊 مكافحة السبام"),
        BotCommand(command="antilink", description="🔗 منع الروابط"),
        BotCommand(command="antiword", description="🚫 منع الكلمات"),
        
        # أوامر الترحيب
        BotCommand(command="welcome", description="👋 إعدادات الترحيب"),
        BotCommand(command="setwelcome", description="📝 تعيين رسالة ترحيب"),
        BotCommand(command="testwelcome", description="🧪 اختبار الترحيب"),
        
        # أوامر أخرى
        BotCommand(command="adminlist", description="👥 قائمة المشرفين"),
        BotCommand(command="info", description="ℹ️ معلومات المجموعة"),
        BotCommand(command="stats", description="📊 الإحصائيات"),
    ]
    
    await bot.set_my_commands(commands)
    logger.info("تم تعيين أوامر البوت بنجاح")

async def on_startup():
    """وظائف بدء التشغيل"""
    try:
        # التحقق من صحة الإعدادات
        validate_config()
        logger.info("تم التحقق من الإعدادات بنجاح")
        
        # إنشاء جداول قاعدة البيانات
        await db.create_tables()
        logger.info("تم التحقق من قاعدة البيانات")
        
        # تعيين أوامر البوت
        await set_bot_commands()
        
        # إرسال رسالة بدء التشغيل
        for sudo_user in config.SUDO_USERS:
            try:
                await bot.send_message(
                    sudo_user, 
                    f"🚀 تم بدء تشغيل البوت بنجاح!\n"
                    f"⏰ الوقت: {config.EMOJI['info']}\n"
                    f"🤖 اسم البوت: @{config.BOT_USERNAME}"
                )
            except:
                pass
        
        logger.info("تم بدء تشغيل البوت بنجاح!")
        
    except Exception as e:
        logger.error(f"خطأ في بدء التشغيل: {e}")
        raise

async def on_shutdown():
    """وظائف إيقاف التشغيل"""
    try:
        # إرسال رسالة إيقاف التشغيل
        for sudo_user in config.SUDO_USERS:
            try:
                await bot.send_message(
                    sudo_user, 
                    f"⏹️ تم إيقاف تشغيل البوت\n"
                    f"⏰ الوقت: {config.EMOJI['info']}"
                )
            except:
                pass
        
        logger.info("تم إيقاف تشغيل البوت")
        
    except Exception as e:
        logger.error(f"خطأ في إيقاف التشغيل: {e}")

async def main():
    """الوظيفة الرئيسية"""
    try:
        # تسجيل الراوترز
        dp.include_router(admin_router)
        dp.include_router(protection_router)
        dp.include_router(welcome_router)
        dp.include_router(general_router)
        dp.include_router(callback_router)
        
        # تسجيل أحداث بدء وإيقاف التشغيل
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        logger.info("بدء تشغيل البوت...")
        
        # بدء البوت
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")
        raise
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {e}")
