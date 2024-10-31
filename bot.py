import telebot
import mysql.connector
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# إعداد التوكن الخاص بالبوت
API_TOKEN = '7859733734:AAEfUSacYoHRMDgmL_QBjCKOdv_xOQRqMhY'
bot = telebot.TeleBot(API_TOKEN)

# إعدادات الاتصال بقاعدة البيانات
db_config = {
    'host': 'localhost',         # عنوان السيرفر
    'user': 'your_username',     # اسم المستخدم
    'password': 'your_password', # كلمة المرور
    'database': 'your_database'  # اسم قاعدة البيانات
}

# دالة لجلب بريد Gmail عشوائي غير محجوز من قاعدة البيانات
def fetch_random_email():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT email, password FROM gmail_accounts WHERE reserved = 0 ORDER BY RAND() LIMIT 1")
    result = cursor.fetchone()
    if result:
        email, password = result
        # تحديث حالة البريد كـ"محجوز"
        cursor.execute("UPDATE gmail_accounts SET reserved = 1 WHERE email = %s", (email,))
        conn.commit()
    else:
        email, password = None, None
    cursor.close()
    conn.close()
    return {"email": email, "password": password} if email else None

# دالة لإظهار زر "تسجيل حساب Gmail جديد"
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    btn_new_account = InlineKeyboardButton("تسجيل حساب Gmail جديد", callback_data="new_account")
    markup.add(btn_new_account)
    bot.send_message(message.chat.id, "مرحباً! اضغط على الزر أدناه لتسجيل حساب Gmail جديد.", reply_markup=markup)

# التعامل مع ضغط زر "تسجيل حساب Gmail جديد"
@bot.callback_query_handler(func=lambda call: call.data == "new_account")
def handle_new_account(call):
    email_data = fetch_random_email()
    if email_data:
        bot.send_message(call.message.chat.id, f"📧 Email: {email_data['email']}\n🔐 Password: {email_data['password']}")
    else:
        bot.send_message(call.message.chat.id, "عذرًا، لا يوجد بريد إلكتروني متاح حالياً.")

# تشغيل البوت
bot.polling()
