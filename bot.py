import os
import telebot
import yt_dlp
from dotenv import load_dotenv

# تحميل التوكن من ملف .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# إنشاء مجلد لحفظ الفيديوهات مؤقتاً
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! 🎬\nأرسل لي رابط فيديو من (يوتيوب، تيك توك، إنستغرام، فيسبوك) وسأقوم بتحميله لك 📥")

# دعم المنصات المتعددة
@bot.message_handler(func=lambda message: any(domain in message.text.lower() for domain in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "facebook.com", "fb.watch"]))
def download_video(message):
    url = message.text
    msg = bot.reply_to(message, "⏳ جاري تحميل الفيديو، يرجى الانتظار...")

    # مسار ffmpeg (تأكد من صحته)
   # FFMPEG_PATH = r"C:\Users\mazar\Downloads\ffmpeg-9.0.2-essentials_build\ffmpeg-9.0.2-essentials_build\bin\ffmpeg.exe"
    
    # مسار ملف الكوكيز (إذا قمت بتصديره لإنستغرام، أزل علامة المربع # من السطر التالي)
    # COOKIES_PATH = "cookies.txt" 

    ydl_opts = {
        # جلب أفضل فيديو وأفضل صوت ودمجهما
        'format': 'bestvideo+bestaudio/best',
        # تفضيل جودة 720p لتقليل الحجم وتجنب تجاوز 50 ميجابايت
        'format_sort': ['res:720', 'ext:mp4:m4a'],
       # 'ffmpeg_location': FFMPEG_PATH,
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'nocheckcertificate': True,
        'socket_timeout': 60,
        # محاكاة متصفح لتجاوز حظر المنصات
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
        # 'cookiefile': COOKIES_PATH, # تفعيل هذا السطر إذا كنت تستخدم الكوكيز لإنستغرام
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            
            # التأكد من المسار في حال تغير الامتداد بعد الدمج
            if not os.path.exists(file_path):
                base, _ = os.path.splitext(file_path)
                file_path = base + '.mp4'

        # التحقق من حجم الملف قبل الإرسال (50 ميجابايت)
        if os.path.getsize(file_path) > 50 * 1024 * 1024:
            os.remove(file_path)
            bot.edit_message_text("❌ الملف كبير جدًا (أكثر من 50 ميجابايت) ولا يمكن إرساله عبر تيليجرام.", chat_id=message.chat.id, message_id=msg.message_id)
            return

        bot.edit_message_text("📤 جاري إرسال الفيديو إلى تيليجرام...", chat_id=message.chat.id, message_id=msg.message_id)
        
        # إرسال الفيديو مع مهلة زمنية طويلة
        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="تم التحميل بنجاح ✅", timeout=300)
        
        # حذف الملف من جهازك لتوفير المساحة
        os.remove(file_path)

    except Exception as e:
        # خطة بديلة: إذا فشل تحميل الفيديو، قم بتحميل الصوت فقط
        bot.edit_message_text("⚠️ الفيديو كبير جداً أو حدث خطأ، جاري محاولة تحميل الصوت فقط...", chat_id=message.chat.id, message_id=msg.message_id)
        
        ydl_opts_audio = {
            'format': 'bestaudio/best',
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'quiet': True,
            # 'ffmpeg_location': FFMPEG_PATH,
            # تحويل الصوت إلى mp3
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info_dict)
                # تغيير الامتداد إلى mp3
                base, _ = os.path.splitext(file_path)
                file_path = base + '.mp3'

            with open(file_path, 'rb') as audio:
                bot.send_audio(message.chat.id, audio, caption="تم تحميل الصوت بنجاح 🎵", timeout=300)
            os.remove(file_path)
            
        except Exception as e2:
            bot.edit_message_text(f"❌ فشل التحميل نهائياً:\n{str(e2)}", chat_id=message.chat.id, message_id=msg.message_id)

# الرد على أي رسالة أخرى لا تحتوي على رابط
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "أرسل لي رابط فيديو صالح من (يوتيوب، تيك توك، إنستغرام، فيسبوك) لتحميله.")

print("بوت التحميل الشامل يعمل الآن...")
bot.infinity_polling()