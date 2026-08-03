import os
import logging
import requests
from telebot import TeleBot, types

# ========== 1. الإعدادات الأساسية ==========
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    logging.error("خطأ حرج: TELEGRAM_BOT_TOKEN غير موجود في Railway Variables!")
if not GROQ_API_KEY:
    logging.error("خطأ حرج: GROQ_API_KEY غير موجود في Railway Variables!")

bot = TeleBot(TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None
pending_content = {}

# دالة الاتصال بـ Groq (Llama 3 عبر Groq Cloud API)
def generate_groq_content(prompt_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "أنت مساعد ذكي ومحترف، تجيب باللغة العربية الفصحى والدارجة المغربية حسب السياق."},
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        res_json = response.json()
        if response.status_code == 200:
            return res_json['choices'][0]['message']['content']
        else:
            error_msg = res_json.get('error', {}).get('message', 'خطأ غير معروف من Groq')
            return f"⚠️ خطأ من Groq API: {error_msg}"
    except Exception as e:
        return f"⚠️ خطأ في الاتصال: {str(e)}"

# ========== 2. معالج الأوامر ==========
@bot.message_handler(commands=['start', 'menu', 'shop', 'balance', 'profile', 'support'])
def send_welcome(message):
    chat_id = message.chat.id
    welcome_text = (
        "🚀 **مرحباً بك يا إدريس في نظامك الذكي المطور (Groq Llama 3)!**\n\n"
        "النظام شغال وسريع جداً. صيفط لي أي فكرة أو مجال بغيتي، وأنا غانكلف بـ:\n"
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
    bot.send_message(chat_id, "⏳ *جاري تحليل الفكرة، كتابة المقال والسكريبت بسرعة فائقة...*", parse_mode="Markdown")

    try:
        prompt = f"""
        بناءً على الفكرة أو الطلب التالي: "{idea}"
        قم بإعداد التالي باللغة العربية بأسلوب احترافي:
        1. **المقال الشامل:** مقال متكامل جاهز للنشر على المدونة (مقدمة، صلب الموضوع، خاتمة).
        2. **سكريبت الفيديو (Shorts):** سكريبت 40 ثانية بالدارجة المغربية جذاب (هوك، قيمة، CTA).
        3. **العناوين والهاشتاغات:** عناوين جذابة + وصف + هاشتاغات ترند ليوتيوب وتيك توك.
        """

        full_output = generate_groq_content(prompt)
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
