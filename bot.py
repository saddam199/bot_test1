import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ضع رمز API الخاص بالبوت هنا
API_TOKEN = '7859733734:AAEfUSacYoHRMDgmL_QBjCKOdv_xOQRqMhY'
bot = telebot.TeleBot(API_TOKEN)

# إعداد الأزرار الرئيسية
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("Register a new Gmail"), KeyboardButton("My accounts"))
    markup.row(KeyboardButton("Balance"), KeyboardButton("My referrals"))
    markup.row(KeyboardButton("Settings"), KeyboardButton("Help"))
    return markup

# معالجة رسالة البدء
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "أهلاً بالجميع في البوت! اختر أحد الخيارات أدناه:", reply_markup=main_menu())

# معالجة زر "Register a new Gmail"
@bot.message_handler(func=lambda message: message.text == "Register a new Gmail")
def register_gmail(message):
    # الرسالة التي تظهر عند اختيار "Register a new Gmail"
    registration_info = (
        "🔹 Register a Gmail account using the specified data and get 0.05$ \n\n"
        "📧 Email: test@gmail.com\n"
        "🔐 Password: test\n\n"
        "⚠️ Be sure to use the specified password, otherwise the account will not be paid."
    )
    bot.send_message(message.chat.id, registration_info)

# تشغيل البوت
bot.polling()

