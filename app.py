import telebot
from telebot import types
import os
import json
from functools import partial

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 7397929275
DATA_FILE = "/mnt/data/data.json"
PDF_DIR = "pdfs"

bot = telebot.TeleBot(TOKEN)

# 🔐 Majburiy obuna kanallari
FORCE_CHANNELS = [
    "@begaliev_devoleper",
    "@otaku_zone2010",
    "@motiv_kitob_tj"
    
]

if not os.path.exists(PDF_DIR):
    os.mkdir(PDF_DIR)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "categories": {}, "downloads": {}, "officers": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
# ================= FORCE SUBSCRIBE =================

def check_subscription(user_id):
    for channel in FORCE_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def send_subscribe_message(chat_id):
    markup = types.InlineKeyboardMarkup()

    for channel in FORCE_CHANNELS:
        markup.add(
            types.InlineKeyboardButton(
                text=f"➕ {channel}",
                url=f"https://t.me/{channel.replace('@','')}"
            )
        )

    markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub"))

    bot.send_message(
        chat_id,
        "📢 Botdan foydalanish uchun kanallarga obuna bo‘ling:",
        reply_markup=markup
    )        

STRINGS = {
    "uz": {
        "welcome": "Xush kelibsiz! Tilni tanlang:",
        "main_menu": "Asosiy menyu:",
        "cats": "📚 Kitoblar",
        "search": "🔍 Qidirish",
        "about": "ℹ️ Bot haqida",
        "top": "🏆 Top foydalanuvchilar",
        "admin": "➕ Admin panel",
        "search_prompt": "Kitob nomini kiriting (kamida 2 ta harf):",
        "no_results": "Hech narsa topilmadi.",
        "back": "⬅️ Orqaga",
        "category_prompt": "Kategoriya nomini yozing:",
        "book_prompt": "Kitob nomini yozing:",
        "send_pdf": "Faylni yuboring (PDF):",
        "pdf_added": "Muvaffaqiyatli qo'shildi!",
        "officer_prompt": "Ofitser bo'ladigan foydalanuvchi ID sini yozing:",
        "officer_added": "Yangi ofitser tayinlandi!",
        "not_pdf": "Bu fayl emas!",
        "admin_only": "Faqat admin yoki ofitser uchun!",
        "about_text": "Bu bot PDF kitoblarni boshqarish va ulashish uchun mo‘ljallangan."
    },
    "tj": {
        "welcome": "Хуш омадед! Забонро интихоб кунед:",
        "main_menu": "Менюи асосӣ:",
        "cats": "📚 Китобҳо",
        "search": "🔍 Ҷустуҷӯ",
        "about": "ℹ️ Дар бораи бот",
        "top": "🏆 Истифодабарандагони беҳтарин",
        "admin": "➕ Панели админ",
        "search_prompt": "Номи китобро ворид кунед (ҳадди аққал 2 ҳарф):",
        "no_results": "Ҳеҷ чиз ёфт нашуд.",
        "back": "⬅️ Ба ақиб",
        "category_prompt": "Номи категорияро нависед:",
        "book_prompt": "Номи китобро нависед:",
        "send_pdf": "Файлро фиристед (PDF):",
        "pdf_added": "Бомуваффақият илова шуд!",
        "officer_prompt": "ID-и корбареро, ки офицер мешавад, нависед:",
        "officer_added": "Офицер нав таъин шуд!",
        "not_pdf": "Ин файл нест!",
        "admin_only": "Фақат барои админ ё офицер!",
        "about_text": "Ин бот барои идора ва мубодилаи китобҳои PDF тарҳрезӣ шудааст."
    }
}

def get_lang(uid):
    data = load_data()
    return data["users"].get(str(uid), {}).get("lang", "uz")

def main_menu(message, lang=None):
    if not lang:
        lang = get_lang(message.chat.id)
    s = STRINGS[lang]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(s["cats"], s["search"])
    markup.row(s["top"], s["about"])
    data = load_data()
    if message.chat.id == ADMIN_ID or str(message.chat.id) in data["officers"]:
        markup.add(s["admin"])
    bot.send_message(message.chat.id, s["main_menu"], reply_markup=markup)

def admin_panel_markup(lang):
    s = STRINGS[lang]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ Kategoriya qo'shish", "❌ Kategoriya o'chirish")
    markup.row("➕ PDF qo'shish", "❌ PDF o'chirish")
    markup.row("📢 Kanallarga reklama", "🎖 Ofitser tayinlash")
    markup.row("📢 Reklama")
    markup.add(s["back"])
    return markup

# --- Start & til tanlash ---
@bot.message_handler(commands=['start'])
def start(message):

    if not check_subscription(message.from_user.id):
        send_subscribe_message(message.chat.id)
        return

    uid = str(message.from_user.id)
    data = load_data()
    if uid not in data["users"]:
        data["users"][uid] = {
            "lang": "uz",
            "dl_count": 0,
            "name": message.from_user.first_name
        }
        save_data(data)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("🇺🇿 O'zbek", "🇹🇯 Тоҷикӣ")
    bot.send_message(message.chat.id, STRINGS["uz"]["welcome"], reply_markup=markup)
@bot.message_handler(func=lambda m: m.text in ["🇺🇿 O'zbek", "🇹🇯 Тоҷикӣ"])
def choose_language(message):
    uid = str(message.from_user.id)
    data = load_data()
    if message.text == "🇺🇿 O'zbek":
        data["users"][uid]["lang"] = "uz"
        lang = "uz"
        lang_name = "O'zbek"
    else:
        data["users"][uid]["lang"] = "tj"
        lang = "tj"
        lang_name = "Тоҷикӣ"
    save_data(data)
    bot.send_message(message.chat.id, f"Siz {lang_name} tilini tanladingiz!")
    main_menu(message, lang)
    
@bot.message_handler(func=lambda m: m.text in ["📚 Kitoblar", "📚 Китобҳо"])
def show_categories(message):
    data = load_data()
    lang = get_lang(message.chat.id)
    
    if not data["categories"]:
        bot.send_message(message.chat.id, "Hech qanday kategoriya mavjud emas!")
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for cat in data["categories"]:
        markup.add(cat)
    markup.add(STRINGS[lang]["back"])
    
    bot.send_message(message.chat.id, "Kategoriya tanlang:", reply_markup=markup)    

# --- Admin panel ---
@bot.message_handler(func=lambda m: m.text in ["➕ Admin panel", "➕ Панели админ"])
def admin_menu(message):
    data = load_data()
    if message.chat.id != ADMIN_ID and str(message.chat.id) not in data["officers"]:
        bot.send_message(message.chat.id, STRINGS[get_lang(message.chat.id)]["admin_only"])
        return
    bot.send_message(message.chat.id, "Admin panel:", reply_markup=admin_panel_markup(get_lang(message.chat.id)))

# --- Ofitser ---
@bot.message_handler(func=lambda m: m.text == "🎖 Ofitser tayinlash")
def add_officer(message):
    data = load_data()
    if message.chat.id != ADMIN_ID and str(message.chat.id) not in data["officers"]:
        bot.send_message(message.chat.id, STRINGS[get_lang(message.chat.id)]["admin_only"])
        return
    lang = get_lang(message.chat.id)
    msg = bot.send_message(message.chat.id, STRINGS[lang]["officer_prompt"])
    bot.register_next_step_handler(msg, save_officer)

def save_officer(message):
    lang = get_lang(message.chat.id)
    text = message.text.strip()
    if not text.isdigit():
        bot.send_message(message.chat.id, "Xato ID! Faqat raqam kiriting.")
        return
    oid = str(text)
    data = load_data()
    if oid not in data["users"]:
        bot.send_message(message.chat.id, "Bu foydalanuvchi hali botni ishga tushirmagan!")
        return
    if oid not in data["officers"]:
        data["officers"].append(oid)
        save_data(data)
    bot.send_message(message.chat.id, STRINGS[lang]["officer_added"])

# --- PDF qo'shish ---
@bot.message_handler(func=lambda m: m.text == "➕ PDF qo'shish")
def add_pdf_start(message):
    data = load_data()
    if message.chat.id != ADMIN_ID and str(message.chat.id) not in data["officers"]:
        bot.send_message(message.chat.id, STRINGS[get_lang(message.chat.id)]["admin_only"])
        return
    lang = get_lang(message.chat.id)
    msg = bot.send_message(message.chat.id, STRINGS[lang]["category_prompt"])
    bot.register_next_step_handler(msg, add_pdf_name_step)

def add_pdf_name_step(message):
    cat = message.text.strip()
    lang = get_lang(message.chat.id)
    msg = bot.send_message(message.chat.id, STRINGS[lang]["book_prompt"])
    bot.register_next_step_handler(msg, lambda m: add_pdf_file_step(m, cat))

def add_pdf_file_step(message, cat):
    name = message.text.strip()
    lang = get_lang(message.chat.id)
    msg = bot.send_message(message.chat.id, STRINGS[lang]["send_pdf"])
    bot.register_next_step_handler(msg, lambda m: final_save_pdf(m, cat, name))

def final_save_pdf(message, cat, name):
    lang = get_lang(message.chat.id)
    if not message.document or not message.document.file_name.endswith(".pdf"):
        bot.send_message(message.chat.id, STRINGS[lang]["not_pdf"])
        return
    
    # Faylni yuklab o'tirmaymiz, shunchaki Telegram bergan ID ni olamiz
    file_id = message.document.file_id
    
    data = load_data()
    if cat not in data["categories"]:
        data["categories"][cat] = {}
    
    # Path o'rniga file_id ni saqlaymiz
    data["categories"][cat][name] = {"file_id": file_id} 
    save_data(data)
    bot.send_message(message.chat.id, STRINGS[lang]["pdf_added"])


# ================= PDF o'chirish =================
@bot.message_handler(func=lambda m: m.text == "❌ PDF o'chirish")
def delete_pdf_start(message):
    data = load_data()
    if message.chat.id != ADMIN_ID and str(message.chat.id) not in data["officers"]:
        bot.send_message(message.chat.id, STRINGS[get_lang(message.chat.id)]["admin_only"])
        return
    if not data["categories"]:
        bot.send_message(message.chat.id, "Hech qanday kategoriya mavjud emas!")
        return
    lang = get_lang(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for cat in data["categories"]:
        markup.add(cat)
    markup.add(STRINGS[lang]["back"])
    msg = bot.send_message(message.chat.id, "O'chirish uchun kategoriya tanlang:", reply_markup=markup)
    bot.register_next_step_handler(msg, select_category_for_pdf_delete)

def select_category_for_pdf_delete(message):
    cat_name = message.text.strip()
    data = load_data()
    lang = get_lang(message.chat.id)
    if cat_name == STRINGS[lang]["back"]:
        main_menu(message, lang)
        return
    if cat_name not in data["categories"]:
        bot.send_message(message.chat.id, "Bunday kategoriya topilmadi!")
        return
    books = list(data["categories"][cat_name].keys())
    if not books:
        bot.send_message(message.chat.id, "Bu kategoriyada PDF mavjud emas!")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for book in books:
        markup.add(book)
    markup.add(STRINGS[lang]["back"])
    msg = bot.send_message(message.chat.id, "O'chirish uchun PDF tanlang:", reply_markup=markup)
    bot.register_next_step_handler(msg, partial(delete_selected_pdf, cat_name))

def delete_selected_pdf(cat_name, message):
    pdf_name = message.text.strip()
    data = load_data()
    lang = get_lang(message.chat.id)
    
    if pdf_name == STRINGS[lang]["back"]:
        main_menu(message, lang)
        return
        
    if cat_name in data["categories"] and pdf_name in data["categories"][cat_name]:
        # os.remove(file_path) kerak emas, chunki fayl diskda emas, Telegramda
        del data["categories"][cat_name][pdf_name]
        save_data(data)
        bot.send_message(message.chat.id, f"PDF '{pdf_name}' muvaffaqiyatli o‘chirildi!")
    else:
        bot.send_message(message.chat.id, "Bunday PDF topilmadi!")
    
    main_menu(message, lang) # Menyoga qaytarish

# ================= Kategoriya qo'shish / o'chirish =================
@bot.message_handler(func=lambda m: m.text == "➕ Kategoriya qo'shish")
def add_category_start(message):
    data = load_data()
    uid = str(message.chat.id)
    if message.chat.id != ADMIN_ID and uid not in data["officers"]:
        bot.send_message(message.chat.id, STRINGS[get_lang(message.chat.id)]["admin_only"])
        return
    lang = get_lang(message.chat.id)
    msg = bot.send_message(message.chat.id, STRINGS[lang]["category_prompt"])
    bot.register_next_step_handler(msg, save_category_step)

def save_category_step(message):
    cat_name = message.text.strip()
    data = load_data()
    lang = get_lang(message.chat.id)
    if not cat_name:
        bot.send_message(message.chat.id, "Kategoriya nomi bo‘sh bo‘lishi mumkin emas!")
        return
    if cat_name in data["categories"]:
        bot.send_message(message.chat.id, f"Kategoriya '{cat_name}' allaqachon mavjud!")
        return
    data["categories"][cat_name] = {}
    save_data(data)
    bot.send_message(message.chat.id, f"Kategoriya '{cat_name}' muvaffaqiyatli qo‘shildi!")
    main_menu(message, lang)

@bot.message_handler(func=lambda m: m.text == "❌ Kategoriya o'chirish")
def delete_category_start(message):
    data = load_data()
    uid = str(message.chat.id)
    if message.chat.id != ADMIN_ID and uid not in data["officers"]:
        bot.send_message(message.chat.id, STRINGS[get_lang(message.chat.id)]["admin_only"])
        return
    
    if not data["categories"]:
        bot.send_message(message.chat.id, "Hech qanday kategoriya mavjud emas!")
        return
        
    lang = get_lang(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for cat in data["categories"]:
        markup.add(cat)
    markup.add(STRINGS[lang]["back"])
    
    msg = bot.send_message(message.chat.id, "O'chirish uchun kategoriya tanlang:", reply_markup=markup)
    bot.register_next_step_handler(msg, delete_category_step)

def delete_category_step(message):
    cat_name = message.text.strip()
    data = load_data()
    lang = get_lang(message.chat.id)
    
    if cat_name == STRINGS[lang]["back"]:
        main_menu(message, lang)
        return
        
    if cat_name in data["categories"]:
        # Diqqat: Siz PDF-larni file_id ko'rinishida saqlayotganingiz uchun 
        # os.remove() ishlatish shart emas va u xato beradi.
        # Shunchaki JSON lug'atidan o'chirib yuboramiz.
        del data["categories"][cat_name]
        save_data(data)
        bot.send_message(message.chat.id, f"✅ Kategoriya '{cat_name}' va uning ichidagi barcha PDF-lar muvaffaqiyatli o‘chirildi!")
    else:
        bot.send_message(message.chat.id, "❌ Bunday kategoriya topilmadi!")
    
    main_menu(message, lang)

# --- Top foydalanuvchilar ---
@bot.message_handler(func=lambda m: m.text in ["🏆 Top foydalanuvchilar", "🏆 Истифодабарандагони беҳтарин"])
def show_top(message):
    data = load_data()
    users = data["users"]
    sorted_users = sorted(users.items(), key=lambda x: x[1].get("dl_count",0), reverse=True)[:5]
    text = "🏆 TOP 5:\n\n"
    for i,(uid, info) in enumerate(sorted_users,1):
        text += f"{i}. {info.get('name','User')} — {info.get('dl_count',0)} ta kitob\n"
    bot.send_message(message.chat.id, text)

# --- Reklama ---
@bot.message_handler(func=lambda m: m.text == "📢 Reklama")
def send_broadcast_start(message):
    data = load_data()
    if message.chat.id != ADMIN_ID and str(message.chat.id) not in data["officers"]:
        bot.send_message(message.chat.id, STRINGS[get_lang(message.chat.id)]["admin_only"])
        return
    msg = bot.send_message(message.chat.id, "Xabar matnini kiriting:")
    bot.register_next_step_handler(msg, broadcast_message)

def broadcast_message(message):
    text = message.text
    data = load_data()
    count = 0
    for uid in data["users"]:
        try:
            bot.send_message(int(uid), text)
            count += 1
        except:
            continue
    bot.send_message(message.chat.id, f"Xabar {count} foydalanuvchiga yuborildi!")

# --- About ---
@bot.message_handler(func=lambda m: m.text in ["ℹ️ Bot haqida", "ℹ️ Дар бораи бот"])
def about_bot(message):
    lang = get_lang(message.chat.id)
    bot.send_message(message.chat.id, STRINGS[lang]["about_text"])

# --- Back ---
@bot.message_handler(func=lambda m: m.text in ["⬅️ Orqaga","⬅️ Ба ақиб"])
def back_to_main(message):
    main_menu(message, get_lang(message.chat.id))

@bot.message_handler(func=lambda m: True)
def category_or_pdf_handler(message):
    data = load_data()
    uid = str(message.chat.id)
    lang = get_lang(message.chat.id)
    text = message.text.strip()

    # Foydalanuvchini ro'yxatga olish va dl_count boshlang'ich qiymati
    if uid not in data["users"]:
        data["users"][uid] = {"name": message.from_user.first_name, "dl_count": 0}
        save_data(data)

    # 🔙 Orqaga tugmasi
    if text == STRINGS[lang]["back"]:
        main_menu(message, lang)
        return

    # 📚 Kategoriya tanlandi
    if text in data["categories"]:
        books = data["categories"][text]
        if not books:
            bot.send_message(message.chat.id, "Bu kategoriyada PDF mavjud emas!")
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for book in books.keys():
            markup.add(book)
        markup.add(STRINGS[lang]["back"])
        bot.send_message(message.chat.id, f"📚 {text} bo'limi:", reply_markup=markup)
        return

    # 📖 PDF tanlandi
    for cat_name, books in data["categories"].items():
        if text in books:
            book_data = books[text]
            file_id = book_data.get("file_id") if isinstance(book_data, dict) else None
            if file_id:
                try:
                    bot.send_document(message.chat.id, file_id, caption=f"📖 {text}")
                    # ✅ dl_count oshiriladi
                    data["users"][uid]["dl_count"] = data["users"][uid].get("dl_count",0) + 1
                    save_data(data)
                except Exception as e:
                    bot.send_message(message.chat.id, f"Y:✅{e}")
            return
    # Agar hech narsa topilmasa — jim turadi

# Global set foydalanuvchilar qidiruvini boshqarish uchun
SEARCH_USERS = set()

# --- Qidiruvni boshlash ---
@bot.message_handler(func=lambda m: m.text in ["🔍 Qidirish", "🔍 Ҷустуҷӯ"])
def ask_search(message):
    lang = get_lang(message.chat.id)
    msg = bot.send_message(message.chat.id, STRINGS[lang]["search_prompt"])
    # Foydalanuvchini qidiruv jarayonida ekanini belgilaymiz
    SEARCH_USERS.add(message.chat.id)

# --- Qidiruvni qabul qilish ---
@bot.message_handler(func=lambda m: m.chat.id in SEARCH_USERS)
def process_search_wrapper(message):
    SEARCH_USERS.discard(message.chat.id)  # Foydalanuvchi endi qidiruvda emas
    process_search(message)                 # Asosiy qidiruv funksiyasini chaqiramiz

# --- Asosiy qidiruv funksiyasi ---
def process_search(message):
    query = message.text.strip().lower()
    lang = get_lang(message.chat.id)

    # Kamida 2 harf bo'lishi kerak
    if len(query) < 2:
        bot.send_message(message.chat.id, "Kamida 2 ta harf kiriting!")
        return

    data = load_data()
    results = []

    # Har bir kategoriya va kitobni tekshiramiz
    for cat, books in data["categories"].items():
        for book_name in books.keys():
            if query in book_name.lower():
                results.append(book_name)

    # Natija topilmasa
    if not results:
        bot.send_message(message.chat.id, STRINGS[lang]["no_results"])
        return

    # Natijalarni inline tugmalar bilan yuborish
    markup = types.InlineKeyboardMarkup()
    for book_name in results[:10]:  # maksimal 10 ta natija
        callback_val = f"get_{book_name[:50]}"  # callback max 64 byte
        markup.add(types.InlineKeyboardButton(text=f"📖 {book_name}", callback_data=callback_val))

    bot.send_message(message.chat.id, "Natijalar:", reply_markup=markup)

# --- Inline tugma orqali PDF yuborish ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("get_"))
def callback_get_pdf(call):
    data = load_data()
    search_name = call.data.replace("get_", "") 
    uid = str(call.from_user.id)
    
    file_id = None
    full_book_name = ""

    for cat, books in data["categories"].items():
        for b_name, b_info in books.items():
            if b_name.startswith(search_name):
                file_id = b_info.get("file_id")
                full_book_name = b_name
                break
        if file_id: break

    if file_id:
        try:
            bot.send_document(call.message.chat.id, file_id, caption=f"📖 {full_book_name}")
            # Statistika kodini shu yerda davom ettiring...
            bot.answer_callback_query(call.id, "Yuborilmoqda...")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Xato: {e}")
    else:
        bot.answer_callback_query(call.id, "Fayl topilmadi!", show_alert=True)
        
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_callback(call):

    if check_subscription(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Tasdiqlandi!")
        main_menu(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo‘lmagansiz!", show_alert=True)   
             
@bot.message_handler(func=lambda m: m.text == "📢 Kanallarga reklama")
def send_broadcast_to_channels(message):
    data = load_data()
    if message.chat.id != ADMIN_ID and str(message.chat.id) not in data["officers"]:
        bot.send_message(message.chat.id, STRINGS[get_lang(message.chat.id)]["admin_only"])
        return

    msg = bot.send_message(message.chat.id, "Kanallarga yuboriladigan xabar matnini kiriting:")
    bot.register_next_step_handler(msg, broadcast_to_channels)

def broadcast_to_channels(message):
    text = message.text
    channels = ["@otaku_zone2010", "@motiv_kitob_tj"]  # Bot admin bo‘lgan kanallar
    sent_count = 0
    for ch in channels:
        try:
            bot.send_message(ch, text)
            sent_count += 1
        except Exception as e:
            bot.send_message(message.chat.id, f"Kanalga yuborishda xato: {ch} — {e}")

    bot.send_message(message.chat.id, f"Xabar {sent_count} kanallarga yuborildi!")

print("Bot ishga tushdi...")
bot.infinity_polling()
