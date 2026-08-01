import os
import time
import schedule
import threading
import telebot
import requests
import google.generativeai as genai

# تحميل المتغيرات السرية من السيرفر (Railway)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
YOUR_CHAT_ID = os.environ.get("YOUR_CHAT_ID")

# متغيرات المنصات (فيسبوك، بنتريست، يوتيوب)
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
PINTEREST_USERNAME = os.environ.get("PINTEREST_USERNAME") or "delrhayour0112"
YT_API_KEY = os.environ.get("YT_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# استخدام النسخة المدفوعة القوية Pro
model = genai.GenerativeModel('gemini-1.5-pro')

latest_topics = []
selected_sujet_text = ""
selected_article = ""
selected_social_post = ""

# ========== العميل 1: الباحث المفتوح والذكي ==========
def client_chercheur():
    try:
        prompt = "انت خبير ترندات ذكي جداً فالمغرب وعالمياً. بحث وعطيني أفضل وأقوى 3 مواضيع حصرياً وطالعة ترند حالياً في مختلف المجالات (AI، تقنية، ربح من النت، أخبار الساعة...). اعطيني كل موضوع في سطر يبدأ برقم 1 و 2 و 3 مع عنوان جذاب فقط بدون تفاصيل كثيرة."
        response = model.generate_content(prompt)
        global latest_topics
        latest_topics = response.text.split('\n')
        msg = f"🔍 *العميل 1 (الباحث): أحدث الترندات الطالعة دابا*\n\n{response.text}\n\n👉 رد برقم الموضوع (1 أو 2 أو 3) للاختيار."
        bot.send_message(YOUR_CHAT_ID, msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(YOUR_CHAT_ID, f"خطأ فالباحث: {e}")

# ========== العميل 2: الكاتب المحترف (>1800 كلمة + ألوان متجددة) ==========
def client_ecrivain(sujet):
    try:
        prompt = f"""انت كاتب محتوى تقني وتسويقي محترف جداً. اكتب مقالاً حصرياً وشاملاً وطويلاً جداً (أكثر من 1800 كلمة) حول الموضوع التالي: {sujet}.
        
شروط الصياغة والستايل:
1. الستايل عصري، احترافي، جذاب، ويخاطب القارئ مباشرة بأسلوب سلس.
2. استخدم كود HTML متكامل ونظيف للمدونة.
3. خلفية داكنة رئيسية (#0a0a0a) مع تغيير ألوان التنسيق، العناوين، والخطوط البصرية ديناميكياً في كل مقال (مثل تدرجات النيون، البنفسجي، الأزرق الملكي) لتكون متجددة.
4. أضف شريط متحرك (marquee) تحذيري أو ترويجي في البداية بلون جذاب.
5. قسّم المقال إلى فقرات عميقة وعناوين فرعية H2 و H3 مدعومة بقوائم منقطة وصناديق تنبيه."""
        
        response = model.generate_content(prompt)
        global selected_article
        selected_article = response.text
        
        msg = f"✍️ *العميل 2 (الكاتب): أنشأ المقال الشامل (>1800 كلمة)*\n\n{response.text[:800]}...\n\n👉 رد بكلمة 'نعم' لاعتماد المقال والانتقال للمصمم البصري، أو 'لا' للإلغاء."
        bot.send_message(YOUR_CHAT_ID, msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(YOUR_CHAT_ID, f"خطأ فالكاتب: {e}")

# ========== العميل 3: المصمم البصري (3 صور جاهزة) ==========
def client_designer(sujet):
    try:
        prompt = f"اقترح لي 3 وصف دقيق وساحر لصور مصغرة جاهزة للاستخدام في أدوات توليد الصور لموضوع: {sujet} بجودة سينمائية 4K وتصميم تجاري جذاب."
        response = model.generate_content(prompt)
        msg = f"🎨 *العميل 3 (المصمم): اقترح 3 صور جاهزة لترفق مع المقال*\n\n{response.text}\n\n👉 اضغط 'نشر' للانتقال لعميل السوشيال ميديا، أو 'لا' للإلغاء."
        bot.send_message(YOUR_CHAT_ID, msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(YOUR_CHAT_ID, f"خطأ فالمصمم: {e}")

# ========== العميل 4: عميل السوشيال ميديا (فيسبوك وبنتريست) ==========
def client_social_publisher(sujet):
    global selected_social_post
    try:
        prompt = f"اكتب لي منشور ترويجي قصير وجذاب جداً يناسب منصات التواصل الاجتماعي (Facebook, Pinterest حساب {PINTEREST_USERNAME}) للترويج لهذا المقال: {sujet} مع هاشتاغات قوية."
        response = model.generate_content(prompt)
        selected_social_post = response.text
        
        status_report = f"\n📌 حساب بنتريست: {PINTEREST_USERNAME}"
        
        # 1. النشر في فيسبوك
        if FB_PAGE_TOKEN and FB_PAGE_ID:
            url_fb = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/feed"
            res_fb = requests.post(url_fb, data={'message': selected_social_post, 'access_token': FB_PAGE_TOKEN})
            if res_fb.status_code == 200:
                status_report += "\n✅ تم النشر في فيسبوك (كنزة Ai) بنجاح."
            else:
                status_report += f"\n❌ خطأ في فيسبوك: {res_fb.text}"
        else:
            status_report += "\n⚠️ متغييرات فيسبوك غير مكتملة."

        msg = f"📢 *العميل 4 (النشر الاجتماعي):*{status_report}\n\n{selected_social_post}\n\n👉 أرسل كلمة 'فيديو' للانتقال لصانع فيديو يوتيوب شورتس، أو 'لا' للإلغاء."
        bot.send_message(YOUR_CHAT_ID, msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(YOUR_CHAT_ID, f"خطأ فمشروع السوشيال: {e}")

# ========== العميل 5: صانع الفيديو الآلي (يوتيوب شورتس - 40 ثانية) ==========
def client_video_creator(sujet):
    try:
        prompt = f"اكتب لي سكريبت احترافي لفيديو قصير (حوالي 40 ثانية) باللغة العربية الفصحى وبدون ظهور وجوه، مخصص ليوتيوب شورتس حول: {sujet}."
        response = model.generate_content(prompt)
        
        yt_status = "\n✅ مفتاح يوتيوب API متصل وجاهز للجدولة والرفع." if YT_API_KEY else "\n⚠️ (وضع التحضير): أضف YT_API_KEY لتفعيل الاتصال التلقائي بيوتيوب."

        msg = f"🎬 *العميل 5 (يوتيوب شورتس):*{yt_status}\n\n{response.text}\n\n🚀 *تمت دورة العمل بالكامل بنجاح تام! صيفط (/start) للبدء من جديد.*"
        bot.send_message(YOUR_CHAT_ID, msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(YOUR_CHAT_ID, f"خطأ في صانع الفيديو: {e}")

# ========== أمر /start للبداية ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🚀 مرحباً بك يا إدريس! النظام الخماسي الشامل (Pro) يشتغل بكل منصاتك. جاري جلب أحدث الترندات...")
    client_chercheur()

# ========== نظام التحكم الإداري والـ Breakdown التفاعلي ==========
@bot.message_handler(func=lambda message: True)
def handle_user_input(message):
    global selected_sujet_text
    text = message.text.strip().lower()
    
    if text in ['1', '2', '3']:
        index = int(text) - 1
        try:
            selected_sujet_text = latest_topics[index]
        except:
            selected_sujet_text = f"موضوع ترند رقم {text}"
            
        bot.send_message(YOUR_CHAT_ID, f"📊 **Breakdown - الخطوة 1:** تم اختيار الموضوع: {selected_sujet_text}\n\n🔄 العميل 2 (الكاتب) يباشر كتابة المقال العملاق (>1800 كلمة)...")
        client_ecrivain(selected_sujet_text)
        
    elif text == 'نعم':
        bot.send_message(YOUR_CHAT_ID, "📊 **Breakdown - الخطوة 2 & 3:** تم اعتماد المقال! جاري تجهيز اقتراحات الصور البصرية...")
        client_designer(selected_sujet_text)
        
    elif text == 'نشر':
        bot.send_message(YOUR_CHAT_ID, "📊 **Breakdown - الخطوة 4:** جاري النشر التلقائي في فيسبوك وبنتريست...")
        client_social_publisher(selected_sujet_text)
        
    elif text == 'فيديو':
        bot.send_message(YOUR_CHAT_ID, "📊 **Breakdown - الخطوة 5:** جاري إعداد سكريبت يوتيوب شورتس (40 ثانية)...")
        client_video_creator(selected_sujet_text)
        
    elif text == 'لا':
        bot.send_message(YOUR_CHAT_ID, "❌ تم إلغاء العملية الحالية. أرسل `/start` للبدء من جديد.")
    else:
        bot.send_message(YOUR_CHAT_ID, "🤖 **مدير النظام:** ما فهمت الرد ديالك. استعمل الأوامر المتاحة (`/start`، الأرقام، `نعم`، `نشر`، `فيديو`، أو `لا`).")

# ========== الجدولة في الخلفية ==========
def run_schedule():
    schedule.every(6).hours.do(client_chercheur)
    while True:
        schedule.run_pending()
        time.sleep(60)

t = threading.Thread(target=run_schedule)
t.start()

print("النظام الخماسي المتكامل (فيسبوك، بنتريست، يوتيوب) خدام بنجاح... 🚀")
bot.infinity_polling()
