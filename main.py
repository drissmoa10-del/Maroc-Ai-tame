import os
import time
import schedule
import threading
import telebot
import google.generativeai as genai

# تحميل المتغيرات السرية من السيرفر (Railway)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
YOUR_CHAT_ID = os.environ.get("YOUR_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

latest_topics = []
selected_sujet_text = ""
selected_article = ""

# ========== العميل 1: الباحث ==========
def client_chercheur():
    try:
        prompt = "انت خبير ترندات. عطيني 3 مواضيع ترند دابا ف المغرب على: الهجرة, AI, الربح من الانترنت. اعطيني كل موضوع في سطر يبدأ برقم 1 و 2 و 3 بدون تفاصيل زايدة فالعنوان."
        response = model.generate_content(prompt)
        global latest_topics
        latest_topics = response.text.split('\n')
        msg = f"🔍 *العميل الباحث جاب الجديد*\n\n{response.text}\n\n👉 رد برقم الموضوع (1 أو 2 أو 3)"
        bot.send_message(YOUR_CHAT_ID, msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(YOUR_CHAT_ID, f"خطأ فالباحث: {e}")

# ========== العميل 2: الكاتب ==========
def client_ecrivain(sujet):
    try:
        prompt = f"كتب مقال حصري احترافي طويل (حوالي 1000 كلمة) على الموضوع التالي: {sujet}. استعمل HTML وخلفية داكنة #0a0a0a مع marquee تحذير بالبنفسجي فالبداية وستايل عصري يناسب مدونة تقنية."
        response = model.generate_content(prompt)
        global selected_article
        selected_article = response.text
        msg = f"✍️ *العميل الكاتب وجد المقال*\n\n{response.text[:800]}...\n\n👉 رد بكلمة 'نعم' للانتقال للمصمم، أو 'لا' للالغاء"
        bot.send_message(YOUR_CHAT_ID, msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(YOUR_CHAT_ID, f"خطأ فالكاتب: {e}")

# ========== العميل 3: المصمم ==========
def client_designer(sujet):
    try:
        prompt = f"عطيني 3 برومتات احترافية لتوليد صورة مصغرة لجلب الترافيك لموضوع: {sujet}. الستايل: dark, cinematic, 4k, futuristic neon."
        response = model.generate_content(prompt)
        msg = f"🎨 *العميل المصمم*\n\n{response.text}\n\n🚀 المقال جاهز!"
        bot.send_message(YOUR_CHAT_ID, msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(YOUR_CHAT_ID, f"خطأ فالمصمم: {e}")

# ========== أمر /start باش يبدأ البوت يخدم فوراً ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🚀 مرحباً بك يا إدريس! الفريق الذكي مستعد. جاري إرسال أحدث الترندات...")
    client_chercheur()

# ========== استقبال ردود المستخدم ==========
@bot.message_handler(func=lambda message: True)
def handle_user_input(message):
    global selected_sujet_text
    text = message.text.strip()
    
    if text in ['1', '2', '3']:
        index = int(text) - 1
        try:
            selected_sujet_text = latest_topics[index]
        except:
            selected_sujet_text = f"موضوع ترند رقم {text}"
            
        bot.send_message(YOUR_CHAT_ID, f"✅ اخترتي الموضوع: {selected_sujet_text}\n\nالكاتب دابا كيوجد المقال...")
        client_ecrivain(selected_sujet_text)
        
    elif text.lower() == 'نعم':
        bot.send_message(YOUR_CHAT_ID, "🎉 تم اعتماد المقال! المصمم كيوجد البرومتات...")
        client_designer(selected_sujet_text)
        
    elif text.lower() == 'لا':
        bot.send_message(YOUR_CHAT_ID, "❌ تم إلغاء العملية.")
    else:
        bot.send_message(YOUR_CHAT_ID, "🤖 المدير: ما فهمتش الرد ديالك. صيفط /start للبداية.")

# ========== الجدولة في الخلفية ==========
def run_schedule():
    schedule.every(6).hours.do(client_chercheur)
    while True:
        schedule.run_pending()
        time.sleep(60)

t = threading.Thread(target=run_schedule)
t.start()

print("المدير والفريق خدامين... 🚀")
bot.infinity_polling()
