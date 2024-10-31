import telebot
import mysql.connector
import random

# إعدادات الاتصال بقاعدة البيانات
db = mysql.connector.connect(
    host="localhost",  # عنوان قاعدة البيانات
    user="your_username",  # اسم مستخدم MySQL
    password="your_password",  # كلمة مرور MySQL
    database="your_database"  # اسم قاعدة البيانات
)

# إعداد التوكن الخاص بالبوت
API_TOKEN = '7859733734:AAEfUSacYoHRMDgmL_QBjCKOdv_xOQRqMhY'
bot = telebot.TeleBot(bot_token)

# دالة لجلب بريد Gmail عشوائي من قاعدة البيانات
def fetch_random_email():
    cursor = db.cursor()
    cursor.execute("SELECT email FROM emails_table ORDER BY RAND() LIMIT 1")  # استبدل emails_table باسم الجدول
    email = cursor.fetchone()
    cursor.close()
    return email[0] if email else None

# إعداد الرسالة وزر تسجيل حساب جديد
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn_new_account = telebot.types.InlineKeyboardButton("تسجيل حساب Gmail جديد", callback_data="new_account")
    markup.add(btn_new_account)
    bot.send_message(message.chat.id, "مرحباً! اضغط على الزر أدناه لتسجيل حساب Gmail جديد.", reply_markup=markup)

# التعامل مع ضغط الزر
@bot.callback_query_handler(func=lambda call: call.data == "new_account")
def handle_new_account(call):
    email = fetch_random_email()
    if email:
        bot.send_message(call.message.chat.id, f"البريد الإلكتروني الجديد هو: {email}")
    else:
        bot.send_message(call.message.chat.id, "عذرًا، لا يوجد بريد إلكتروني متاح حالياً.")

# تشغيل البوت
bot.polling()
