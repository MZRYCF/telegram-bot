import os
import staypresent

# إنشاء مسار /health لفحص الحالة
staypresent.web.json({"status": "running"})

# تشغيل البوت مع إعادة التشغيل التلقائي في حال حدوث خطأ
staypresent.run(
    "bot.py",
    port=int(os.getenv("PORT", 8080)),
    restart_on_crash=True,
    max_restarts=5
)