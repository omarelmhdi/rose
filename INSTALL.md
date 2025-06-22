# 📋 دليل التثبيت والتشغيل على PythonAnywhere

## 🎯 متطلبات أساسية

قبل البدء، تأكد من أن لديك:
- [x] حساب على [PythonAnywhere](https://www.pythonanywhere.com)
- [x] بوت تليجرام من [BotFather](https://t.me/BotFather)
- [x] حساب على [Supabase](https://supabase.com)

## 🚀 خطوات التثبيت

### 1. إنشاء البوت على تليجرام

#### أ. إنشاء البوت
1. ابحث عن [@BotFather](https://t.me/BotFather) في تليجرام
2. أرسل `/newbot`
3. اختر اسم للبوت (مثل: مدير المجموعات)
4. اختر username للبوت (يجب أن ينتهي بـ bot)
5. احفظ الـ Token الذي ستحصل عليه

#### ب. إعداد صلاحيات البوت
```
/setcommands
اختر البوت الخاص بك
```
ثم أرسل قائمة الأوامر:
```
start - 🚀 بدء البوت
help - ❓ المساعدة والأوامر
admin - ⚙️ لوحة الإدارة
ban - 🚫 حظر عضو
unban - ✅ إلغاء حظر
kick - 👢 طرد عضو
mute - 🔇 كتم عضو
unmute - 🔊 إلغاء كتم
warn - ⚠️ تحذير عضو
unwarn - ✅ إزالة تحذيرات
pin - 📌 تثبيت رسالة
unpin - 📌 إلغاء تثبيت
protection - 🛡️ إعدادات الحماية
welcome - 👋 إعدادات الترحيب
info - ℹ️ معلومات المجموعة
stats - 📊 الإحصائيات
```

### 2. إعداد قاعدة البيانات Supabase

#### أ. إنشاء مشروع جديد
1. اذهب إلى [supabase.com](https://supabase.com)
2. سجل الدخول أو أنشئ حساب جديد
3. اضغط "New Project"
4. اختر Organization أو أنشئ واحدة جديدة
5. املأ بيانات المشروع:
   - **Name**: Telegram Bot DB
   - **Database Password**: كلمة مرور قوية (احفظها!)
   - **Region**: اختر المنطقة الأقرب لك

#### ب. الحصول على بيانات الاتصال
1. بعد إنشاء المشروع، اذهب إلى **Settings** > **API**
2. احفظ:
   - **Project URL** (سيكون مثل: https://xxx.supabase.co)
   - **Project API keys** > **anon public** (المفتاح العام)

#### ج. إنشاء الجداول
1. اذهب إلى **SQL Editor** في لوحة تحكم Supabase
2. انسخ والصق الكود التالي واضغط **Run**:

```sql
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

-- إنشاء indexes لتحسين الأداء
CREATE INDEX IF NOT EXISTS idx_warnings_user_chat ON warnings(user_id, chat_id);
CREATE INDEX IF NOT EXISTS idx_bans_user_chat ON bans(user_id, chat_id);
CREATE INDEX IF NOT EXISTS idx_bans_active ON bans(is_active);
CREATE INDEX IF NOT EXISTS idx_admins_chat ON admins(chat_id);
CREATE INDEX IF NOT EXISTS idx_filters_chat ON filters(chat_id);
CREATE INDEX IF NOT EXISTS idx_notes_chat ON notes(chat_id);
```

### 3. التشغيل على PythonAnywhere

#### أ. رفع الملفات
1. اذهب إلى [pythonanywhere.com](https://www.pythonanywhere.com) وسجل الدخول
2. اذهب إلى **Files** في لوحة التحكم
3. أنشئ مجلد جديد باسم `telegram_bot`
4. ارفع جميع ملفات المشروع إلى هذا المجلد

#### ب. تثبيت المتطلبات
1. اذهب إلى **Consoles** واختر **Bash**
2. نفذ الأوامر التالية:

```bash
# الانتقال لمجلد المشروع
cd telegram_bot

# تثبيت المتطلبات
pip3.10 install --user -r requirements.txt
```

#### ج. إعداد متغيرات البيئة
1. في مجلد المشروع، أنشئ ملف `.env`:

```bash
nano .env
```

2. املأ الملف بالبيانات التالية:

```env
# إعدادات البوت - استبدل بالبيانات الحقيقية
BOT_TOKEN=1234567890:AABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQr
BOT_USERNAME=your_bot_username

# إعدادات Supabase - من لوحة تحكم Supabase
SUPABASE_URL=https://abcdefghijk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# معرف المطور - معرف تليجرام الخاص بك
SUDO_USERS=123456789

# إعدادات اختيارية
REDIS_URL=redis://localhost:6379/0
WEBHOOK_URL=
WEBHOOK_PATH=/webhook
WEBAPP_HOST=0.0.0.0
WEBAPP_PORT=8080
```

3. احفظ الملف بالضغط على `Ctrl+X` ثم `Y` ثم `Enter`

#### د. إعداد Always-On Task
1. اذهب إلى **Tasks** في لوحة التحكم
2. اضغط **Create a new scheduled task**
3. املأ البيانات:
   - **Command**: `cd /home/yourusername/telegram_bot && python3.10 main.py`
   - **Hour**: 00 (منتصف الليل)
   - **Minute**: 00
   - **Description**: Telegram Bot

> **ملاحظة**: الحسابات المجانية تسمح بـ task واحدة فقط تعمل لفترة محدودة. للتشغيل المستمر، ستحتاج حساب مدفوع.

#### هـ. إعداد Keep Alive (للحسابات المجانية)
أنشئ ملف `keep_alive.py`:

```python
import asyncio
import aiohttp
import time
from datetime import datetime

async def keep_alive():
    """إبقاء البوت نشط"""
    while True:
        try:
            print(f"[{datetime.now()}] البوت يعمل...")
            await asyncio.sleep(300)  # انتظار 5 دقائق
        except Exception as e:
            print(f"خطأ في keep_alive: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(keep_alive())
```

### 4. اختبار البوت

#### أ. تشغيل تجريبي
```bash
cd telegram_bot
python3.10 main.py
```

إذا ظهرت رسالة "تم بدء تشغيل البوت بنجاح!" فكل شيء يعمل بشكل صحيح.

#### ب. اختبار الأوامر
1. ابحث عن البوت في تليجرام
2. ابدأ محادثة معه بإرسال `/start`
3. أضف البوت إلى مجموعة تجريبية
4. اجعله مشرف مع جميع الصلاحيات
5. جرب أمر `/admin` في المجموعة

### 5. إعدادات إضافية

#### أ. الحصول على معرف تليجرام الخاص بك
1. ابحث عن [@userinfobot](https://t.me/userinfobot) في تليجرام
2. ابدأ محادثة معه
3. سيرسل لك معرفك الرقمي
4. أضف هذا الرقم إلى `SUDO_USERS` في ملف `.env`

#### ب. إعداد Webhook (اختياري للأداء الأفضل)
إذا كان لديك نطاق مخصص:

```python
# في ملف webhook.py
from aiohttp import web
from main import bot, dp

async def webhook_handler(request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()

app = web.Application()
app.router.add_post('/webhook', webhook_handler)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8080)
```

## 🔧 استكشاف الأخطاء الشائعة

### خطأ: "ModuleNotFoundError"
```bash
pip3.10 install --user module_name
```

### خطأ: "Invalid token"
- تأكد من صحة `BOT_TOKEN` في ملف `.env`
- تأكد من عدم وجود مسافات إضافية

### خطأ: "Connection to database failed"
- تأكد من صحة `SUPABASE_URL` و `SUPABASE_KEY`
- تأكد من إنشاء الجداول في Supabase

### البوت لا يرد في المجموعات
- تأكد من إضافة البوت كمشرف
- تأكد من تفعيل صلاحيات حذف الرسائل وتقييد الأعضاء

### الحساب المجاني محدود الوقت
- استخدم خدمات أخرى مثل Heroku أو Railway
- فكر في ترقية حسابك على PythonAnywhere

## 📱 إضافة البوت للمجموعات

### 1. إعداد صلاحيات البوت
عند إضافة البوت لمجموعة، تأكد من إعطائه الصلاحيات التالية:
- ✅ حذف الرسائل
- ✅ حظر الأعضاء
- ✅ دعوة الأعضاء
- ✅ تثبيت الرسائل
- ✅ تغيير معلومات المجموعة (اختياري)

### 2. الاختبار الأولي
```
/start - في رسالة خاصة مع البوت
/admin - في المجموعة لاختبار لوحة الإدارة
/help - لعرض جميع الأوامر المتاحة
```

### 3. إعداد نظام الحماية
```
/protection - لعرض إعدادات الحماية
/antiflood - لتفعيل مكافحة السبام
/welcome - لإعداد رسالة الترحيب
```

## 🎉 تهانينا!

البوت الآن جاهز للعمل! 🤖

### الخطوات التالية:
- [ ] اختبر جميع الأوامر
- [ ] خصص رسائل الترحيب
- [ ] اضبط إعدادات الحماية
- [ ] ادع الأصدقاء لاختبار البوت
- [ ] راقب السجلات للتأكد من عمل كل شيء

### للدعم:
إذا واجهت أي مشاكل، تأكد من:
1. قراءة رسائل الخطأ بعناية
2. التحقق من ملف `.env`
3. مراجعة السجلات في PythonAnywhere
4. اختبار الاتصال بقاعدة البيانات

---

**البوت تم تطويره بواسطة MiniMax Agent** 🤖

نتمنى لك تجربة ممتعة! 🎊
