import telebot
import mysql.connector
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

# إعداد اتصال MySQL
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="username",
        password="password",
        database="database_name"
    )

# إنشاء قاعدة البيانات والجداول المطلوبة
def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # إنشاء جدول المستخدمين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            account_name VARCHAR(255),
            account_number VARCHAR(255),
            balance DECIMAL(10, 2) DEFAULT 0.0
        )
    ''')

    # إنشاء جدول الحسابات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_id BIGINT PRIMARY KEY AUTO_INCREMENT,
            user_id BIGINT,
            email VARCHAR(255),
            password VARCHAR(255),
            status VARCHAR(20) DEFAULT 'Pending',
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    # إنشاء جدول المعاملات المالية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id BIGINT PRIMARY KEY AUTO_INCREMENT,
            user_id BIGINT,
            amount DECIMAL(10, 2),
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    conn.close()

# إضافة مستخدم جديد إلى قاعدة البيانات
def add_user(user_id, account_name, account_number):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT IGNORE INTO users (user_id, account_name, account_number, balance)
        VALUES (%s, %s, %s, 0.0)
    ''', (user_id, account_name, account_number))
    conn.commit()
    conn.close()

# تحديث رصيد المستخدم وتسجيل المعاملة المالية
def update_balance(user_id, amount, description):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + %s WHERE user_id = %s', (amount, user_id))
    cursor.execute('INSERT INTO transactions (user_id, amount, description) VALUES (%s, %s, %s)', (user_id, amount, description))
    conn.commit()
    conn.close()

# الحصول على رصيد المستخدم
def get_balance(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = %s', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0.0

# تسجيل حساب Gmail جديد
def add_account(user_id, email, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO accounts (user_id, email, password) VALUES (%s, %s, %s)', (user_id, email, password))
    conn.commit()
    conn.close()

# الحصول على الحسابات الخاصة بالمستخدم
def get_user_accounts(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT email, status FROM accounts WHERE user_id = %s', (user_id,))
    accounts = cursor.fetchall()
    conn.close()
    return accounts


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
