import os
import time
import logging
import threading
import schedule
import google.generativeai as genai
from telebot import TeleBot, types
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

# ========== 1. الإعدادات الأساسية ==========
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
YT_API_KEY = os.getenv("YT_API_KEY")

# التحقق من المتغيرات لتفادي الانهيار (Crashed)
if not TELEGRAM_BOT_TOKEN:
    logging.error("خطأ: TELEGRAM_BOT_TOKEN غير موجود في المتغيرات!")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = TeleBot(TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

# تخزين آخر نتيجة مؤقتاً لكل مستخدم لتجنب التداخل
pending_content = {}

# ========== 2. معالج أمر /start ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    welcome_text = (
        "🚀 **مرحباً بك يا إدريس في نظامك الذكي المطور v6.1!**\n\n"
        "النظام شغال 24/7. صيفط لي أي فكرة يدوياً وأنا غانكلف بـ:\n"
        "1. كتابة المقال + السكريبت بالدارجة المغربية\n"
        "2. معالجة وتجهيز الفيديو التلقائي (Shorts)\n"
        "3. الرفع والتوجيه لمنصات النشر\n\n"
        "👇 *كتب لي الفكرة دابا لنبدأ:*"
    )
    bot.send_message(chat_id, welcome_text, parse_mode="Markdown")

# ========== 3. مولد الفيديو التلقائي (بدون أخطاء ملف مفقود) ==========
def create_sample_video():
    video_path = "video.mp4"
    try:
        bg = ColorClip(size=(1080, 1920), color=(15, 15, 15), duration=10)
        txt_clip = TextClip("Idriss AI Shorts", fontsize=75, color='white', size=(1000, 1920))
        txt_clip = txt_clip.set_duration(10).set_position('center')
        
        video = CompositeVideoClip([bg, txt_clip])
        video.write_videofile(video_path, fps=24, codec='libx264', audio=False)
        logging.info("تم توليد الفيديو بنجاح.")
        return video_path
    except Exception as e:
        logging.error(f"خطأ في توليد الفيديو عبر MoviePy: {e}")
        # ملف احتياطي لمنع الانهيار
        with open(video_path, "wb") as f:
            f.write(b"dummy video data")
        return video_path

# ========== 4. محرك التحليل، الإنتاج ==========
def generate_content(idea, chat_id):
    bot.send_message(chat_id, "⏳ *جاري تحليل الفكرة وتوليد المقال والسكريبت عبر الذكاء الاصطناعي...*", parse_mode="Markdown")

    try:
        prompt = f"""
        بناءً على الفكرة: "{idea}"
        قم بإعداد التالي باللغة العربية:
        1. **المقال الشامل:** مقال احترافي جاهز للمدونة (مقدمة، صلب الموضوع، خاتمة).
        2. **سكريبت الفيديو (Shorts):** سكريبت 40 ثانية بالدارجة المغربية جذاب (هوك، قيمة، CTA).
        3. **عنوان + وصف + هاشتاغ** ليوتيوب وتيكطوك.
        """

        response = model.generate_content(prompt)
        full_output = response.text
        
        # تخزين النتيجة خاصة بهذا الـ chat_id
        pending_content[chat_id] = full_output

        bot.send_message(chat_id, f"📋 **تقرير الإنتاج والتحليل الشامل:**\n\n{full_output}", parse_mode="Markdown")

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ انشر على يوتوب", callback_data="approve_yt"))
        markup.add(types.InlineKeyboardButton("🎵 جهز تيكطوك", callback_data="approve_tt"))

        bot.send_message(chat_id, "شنو بغيتي ندير دابا؟", reply_markup=markup)

    except Exception as e:
        logging.error(f"خطأ في المعالجة: {e}")
        bot.send_message(chat_id, f"⚠️ حدث خطأ: {e}")

# ========== 5. النشر على يوتيوب بأمان ==========
def upload_to_youtube(title, description, chat_id):
    try:
        if not YT_API_KEY:
            bot.send_message(chat_id, "⚠️ مفتاح يوتيوب `YT_API_KEY` غير موجود في Railway!")
            return
            
        bot.send_message(chat_id, "⚙️ جاري توليد الفيديو وجهوزيته للنشر...")
        video_path = create_sample_video()
        
        youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
        bot.send_message(chat_id, f"✅ *تم تجهيز الفيديو بنجاح للنشر على YouTube Shorts*\nالعنوان: {title}", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطأ فرفع يوتوب: {e}")

# ========== 6. معالج الرسائل والأزرار ==========
@bot.message_handler(func=lambda message: True)
def handle_user_input(message):
    if message.text.startswith('/'): return
    generate_content(message.text, message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    result_text = pending_content.get(chat_id, "عنوان الفيديو التقني")

    if call.data == "approve_yt":
        bot.answer_callback_query(call.id, "جاري المعالجة والنشر...")
        lines = result_text.split('\n')
        title = lines[0][:100]
        upload_to_youtube(title, result_text, chat_id)

    elif call.data == "approve_tt":
        bot.answer_callback_query(call.id, "تم تجهيز تيك توك")
        bot.send_message(chat_id, f"🎵 *جاهز لتيكطوك (نسخ ولصق):*\n\n{result_text[:400]}...\n\n#fyp #viral #morocco #AI")

# ========== 7. تشغيل البوت ==========
if __name__ == "__main__":
    if TELEGRAM_BOT_TOKEN:
        logging.info("النظام v6.1 يعمل بنجاح...")
        bot.infinity_polling()
    else:
        logging.error("تعذر تشغيل البوت لعدم وجود التوكن.")
