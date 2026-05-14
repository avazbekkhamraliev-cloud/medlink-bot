"""
MedLink Telegram Bot — Bemor uchun shifokorga yozilish
======================================================
O'rnatish:
  pip install pyTelegramBotAPI

Ishga tushirish:
  1. @BotFather dan bot yarating, TOKEN oling
  2. BOT_TOKEN = "sizning_tokeningiz" ni o'zgartiring
  3. python medlink_bot.py

Kontakt: @exclusivnie | +998 91 657 02 22
"""

import telebot
from telebot import types
from datetime import datetime

# ══════════════════════════════════════
# SOZLAMALAR
# ══════════════════════════════════════
BOT_TOKEN = "SIZNING_BOT_TOKENINGIZ"  # @BotFather dan oling
ADMIN_ID   = "998916570222"           # Sizning Telegram ID ingiz

bot = telebot.TeleBot(BOT_TOKEN)

# ══════════════════════════════════════
# MA'LUMOTLAR BAZASI (oddiy, xotirada)
# Keyinchalik Google Sheets yoki SQL ga o'tkazish mumkin
# ══════════════════════════════════════

KLINIKALAR = {
    "1": {
        "nomi": "MedLife Klinikasi",
        "manzil": "Yunusobod, 7-mavze",
        "telefon": "+998 71 123 45 67",
        "shifokorlar": {
            "101": {"ismi": "Dr. Nilufar Karimova", "mutaxassis": "Kardiolog", "narx": "150,000 so'm", "vaqtlar": ["09:00", "10:30", "12:00", "14:00", "15:30"]},
            "102": {"ismi": "Dr. Bobur Rashidov",   "mutaxassis": "Nevrolog",  "narx": "120,000 so'm", "vaqtlar": ["09:30", "11:00", "13:00", "15:00", "16:30"]},
        }
    },
    "2": {
        "nomi": "Salomatlik Markazi",
        "manzil": "Chilonzor, 9-kvartal",
        "telefon": "+998 71 234 56 78",
        "shifokorlar": {
            "201": {"ismi": "Dr. Malika Yusupova",  "mutaxassis": "Pediatr",    "narx": "100,000 so'm", "vaqtlar": ["08:30", "10:00", "11:30", "13:30", "15:00"]},
            "202": {"ismi": "Dr. Jasur Toshmatov",  "mutaxassis": "Terapevt",   "narx": "80,000 so'm",  "vaqtlar": ["09:00", "10:30", "12:00", "14:30", "16:00"]},
        }
    },
    "3": {
        "nomi": "Shifo Plus",
        "manzil": "Mirzo Ulug'bek, 15-uy",
        "telefon": "+998 71 345 67 89",
        "shifokorlar": {
            "301": {"ismi": "Dr. Zulfiya Nazarova", "mutaxassis": "Ginekolog",  "narx": "180,000 so'm", "vaqtlar": ["09:00", "11:00", "13:00", "15:00", "17:00"]},
            "302": {"ismi": "Dr. Anvar Xolmatov",   "mutaxassis": "Ortoped",    "narx": "130,000 so'm", "vaqtlar": ["10:00", "12:00", "14:00", "16:00"]},
        }
    },
}

# Foydalanuvchi holati (sessiya)
user_state = {}

# Bronlar ro'yxati
bronlar = []

# ══════════════════════════════════════
# YORDAMCHI FUNKSIYALAR
# ══════════════════════════════════════

def get_state(uid):
    if uid not in user_state:
        user_state[uid] = {}
    return user_state[uid]

def set_state(uid, key, val):
    if uid not in user_state:
        user_state[uid] = {}
    user_state[uid][key] = val

def clear_state(uid):
    user_state[uid] = {}

def bron_raqami():
    return f"ML{datetime.now().strftime('%d%m%H%M')}{len(bronlar)+1:03d}"

# ══════════════════════════════════════
# /start — BOSH MENYU
# ══════════════════════════════════════

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    clear_state(uid)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🔍 Shifokor topish"),
        types.KeyboardButton("📅 Mening bronlarim"),
        types.KeyboardButton("🏥 Klinikalar"),
        types.KeyboardButton("📞 Aloqa"),
    )

    name = message.from_user.first_name or "Foydalanuvchi"
    bot.send_message(
        message.chat.id,
        f"👋 Assalomu alaykum, *{name}*!\n\n"
        f"🏥 *MedLink* — xususiy klinikalarga onlayn yozilish platformasi\n\n"
        f"Navbat kutmasdan, telefon qilmasdan — 2 daqiqada shifokorga yoziling!\n\n"
        f"Quyidagi tugmalardan birini tanlang 👇",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ══════════════════════════════════════
# SHIFOKOR TOPISH — MUTAXASSIS TANLASH
# ══════════════════════════════════════

@bot.message_handler(func=lambda m: m.text == "🔍 Shifokor topish")
def shifokor_topish(message):
    uid = message.from_user.id
    clear_state(uid)
    set_state(uid, "qadam", "mutaxassis")

    mutaxassislar = set()
    for k in KLINIKALAR.values():
        for sh in k["shifokorlar"].values():
            mutaxassislar.add(sh["mutaxassis"])

    markup = types.InlineKeyboardMarkup(row_width=2)
    for m in sorted(mutaxassislar):
        markup.add(types.InlineKeyboardButton(f"👨‍⚕️ {m}", callback_data=f"mutax_{m}"))

    bot.send_message(
        message.chat.id,
        "🔍 *Qaysi mutaxassisni qidirmoqdasiz?*\n\nQuyidan tanlang:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("mutax_"))
def mutaxassis_tanlandi(call):
    uid = call.from_user.id
    mutax = call.data.replace("mutax_", "")
    set_state(uid, "mutaxassis", mutax)
    set_state(uid, "qadam", "klinika")

    # Ushbu mutaxassis bor klinikalarni topish
    topilganlar = []
    for kid, k in KLINIKALAR.items():
        for shid, sh in k["shifokorlar"].items():
            if sh["mutaxassis"] == mutax:
                topilganlar.append((kid, shid, k, sh))

    markup = types.InlineKeyboardMarkup(row_width=1)
    for kid, shid, k, sh in topilganlar:
        markup.add(types.InlineKeyboardButton(
            f"🏥 {k['nomi']} — {sh['ismi']} ({sh['narx']})",
            callback_data=f"shifokor_{kid}_{shid}"
        ))

    bot.edit_message_text(
        f"✅ *{mutax}* bo'yicha shifokorlar:\n\nMos variantni tanlang 👇",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ══════════════════════════════════════
# SHIFOKOR TANLASH
# ══════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data.startswith("shifokor_"))
def shifokor_tanlandi(call):
    uid = call.from_user.id
    _, kid, shid = call.data.split("_")
    k = KLINIKALAR[kid]
    sh = k["shifokorlar"][shid]

    set_state(uid, "klinika_id", kid)
    set_state(uid, "shifokor_id", shid)
    set_state(uid, "qadam", "vaqt")

    markup = types.InlineKeyboardMarkup(row_width=3)
    for vaqt in sh["vaqtlar"]:
        markup.add(types.InlineKeyboardButton(f"🕐 {vaqt}", callback_data=f"vaqt_{vaqt}"))
    markup.add(types.InlineKeyboardButton("⬅️ Orqaga", callback_data=f"mutax_{sh['mutaxassis']}"))

    bot.edit_message_text(
        f"👨‍⚕️ *{sh['ismi']}*\n"
        f"🏥 {k['nomi']}\n"
        f"📍 {k['manzil']}\n"
        f"💰 Qabul narxi: *{sh['narx']}*\n\n"
        f"⏰ *Qulay vaqtni tanlang:*",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ══════════════════════════════════════
# VAQT TANLASH
# ══════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data.startswith("vaqt_"))
def vaqt_tanlandi(call):
    uid = call.from_user.id
    vaqt = call.data.replace("vaqt_", "")
    set_state(uid, "vaqt", vaqt)
    set_state(uid, "qadam", "ism")

    bot.edit_message_text(
        f"✅ Vaqt tanlandi: *{vaqt}*\n\n"
        f"📝 Iltimos, to'liq ismingizni yozing:\n_(Masalan: Alisher Karimov)_",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

# ══════════════════════════════════════
# ISM KIRITISH
# ══════════════════════════════════════

@bot.message_handler(func=lambda m: get_state(m.from_user.id).get("qadam") == "ism")
def ism_kiritish(message):
    uid = message.from_user.id
    set_state(uid, "ism", message.text)
    set_state(uid, "qadam", "telefon")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📱 Raqamimni yuborish", request_contact=True))

    bot.send_message(
        message.chat.id,
        f"👤 *{message.text}*\n\n"
        f"📞 Telefon raqamingizni yuboring yoki qo'lda kiriting:\n_(Masalan: +998901234567)_",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ══════════════════════════════════════
# TELEFON — KONTAKT ORQALI
# ══════════════════════════════════════

@bot.message_handler(content_types=['contact'])
def kontakt_qabul(message):
    uid = message.from_user.id
    if get_state(uid).get("qadam") != "telefon":
        return
    telefon = message.contact.phone_number
    if not telefon.startswith("+"):
        telefon = "+" + telefon
    set_state(uid, "telefon", telefon)
    tasdiqlash(message)

# ══════════════════════════════════════
# TELEFON — QO'LDA KIRITISH
# ══════════════════════════════════════

@bot.message_handler(func=lambda m: get_state(m.from_user.id).get("qadam") == "telefon")
def telefon_kiritish(message):
    uid = message.from_user.id
    telefon = message.text.strip()
    if not any(c.isdigit() for c in telefon):
        bot.send_message(message.chat.id, "❌ Iltimos, to'g'ri telefon raqam kiriting.")
        return
    set_state(uid, "telefon", telefon)
    tasdiqlash(message)

# ══════════════════════════════════════
# TASDIQLASH
# ══════════════════════════════════════

def tasdiqlash(message):
    uid = message.from_user.id
    st = get_state(uid)

    kid = st["klinika_id"]
    shid = st["shifokor_id"]
    k = KLINIKALAR[kid]
    sh = k["shifokorlar"][shid]

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_yes"),
        types.InlineKeyboardButton("❌ Bekor qilish", callback_data="confirm_no"),
    )

    bot.send_message(
        message.chat.id,
        f"📋 *Bronni tasdiqlang:*\n\n"
        f"👤 Ism: *{st['ism']}*\n"
        f"📞 Telefon: *{st['telefon']}*\n"
        f"👨‍⚕️ Shifokor: *{sh['ismi']}*\n"
        f"🏥 Klinika: *{k['nomi']}*\n"
        f"📍 Manzil: {k['manzil']}\n"
        f"⏰ Vaqt: *{st['vaqt']}*\n"
        f"💰 Narx: *{sh['narx']}*\n\n"
        f"Tasdiqlaysizmi?",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda c: c.data == "confirm_yes")
def bron_tasdiqlandi(call):
    uid = call.from_user.id
    st = get_state(uid)

    kid = st["klinika_id"]
    shid = st["shifokor_id"]
    k = KLINIKALAR[kid]
    sh = k["shifokorlar"][shid]
    raqam = bron_raqami()

    # Bronni saqlash
    bron = {
        "raqam": raqam,
        "uid": uid,
        "ism": st["ism"],
        "telefon": st["telefon"],
        "klinika": k["nomi"],
        "shifokor": sh["ismi"],
        "mutaxassis": sh["mutaxassis"],
        "vaqt": st["vaqt"],
        "narx": sh["narx"],
        "sana": datetime.now().strftime("%d.%m.%Y"),
        "holat": "tasdiqlangan"
    }
    bronlar.append(bron)

    # Foydalanuvchiga xabar
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🔍 Shifokor topish"),
        types.KeyboardButton("📅 Mening bronlarim"),
        types.KeyboardButton("🏥 Klinikalar"),
        types.KeyboardButton("📞 Aloqa"),
    )

    bot.edit_message_text(
        f"🎉 *Bron muvaffaqiyatli qilindi!*\n\n"
        f"📌 Bron raqami: `{raqam}`\n\n"
        f"👨‍⚕️ {sh['ismi']}\n"
        f"🏥 {k['nomi']}\n"
        f"📍 {k['manzil']}\n"
        f"⏰ Bugun soat {st['vaqt']}\n"
        f"💰 {sh['narx']}\n\n"
        f"📞 Klinika telefoni: {k['telefon']}\n\n"
        f"⚠️ Qabuldan 1 soat oldin eslatma keladi!\n"
        f"❌ Bekor qilish uchun /bronlar buyrug'ini yuboring.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

    bot.send_message(call.message.chat.id, "Bosh menyuga qaytdingiz 👇", reply_markup=markup)

    # Adminga xabar
    try:
        bot.send_message(
            ADMIN_ID,
            f"🔔 *Yangi bron!*\n\n"
            f"📌 #{raqam}\n"
            f"👤 {bron['ism']} — {bron['telefon']}\n"
            f"👨‍⚕️ {bron['shifokor']} ({bron['mutaxassis']})\n"
            f"🏥 {bron['klinika']}\n"
            f"⏰ {bron['vaqt']}",
            parse_mode="Markdown"
        )
    except:
        pass

    clear_state(uid)

@bot.callback_query_handler(func=lambda c: c.data == "confirm_no")
def bron_bekor(call):
    uid = call.from_user.id
    clear_state(uid)
    bot.edit_message_text(
        "❌ Bron bekor qilindi.\n\n/start — bosh menyuga qaytish",
        call.message.chat.id,
        call.message.message_id
    )

# ══════════════════════════════════════
# MENING BRONLARIM
# ══════════════════════════════════════

@bot.message_handler(func=lambda m: m.text == "📅 Mening bronlarim")
def mening_bronlarim(message):
    uid = message.from_user.id
    mening = [b for b in bronlar if b["uid"] == uid]

    if not mening:
        bot.send_message(
            message.chat.id,
            "📭 Sizda hozircha bron yo'q.\n\n🔍 Shifokor topish tugmasini bosing!"
        )
        return

    matn = "📅 *Sizning bronlaringiz:*\n\n"
    for b in mening[-5:]:
        matn += (
            f"📌 `{b['raqam']}` — *{b['holat']}*\n"
            f"👨‍⚕️ {b['shifokor']}\n"
            f"🏥 {b['klinika']} — ⏰ {b['vaqt']}\n"
            f"💰 {b['narx']}\n\n"
        )

    bot.send_message(message.chat.id, matn, parse_mode="Markdown")

# ══════════════════════════════════════
# KLINIKALAR RO'YXATI
# ══════════════════════════════════════

@bot.message_handler(func=lambda m: m.text == "🏥 Klinikalar")
def klinikalar(message):
    matn = "🏥 *Platformamizdagi klinikalar:*\n\n"
    for k in KLINIKALAR.values():
        matn += f"🏥 *{k['nomi']}*\n"
        matn += f"📍 {k['manzil']}\n"
        matn += f"📞 {k['telefon']}\n"
        shifokorlar = ", ".join(sh["mutaxassis"] for sh in k["shifokorlar"].values())
        matn += f"👨‍⚕️ {shifokorlar}\n\n"

    bot.send_message(message.chat.id, matn, parse_mode="Markdown")

# ══════════════════════════════════════
# ALOQA
# ══════════════════════════════════════

@bot.message_handler(func=lambda m: m.text == "📞 Aloqa")
def aloqa(message):
    bot.send_message(
        message.chat.id,
        "📞 *MedLink bilan bog'lanish:*\n\n"
        "💬 Telegram: @exclusivnie\n"
        "📱 Telefon: +998 91 657 02 22\n\n"
        "Klinikangizni platformaga qo'shish uchun yozing!",
        parse_mode="Markdown"
    )

# ══════════════════════════════════════
# ADMIN — /bronlar
# ══════════════════════════════════════

@bot.message_handler(commands=['bronlar'])
def admin_bronlar(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    if not bronlar:
        bot.send_message(message.chat.id, "Hozircha bron yo'q.")
        return
    matn = f"📊 *Jami bronlar: {len(bronlar)}*\n\n"
    for b in bronlar[-10:]:
        matn += f"📌 `{b['raqam']}` | {b['ism']} | {b['shifokor']} | {b['vaqt']}\n"
    bot.send_message(message.chat.id, matn, parse_mode="Markdown")

# ══════════════════════════════════════
# ISHGA TUSHIRISH
# ══════════════════════════════════════

print("✅ MedLink bot ishga tushdi...")
print("📱 @exclusivnie | +998 91 657 02 22")
bot.infinity_polling()
