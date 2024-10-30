import telebot
import sqlite3
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ضع رمز API الخاص بالبوت هنا
API_TOKEN = '7859733734:AAEfUSacYoHRMDgmL_QBjCKOdv_xOQRqMhY'
bot = telebot.TeleBot(API_TOKEN)

# قائمة الإيميلات وكلمات المرور
email_list = [
    {"email": "email1@gmail.com", "password": "password1"},
    {"email": "email2@gmail.com", "password": "password2"},
    {"email": "email3@gmail.com", "password": "password3"}
]
reserved_emails = {}  # تخزين الإيميلات المحجوزة لكل مستخدم

# إنشاء قاعدة بيانات وجدول للمستخدمين والمحافظ المالية إذا لم تكن موجودة
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            account_name TEXT,
            account_number TEXT,
            balance REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()

# إضافة مستخدم جديد إلى قاعدة البيانات
def add_user(user_id, account_name, account_number):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, account_name, account_number, balance)
        VALUES (?, ?, ?, 0.0)
    ''', (user_id, account_name, account_number))
    conn.commit()
    conn.close()

# تحديث رصيد المستخدم
def update_balance(user_id, amount):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

# الحصول على رصيد المستخدم
def get_balance(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0.0

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
    user_id = message.from_user.id
    user_name = message.from_user.username or "UnknownUser"  # إذا لم يكن لديه اسم مستخدم
    account_number = f"ACC-{user_id}"  # صيغة رقم الحساب

    # إضافة المستخدم إلى قاعدة البيانات إذا لم يكن موجودًا
    add_user(user_id, user_name, account_number)

    bot.send_message(message.chat.id, "أهلاً بالجميع في البوت! اختر أحد الخيارات أدناه:", reply_markup=main_menu())

# معالجة زر "Register a new Gmail"
@bot.message_handler(func=lambda message: message.text == "Register a new Gmail")
def register_gmail(message):
    user_id = message.from_user.id
    if user_id in reserved_emails:
        bot.send_message(message.chat.id, "لديك إيميل محجوز بالفعل. استخدمه أولاً.")
        return

    # الحصول على أول إيميل غير محجوز من القائمة
    if email_list:
        email_data = email_list.pop(0)  # إزالة الإيميل من القائمة
        reserved_emails[user_id] = email_data  # حجز الإيميل للمستخدم

        # إعداد أزرار الموافقة أو الرفض
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Oui", callback_data="confirm_yes"))
        markup.add(InlineKeyboardButton("No", callback_data="confirm_no"))

        # إرسال معلومات الإيميل
        registration_info = (
            "🔹 Register a Gmail account using the specified data and get 0.05$ \n\n"
            f"📧 Email: {email_data['email']}\n"
            f"🔐 Password: {email_data['password']}\n\n"
            "⚠️ Be sure to use the specified password, otherwise the account will not be paid."
        )
        bot.send_message(message.chat.id, registration_info, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "عذرًا، جميع الإيميلات محجوزة حاليًا.")

# التعامل مع رد المستخدم على طلب الحجز
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def callback_confirm(call):
    user_id = call.from_user.id
    if user_id not in reserved_emails:
        bot.send_message(call.message.chat.id, "لم يتم العثور على إيميل محجوز.")
        return

    if call.data == "confirm_yes":
        # إضافة 0.05$ إلى رصيد المستخدم
        update_balance(user_id, 0.05)
        bot.send_message(call.message.chat.id, "تم حجز الإيميل بنجاح! وقد تم إضافة 0.05$ إلى رصيدك.")
        # إزالة الإيميل المحجوز
        reserved_emails.pop(user_id)
    elif call.data == "confirm_no":
        # إرجاع الإيميل للقائمة وإلغاء الحجز
        email_data = reserved_emails.pop(user_id)
        email_list.append(email_data)
        bot.send_message(call.message.chat.id, "تم إلغاء الحجز. يمكنك طلب إيميل جديد لاحقًا.")

# معالجة زر "Balance" لعرض الرصيد
@bot.message_handler(func=lambda message: message.text == "Balance")
def show_balance(message):
    user_id = message.from_user.id
    balance = get_balance(user_id)
    bot.send_message(message.chat.id, f"رصيدك الحالي هو: {balance:.2f} $")

# تهيئة قاعدة البيانات عند بدء التشغيل
init_db()

# تشغيل البوت
bot.polling()
