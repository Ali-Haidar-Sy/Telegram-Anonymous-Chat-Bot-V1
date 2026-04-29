# -*- coding: utf-8 -*-
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import sqlite3
import threading
import time
import random
from datetime import datetime
import os

# ==================== الإعدادات الأساسية ====================
TOKEN = "UR-TOKEN"  # ضع التوكن الخاص بك
ADMIN_ID = 6731423732
BOT_VERSION = "2.0.0"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ==================== قاعدة البيانات ====================
DB_NAME = "chat_bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # جدول المستخدمين مع إضافة حقول الجنس والتفضيل
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  first_name TEXT,
                  language TEXT DEFAULT 'ar',
                  total_chats INTEGER DEFAULT 0,
                  is_banned INTEGER DEFAULT 0,
                  banned_until INTEGER DEFAULT 0,
                  created_at INTEGER,
                  gender TEXT,
                  preference TEXT)''')
    # جدول الجلسات النشطة
    c.execute('''CREATE TABLE IF NOT EXISTS active_sessions
                 (user_id INTEGER PRIMARY KEY,
                  partner_id INTEGER,
                  started_at INTEGER)''')
    # جدول قائمة الانتظار مع الجنس والتفضيل
    c.execute('''CREATE TABLE IF NOT EXISTS waiting_queue
                 (user_id INTEGER PRIMARY KEY,
                  joined_at INTEGER,
                  gender TEXT,
                  preference TEXT)''')
    # جدول البلاغات
    c.execute('''CREATE TABLE IF NOT EXISTS reports
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  reporter_id INTEGER,
                  reported_id INTEGER,
                  reason TEXT,
                  created_at INTEGER)''')
    # جدول الحظر (للإدارة)
    c.execute('''CREATE TABLE IF NOT EXISTS blocks
                 (user_id INTEGER PRIMARY KEY,
                  blocked_until INTEGER,
                  reason TEXT)''')
    conn.commit()
    conn.close()

# محاولة إضافة الأعمدة الجديدة إذا لم تكن موجودة (للإصدارات السابقة)
def migrate_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE users ADD COLUMN gender TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN preference TEXT")
    except:
        pass
    conn.commit()
    conn.close()

init_db()
migrate_db()

# دوال مساعدة لقاعدة البيانات
def db_execute(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(query, params)
    if fetchone:
        result = c.fetchone()
    elif fetchall:
        result = c.fetchall()
    else:
        result = None
    conn.commit()
    conn.close()
    return result

def get_user(user_id):
    return db_execute("SELECT * FROM users WHERE user_id=?", (user_id,), fetchone=True)

def create_user(user_id, first_name, lang='ar'):
    now = int(time.time())
    db_execute("INSERT OR IGNORE INTO users (user_id, first_name, created_at) VALUES (?, ?, ?)",
               (user_id, first_name, now))

def update_user_lang(user_id, lang):
    db_execute("UPDATE users SET language=? WHERE user_id=?", (lang, user_id))

def update_user_gender(user_id, gender):
    db_execute("UPDATE users SET gender=? WHERE user_id=?", (gender, user_id))

def update_user_preference(user_id, pref):
    db_execute("UPDATE users SET preference=? WHERE user_id=?", (pref, user_id))

def is_banned(user_id):
    user = get_user(user_id)
    if user and user[5] == 1:  # is_banned
        banned_until = user[6]
        if banned_until == 0 or banned_until > time.time():
            return True
        else:
            db_execute("UPDATE users SET is_banned=0, banned_until=0 WHERE user_id=?", (user_id,))
    return False

# ==================== دعم اللغات (موسع) ====================
LANGUAGES = {
    'ar': {
        'welcome': "👋 مرحباً {name}!\n🆔 معرفك: <code>{uid}</code>\n📊 إحصائياتك: {stats} محادثة\nاختر من القائمة أدناه:",
        'main_menu': "القائمة الرئيسية",
        'start_chat': "💬 بدء محادثة",
        'statistics': "📊 الإحصائيات",
        'language': "🌐 اللغة",
        'report': "📝 بلاغ",
        'finish_bot': "🚪 إنهاء البوت",
        'next': "⏩ التالي",
        'help': "❓ المساعدة",
        'user_info': "👤 معلوماتي",
        'bot_version': "ℹ️ إصدار البوت",
        'select_gender': "⚤ اختر جنسك:",
        'select_preference': "🎯 مع من تريد التحدث؟",
        'male': "ذكر",
        'female': "أنثى",
        'both': "الكل",
        'gender_saved': "✅ تم حفظ جنسك.",
        'pref_saved': "✅ تم حفظ تفضيلك. جاري البحث عن شريك...",
        'start_wait': "✨ تمت إضافتك إلى قائمة الانتظار. جاري البحث عن شريك...",
        'already_waiting': "⏳ أنت بالفعل في قائمة الانتظار.",
        'partner_found': "🎉 تم العثور على شريك! يمكنك بدء المحادثة الآن.\nأرسل /stop لإنهاء المحادثة.",
        'no_active_chat': "❌ لا توجد محادثة نشطة.",
        'chat_ended': "👋 تم إنهاء المحادثة.",
        'partner_left': "😕 غادر الطرف الآخر المحادثة.",
        'error_sending': "⚠️ خطأ في الإرسال، تم إنهاء المحادثة.",
        'report_received': "📝 تم استلام بلاغك.",
        'blocked': "🚫 أنت محظور من استخدام البوت.",
        'stats_text': "📊 إحصائياتك:\nعدد المحادثات: {total_chats}\nتاريخ الانضمام: {created_at}",
        'language_selected': "✅ تم اختيار العربية.",
        'waiting_notification': "⏰ ما زلت في قائمة الانتظار... شكراً لصبرك.",
        'cancel_wait': "تم إلغاء البحث.",
        'report_prompt': "أرسل سبب البلاغ (نصاً):",
        'invalid_report': "❌ استخدم هذا الأمر أثناء المحادثة.",
        'help_text': "📘 <b>مساعدة البوت</b>\n\n"
                     "1️⃣ للبدء: أرسل /start واختر 'بدء محادثة'.\n"
                     "2️⃣ اختر جنسك ومن تريد التحدث معه.\n"
                     "3️⃣ سيتم البحث عن شريك متوافق.\n"
                     "4️⃣ يمكنك استخدام الأزرار أثناء المحادثة.\n\n"
                     "🔹 <b>الأوامر المتاحة:</b>\n"
                     "/start - القائمة الرئيسية\n"
                     "/stop - إنهاء المحادثة\n"
                     "/next - شريك جديد\n"
                     "/lang - تغيير اللغة\n"
                     "/report - الإبلاغ عن مستخدم\n"
                     "/stats - إحصائياتك\n"
                     "/help - هذه المساعدة\n\n"
                     "⚙️ <b>الإصدار:</b> {version}\n"
                     "👨‍💻 <b>المطور:</b> @YourAdminUsername",
        'admin_panel': "🔧 لوحة التحكم",
        'broadcast': "📢 إرسال رسالة للجميع",
        'ban_user': "🔨 حظر مستخدم",
        'unban_user': "🔓 فك الحظر",
        'admin_stats': "📈 إحصائيات عامة",
        'enter_user_id': "أرسل معرف المستخدم (رقم):",
        'enter_reason': "أرسل سبب الحظر:",
        'broadcast_msg': "أرسل الرسالة التي تريد نشرها:",
        'done': "✅ تم.",
    },
    'en': {
        'welcome': "👋 Welcome {name}!\n🆔 Your ID: <code>{uid}</code>\n📊 Your stats: {stats} chats\nChoose from the menu below:",
        'main_menu': "Main Menu",
        'start_chat': "💬 Start Chat",
        'statistics': "📊 Statistics",
        'language': "🌐 Language",
        'report': "📝 Report",
        'finish_bot': "🚪 Finish Bot",
        'next': "⏩ Next",
        'help': "❓ Help",
        'user_info': "👤 My Info",
        'bot_version': "ℹ️ Bot Version",
        'select_gender': "⚤ Select your gender:",
        'select_preference': "🎯 Who do you want to chat with?",
        'male': "Male",
        'female': "Female",
        'both': "Both",
        'gender_saved': "✅ Gender saved.",
        'pref_saved': "✅ Preference saved. Searching for partner...",
        'start_wait': "✨ Added to waiting list. Searching for partner...",
        'already_waiting': "⏳ You are already in the waiting list.",
        'partner_found': "🎉 Partner found! You can start chatting now.\nSend /stop to end the chat.",
        'no_active_chat': "❌ No active chat.",
        'chat_ended': "👋 Chat ended.",
        'partner_left': "😕 Your partner left the chat.",
        'error_sending': "⚠️ Error sending message, chat ended.",
        'report_received': "📝 Report received.",
        'blocked': "🚫 You are banned from using this bot.",
        'stats_text': "📊 Your stats:\nTotal chats: {total_chats}\nJoin date: {created_at}",
        'language_selected': "✅ English selected.",
        'waiting_notification': "⏰ Still waiting... Thanks for your patience.",
        'cancel_wait': "Search cancelled.",
        'report_prompt': "Send the reason for the report (text):",
        'invalid_report': "❌ Use this command during an active chat.",
        'help_text': "📘 <b>Bot Help</b>\n\n"
                     "1️⃣ To start: send /start and choose 'Start Chat'.\n"
                     "2️⃣ Select your gender and who you want to chat with.\n"
                     "3️⃣ We'll search for a compatible partner.\n"
                     "4️⃣ You can use the buttons while chatting.\n\n"
                     "🔹 <b>Available commands:</b>\n"
                     "/start - Main menu\n"
                     "/stop - End chat\n"
                     "/next - New partner\n"
                     "/lang - Change language\n"
                     "/report - Report a user\n"
                     "/stats - Your statistics\n"
                     "/help - This help\n\n"
                     "⚙️ <b>Version:</b> {version}\n"
                     "👨‍💻 <b>Developer:</b> @YourAdminUsername",
        'admin_panel': "🔧 Control Panel",
        'broadcast': "📢 Broadcast",
        'ban_user': "🔨 Ban User",
        'unban_user': "🔓 Unban User",
        'admin_stats': "📈 Global Stats",
        'enter_user_id': "Send the user ID (number):",
        'enter_reason': "Send the ban reason:",
        'broadcast_msg': "Send the message to broadcast:",
        'done': "✅ Done.",
    }
}

def get_text(user_id, key, **kwargs):
    user = get_user(user_id)
    lang = user[2] if user else 'ar'
    text = LANGUAGES.get(lang, LANGUAGES['ar']).get(key, key)
    return text.format(**kwargs)

# ==================== إدارة قائمة الانتظار والمطابقة بالجنس ====================
def add_to_waiting(user_id, gender, preference):
    now = int(time.time())
    db_execute("INSERT OR REPLACE INTO waiting_queue (user_id, joined_at, gender, preference) VALUES (?, ?, ?, ?)",
               (user_id, now, gender, preference))

def remove_from_waiting(user_id):
    db_execute("DELETE FROM waiting_queue WHERE user_id=?", (user_id,))

def get_waiting_users():
    rows = db_execute("SELECT user_id, gender, preference FROM waiting_queue ORDER BY joined_at", fetchall=True)
    return [{'id': r[0], 'gender': r[1], 'preference': r[2]} for r in rows]

def match_users():
    """مطابقة اثنين متوافقين من قائمة الانتظار بناءً على الجنس والتفضيل."""
    waiting = get_waiting_users()
    if len(waiting) < 2:
        return False
    # محاولة إيجاد زوج متوافق
    for i, u1 in enumerate(waiting):
        for u2 in waiting[i+1:]:
            # شرط التوافق: جنس u1 يناسب تفضيل u2، وجنس u2 يناسب تفضيل u1
            if (u1['gender'] == u2['preference'] or u2['preference'] == 'both') and \
               (u2['gender'] == u1['preference'] or u1['preference'] == 'both'):
                # إزالتهما من قائمة الانتظار
                remove_from_waiting(u1['id'])
                remove_from_waiting(u2['id'])
                # إنشاء جلسة
                now = int(time.time())
                db_execute("INSERT INTO active_sessions (user_id, partner_id, started_at) VALUES (?, ?, ?)", (u1['id'], u2['id'], now))
                db_execute("INSERT INTO active_sessions (user_id, partner_id, started_at) VALUES (?, ?, ?)", (u2['id'], u1['id'], now))
                # تحديث عدد المحادثات
                db_execute("UPDATE users SET total_chats = total_chats + 1 WHERE user_id IN (?, ?)", (u1['id'], u2['id']))
                # إرسال رسالة لكليهما
                bot.send_message(u1['id'], get_text(u1['id'], 'partner_found'))
                bot.send_message(u2['id'], get_text(u2['id'], 'partner_found'))
                return True
    return False

# خلفية لإشعارات الانتظار
def waiting_notification_loop():
    while True:
        time.sleep(30)
        waiting = get_waiting_users()
        now = time.time()
        for u in waiting:
            row = db_execute("SELECT joined_at FROM waiting_queue WHERE user_id=?", (u['id'],), fetchone=True)
            if row and (now - row[0]) > 60:
                try:
                    bot.send_message(u['id'], get_text(u['id'], 'waiting_notification'))
                except:
                    pass

threading.Thread(target=waiting_notification_loop, daemon=True).start()

# ==================== إنهاء الجلسة ====================
def end_chat(user_id):
    session = db_execute("SELECT partner_id FROM active_sessions WHERE user_id=?", (user_id,), fetchone=True)
    if session:
        partner_id = session[0]
        db_execute("DELETE FROM active_sessions WHERE user_id IN (?, ?)", (user_id, partner_id))
        try:
            bot.send_message(partner_id, get_text(partner_id, 'partner_left'))
        except:
            pass
        return True
    remove_from_waiting(user_id)
    return False

# ==================== لوحة المفاتيح الرئيسية ====================
def main_menu_keyboard(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(get_text(user_id, 'start_chat'), callback_data="start_chat"),
        InlineKeyboardButton(get_text(user_id, 'statistics'), callback_data="stats"),
        InlineKeyboardButton(get_text(user_id, 'language'), callback_data="lang"),
        InlineKeyboardButton(get_text(user_id, 'report'), callback_data="report"),
        InlineKeyboardButton(get_text(user_id, 'finish_bot'), callback_data="finish"),
        InlineKeyboardButton(get_text(user_id, 'next'), callback_data="next"),
        InlineKeyboardButton(get_text(user_id, 'help'), callback_data="help"),
        InlineKeyboardButton(get_text(user_id, 'user_info'), callback_data="user_info"),
        InlineKeyboardButton(get_text(user_id, 'bot_version'), callback_data="version")
    )
    # إذا كان المستخدم هو الأدمن نضيف زر لوحة التحكم
    if user_id == ADMIN_ID:
        markup.add(InlineKeyboardButton(get_text(user_id, 'admin_panel'), callback_data="admin_panel"))
    return markup

def gender_keyboard(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(get_text(user_id, 'male'), callback_data="set_gender_male"),
        InlineKeyboardButton(get_text(user_id, 'female'), callback_data="set_gender_female")
    )
    return markup

def preference_keyboard(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(get_text(user_id, 'male'), callback_data="set_pref_male"),
        InlineKeyboardButton(get_text(user_id, 'female'), callback_data="set_pref_female"),
        InlineKeyboardButton(get_text(user_id, 'both'), callback_data="set_pref_both")
    )
    return markup

def admin_keyboard(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(get_text(user_id, 'broadcast'), callback_data="admin_broadcast"),
        InlineKeyboardButton(get_text(user_id, 'ban_user'), callback_data="admin_ban"),
        InlineKeyboardButton(get_text(user_id, 'unban_user'), callback_data="admin_unban"),
        InlineKeyboardButton(get_text(user_id, 'admin_stats'), callback_data="admin_stats"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    )
    return markup

# ==================== معالجات الأوامر ====================
@bot.message_handler(commands=['start'])
def cmd_start(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "صديق"
    if is_banned(user_id):
        bot.reply_to(message, get_text(user_id, 'blocked'))
        return
    create_user(user_id, first_name)
    end_chat(user_id)  # إنهاء أي جلسة سابقة
    user = get_user(user_id)
    total_chats = user[3] if user else 0
    created_at = datetime.fromtimestamp(user[7]).strftime('%Y-%m-%d') if user and user[7] else 'N/A'
    # استخدام uid بدلاً من user_id لتجنب التكرار في get_text
    welcome_text = get_text(user_id, 'welcome', name=first_name, uid=user_id, stats=total_chats)
    bot.send_message(user_id, welcome_text, reply_markup=main_menu_keyboard(user_id))

@bot.message_handler(commands=['stop'])
def cmd_stop(message: Message):
    user_id = message.from_user.id
    if end_chat(user_id):
        bot.reply_to(message, get_text(user_id, 'chat_ended'))
    else:
        bot.reply_to(message, get_text(user_id, 'no_active_chat'))
    cmd_start(message)  # عرض القائمة مجدداً

@bot.message_handler(commands=['next'])
def cmd_next(message: Message):
    cmd_stop(message)

@bot.message_handler(commands=['lang'])
def cmd_lang(message: Message):
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    bot.send_message(user_id, "اختر لغتك المفضلة / Choose your preferred language:", reply_markup=markup)

@bot.message_handler(commands=['report'])
def cmd_report(message: Message):
    user_id = message.from_user.id
    session = db_execute("SELECT partner_id FROM active_sessions WHERE user_id=?", (user_id,), fetchone=True)
    if not session:
        bot.reply_to(message, get_text(user_id, 'invalid_report'))
        return
    msg = bot.reply_to(message, get_text(user_id, 'report_prompt'))
    bot.register_next_step_handler(msg, process_report, session[0])

def process_report(message: Message, reported_id):
    user_id = message.from_user.id
    reason = message.text
    now = int(time.time())
    db_execute("INSERT INTO reports (reporter_id, reported_id, reason, created_at) VALUES (?, ?, ?, ?)",
               (user_id, reported_id, reason, now))
    bot.reply_to(message, get_text(user_id, 'report_received'))
    cmd_start(message)  # عودة للقائمة

@bot.message_handler(commands=['stats'])
def cmd_stats(message: Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    if user:
        total_chats = user[3]
        created_at = datetime.fromtimestamp(user[7]).strftime('%Y-%m-%d') if user[7] else 'N/A'
        text = get_text(user_id, 'stats_text', total_chats=total_chats, created_at=created_at)
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, "No stats yet.")

@bot.message_handler(commands=['help'])
def cmd_help(message: Message):
    user_id = message.from_user.id
    help_text = get_text(user_id, 'help_text', version=BOT_VERSION)
    bot.reply_to(message, help_text)

# ==================== معالجات الكول باك ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    data = call.data

    # التعامل مع تغيير اللغة
    if data.startswith('lang_'):
        lang = data.split('_')[1]
        update_user_lang(user_id, lang)
        bot.answer_callback_query(call.id, get_text(user_id, 'language_selected'))
        bot.edit_message_text(get_text(user_id, 'language_selected'), user_id, call.message.message_id)
        cmd_start(call.message)  # إعادة عرض القائمة
        return

    # أزرار القائمة الرئيسية
    if data == "start_chat":
        # التحقق من وجود الجنس والتفضيل
        user = get_user(user_id)
        gender = user[8] if len(user) > 8 else None
        pref = user[9] if len(user) > 9 else None
        if not gender:
            bot.edit_message_text(get_text(user_id, 'select_gender'), user_id, call.message.message_id,
                                  reply_markup=gender_keyboard(user_id))
        elif not pref:
            bot.edit_message_text(get_text(user_id, 'select_preference'), user_id, call.message.message_id,
                                  reply_markup=preference_keyboard(user_id))
        else:
            # تملك الجنس والتفضيل، أضف إلى قائمة الانتظار
            add_to_waiting(user_id, gender, pref)
            bot.edit_message_text(get_text(user_id, 'start_wait'), user_id, call.message.message_id)
            match_users()
        return

    elif data == "stats":
        cmd_stats(call.message)
        bot.answer_callback_query(call.id)
        return

    elif data == "lang":
        cmd_lang(call.message)
        bot.answer_callback_query(call.id)
        return

    elif data == "report":
        cmd_report(call.message)
        bot.answer_callback_query(call.id)
        return

    elif data == "finish":
        # إنهاء البوت يعني إيقاف المحادثة وإزالة من الانتظار
        end_chat(user_id)
        bot.answer_callback_query(call.id, get_text(user_id, 'chat_ended'))
        cmd_start(call.message)
        return

    elif data == "next":
        cmd_next(call.message)
        bot.answer_callback_query(call.id)
        return

    elif data == "help":
        cmd_help(call.message)
        bot.answer_callback_query(call.id)
        return

    elif data == "user_info":
        user = get_user(user_id)
        info = f"👤 <b>الاسم:</b> {user[1]}\n🆔 <b>المعرف:</b> <code>{user_id}</code>\n"
        info += f"⚤ <b>الجنس:</b> {user[8] if user[8] else 'غير محدد'}\n"
        info += f"🎯 <b>التفضيل:</b> {user[9] if user[9] else 'غير محدد'}\n"
        info += f"📊 <b>عدد المحادثات:</b> {user[3]}"
        bot.send_message(user_id, info)
        bot.answer_callback_query(call.id)
        return

    elif data == "version":
        bot.send_message(user_id, f"ℹ️ <b>إصدار البوت:</b> {BOT_VERSION}")
        bot.answer_callback_query(call.id)
        return

    # تعيين الجنس
    elif data.startswith('set_gender_'):
        gender = data.split('_')[2]
        update_user_gender(user_id, gender)
        bot.answer_callback_query(call.id, get_text(user_id, 'gender_saved'))
        # طلب التفضيل
        bot.edit_message_text(get_text(user_id, 'select_preference'), user_id, call.message.message_id,
                              reply_markup=preference_keyboard(user_id))
        return

    # تعيين التفضيل
    elif data.startswith('set_pref_'):
        pref = data.split('_')[2]
        update_user_preference(user_id, pref)
        bot.answer_callback_query(call.id, get_text(user_id, 'pref_saved'))
        # إضافة إلى قائمة الانتظار
        user = get_user(user_id)
        add_to_waiting(user_id, user[8], pref)
        bot.edit_message_text(get_text(user_id, 'start_wait'), user_id, call.message.message_id)
        match_users()
        return

    # لوحة تحكم الأدمن
    elif data == "admin_panel":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ غير مصرح")
            return
        bot.edit_message_text("🔧 لوحة التحكم", user_id, call.message.message_id,
                              reply_markup=admin_keyboard(user_id))
        return

    elif data == "back_to_main":
        cmd_start(call.message)
        bot.answer_callback_query(call.id)
        return

    # أوامر الأدمن (تتطلب خطوات متعددة، سنستخدم register_next_step_handler)
    elif data == "admin_broadcast":
        if user_id != ADMIN_ID: return
        msg = bot.send_message(user_id, get_text(user_id, 'broadcast_msg'))
        bot.register_next_step_handler(msg, process_broadcast)
        bot.answer_callback_query(call.id)
        return

    elif data == "admin_ban":
        if user_id != ADMIN_ID: return
        msg = bot.send_message(user_id, get_text(user_id, 'enter_user_id'))
        bot.register_next_step_handler(msg, process_ban_id)
        bot.answer_callback_query(call.id)
        return

    elif data == "admin_unban":
        if user_id != ADMIN_ID: return
        msg = bot.send_message(user_id, get_text(user_id, 'enter_user_id'))
        bot.register_next_step_handler(msg, process_unban)
        bot.answer_callback_query(call.id)
        return

    elif data == "admin_stats":
        if user_id != ADMIN_ID: return
        total_users = db_execute("SELECT COUNT(*) FROM users", fetchone=True)[0]
        total_chats = db_execute("SELECT SUM(total_chats) FROM users", fetchone=True)[0] or 0
        active_sessions = db_execute("SELECT COUNT(*) FROM active_sessions", fetchone=True)[0] // 2
        waiting = db_execute("SELECT COUNT(*) FROM waiting_queue", fetchone=True)[0]
        stats = f"👥 المستخدمين: {total_users}\n💬 إجمالي المحادثات: {total_chats}\n🟢 محادثات نشطة: {active_sessions}\n⏳ في الانتظار: {waiting}"
        bot.send_message(user_id, stats)
        bot.answer_callback_query(call.id)
        return

# ==================== خطوات الأدمن ====================
def process_broadcast(message: Message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        return
    text = message.text
    # الحصول على جميع المستخدمين
    users = db_execute("SELECT user_id FROM users", fetchall=True)
    success = 0
    fail = 0
    for (uid,) in users:
        try:
            bot.send_message(uid, f"📢 <b>رسالة إدارية:</b>\n\n{text}")
            success += 1
        except:
            fail += 1
    bot.reply_to(message, f"✅ تم الإرسال لـ {success} مستخدمين.\n❌ فشل لـ {fail}.")

def process_ban_id(message: Message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        return
    try:
        target_id = int(message.text)
    except:
        bot.reply_to(message, "❌ معرف غير صالح")
        return
    msg = bot.send_message(admin_id, get_text(admin_id, 'enter_reason'))
    bot.register_next_step_handler(msg, process_ban_reason, target_id)

def process_ban_reason(message: Message, target_id):
    reason = message.text
    now = int(time.time())
    # حظر لمدة غير محددة (banned_until = 0 يعني للأبد)
    db_execute("UPDATE users SET is_banned=1, banned_until=0 WHERE user_id=?", (target_id,))
    db_execute("INSERT OR REPLACE INTO blocks (user_id, blocked_until, reason) VALUES (?, 0, ?)", (target_id, reason))
    bot.reply_to(message, get_text(message.from_user.id, 'done'))

def process_unban(message: Message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        return
    try:
        target_id = int(message.text)
    except:
        bot.reply_to(message, "❌ معرف غير صالح")
        return
    db_execute("UPDATE users SET is_banned=0, banned_until=0 WHERE user_id=?", (target_id,))
    db_execute("DELETE FROM blocks WHERE user_id=?", (target_id,))
    bot.reply_to(message, get_text(admin_id, 'done'))

# ==================== معالج الرسائل (للمحادثات) ====================
@bot.message_handler(func=lambda msg: True, content_types=['text', 'photo', 'video', 'document', 'voice', 'audio', 'sticker'])
def handle_message(message: Message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, get_text(user_id, 'blocked'))
        return
    session = db_execute("SELECT partner_id FROM active_sessions WHERE user_id=?", (user_id,), fetchone=True)
    if not session:
        # إذا لم توجد محادثة نعرض القائمة
        cmd_start(message)
        return
    partner_id = session[0]
    try:
        if message.content_type == 'text':
            bot.send_message(partner_id, f"📝 {message.text}")
        elif message.content_type == 'photo':
            caption = message.caption or ""
            bot.send_photo(partner_id, message.photo[-1].file_id, caption=f"🖼️ {caption}")
        elif message.content_type == 'video':
            bot.send_video(partner_id, message.video.file_id, caption=message.caption)
        elif message.content_type == 'document':
            bot.send_document(partner_id, message.document.file_id, caption=message.caption)
        elif message.content_type == 'voice':
            bot.send_voice(partner_id, message.voice.file_id)
        elif message.content_type == 'audio':
            bot.send_audio(partner_id, message.audio.file_id, caption=message.caption)
        elif message.content_type == 'sticker':
            bot.send_sticker(partner_id, message.sticker.file_id)
        else:
            bot.reply_to(message, "نوع الرسالة غير مدعوم.")
    except Exception as e:
        print(f"Error: {e}")
        end_chat(user_id)
        bot.reply_to(message, get_text(user_id, 'error_sending'))

# ==================== بدء البوت ====================
if __name__ == '__main__':
    print("🤖 البوت الاحترافي يعمل...")
    bot.infinity_polling()
