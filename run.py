#!/usr/bin/env python3
"""
ملف تشغيل البوت المبسط
"""
import sys
import os

# إضافة المجلد الحالي إلى مسار Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        # استيراد وتشغيل البوت
        from main import main
        import asyncio
        
        print("🚀 بدء تشغيل بوت إدارة المجموعات...")
        print("📖 للتوقف اضغط Ctrl+C")
        print("-" * 50)
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف البوت بواسطة المستخدم")
    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        print("💡 تأكد من تثبيت المتطلبات: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        sys.exit(1)
