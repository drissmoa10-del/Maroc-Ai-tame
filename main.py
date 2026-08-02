import os
import time
import logging
import google.generativeai as genai
from telebot import TeleBot, types

# ========== 1. الإعدادات الأساسية ==========
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    logging.error("خطأ حرج: TELEGRAM_BOT_TOKEN غير موجود في Railway Variables!")
if not GEMINI_API_KEY:
    logging.error("خطأ حرج: GEMINI_API_KEY غير موجود في Railway Variables!")

genai.configure(api_key=GEMINI_API_KEY)

# تعديل اسم الموديل إلى gemini-1.5-pro المضمون والمستقر
model = genai.GenerativeModel('gemini-1.5-pro')

bot = TeleBot(TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None
pending_content = {}

# ========== 2. معالج أمر /start ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    welcome_text = (
        "🚀 **مرحباً بك يا إدريس في نظامك الذكي المطور!**\n\n"
        "النظام شغال ومستقر 100%. صيفط لي أي فكرة أو مجال بغيتي، وأنا غانكلف بـ:\n"
        "1. كتابة المقال الشامل للمدونة 📝\n"
        "2. كتابة سكريبت فيديو Shorts بالدارجة المغربية 🎬\n"
        "3. تجهيز الهاشتاغات والعناوين ليوتيوب وتيك توك 🏷️\n\n"
        "👇 *كتب لي الفكرة دابا لنبدأ التنفيذ:*"
    )
    bot.send_message(chat_id, welcome_text, parse_mode="Markdown")

# ========== 3. معالج النصوص والأفكار ==========
@bot.message_handler(func=lambda message: True)
def handle_user_input(message):
    if message.text.startswith('/'): 
        return
    
    chat_id = message.chat.id
    idea = message.text
    bot.send_message(chat_id, "⏳ *جاري تحليل الفكرة، كتابة المقال والسكريبت عبر الذكاء الاصطناعي...*", parse_mode="Markdown")

    try:
        prompt = f"""
        بناءً على الفكرة أو الطلب التالي: "{idea}"
        قم بإعداد التالي باللغة العربية بأسلوب احترافي:
        1. **المقال الشامل:** مقال متكامل جاهز للنشر على المدونة (مقدمة، صلب الموضوع، خاتمة).
        2. **سكريبت الفيديو (Shorts):** سكريبت 40 ثانية بالدارجة المغربية جذاب (هوك، قيمة، CTA).
        3. **العناوين والهاشتاغات:** عناوين جذابة + وصف + هاشتاغات ترند ليوتيوب وتيك توك.
        """

        response = model.generate_content(prompt)
        full_output = response.text
        pending_content[chat_id] = full_output

        bot.send_message(chat_id, f"📋 **النتائج والتحليل الشامل:**\n\n{full_output}", parse_mode="Markdown")

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📺 تجهيز ليوتيوب", callback_data="prep_yt"),
                   types.InlineKeyboardButton("🎵 تجهيز لتيك توك", callback_data="prep_tt"))

        bot.send_message(chat_id, "اختر المنصة لتجهيز النشر:", reply_markup=markup)

    except Exception as e:
        logging.error(f"خطأ في توليد المحتوى: {e}")
        bot.send_message(chat_id, f"⚠️ حدث خطأ أثناء المعالجة: {e}")

# ========== 4. معالج الأزرار ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    result_text = pending_content.get(chat_id, "محتوى جاهز")
    
    if call.data == "prep_yt":
        bot.answer_callback_query(call.id, "تم تجهيز يوتيوب")
        lines = result_text.split('\n')
        title = lines[0] if lines else "فيديو تقني جديد"
        bot.send_message(chat_id, f"📺 **جاهز لـ YouTube Shorts:**\n\n**العنوان:**\n{title}\n\n**الوصف والهاشتاغات:**\n{result_text[:600]}", parse_mode="Markdown")

    elif call.data == "prep_tt":
        bot.answer_callback_query(call.id, "تم تجهيز تيك توك")
        bot.send_message(chat_id, f"🎵 **جاهز لـ TikTok (نسخ ولصق):**\n\n{result_text[:400]}...\n\n#fyp #viral #morocco #AI #ربح_من_الترنت", parse_mode="Markdown")

# ========== 5. تشغيل البوت ==========
if __name__ == "__main__":
    if bot:
        logging.info("البوت يعمل بنجاح...")
        bot.infinity_polling()
