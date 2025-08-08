import logging
import os
import random
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# -------------- CONFIG --------------
TOKEN = "7570796885:AAHHfpXanemNYvW-wVT2Rv40U0xq-XjxSwk"
ADMIN_IDS = [6578706277, 7853664401]
CHANNEL_USERNAME = "@Kitobxon_Kids"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# -------------- STATE GROUPS --------------
class Registration(StatesGroup):
    check_subscription = State()
    child_name = State()
    parent_name = State()
    region = State()
    district = State()
    mahalla = State()
    age = State()
    phone = State()
    feedback = State()

class TakingTest(StatesGroup):
    idle = State()
    answering = State()

# -------------- MENUS --------------
menu = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("📖 Testni boshlash")
).add(
    KeyboardButton("📚 Loyiha haqida"), KeyboardButton("💬 Fikr va maslahatlar")
)

admin_menu = ReplyKeyboardMarkup(resize_keyboard=True).row(
    KeyboardButton("🆕 Test yuklash"), KeyboardButton("🗑 Testni o‘chirish")
).add(
    KeyboardButton("📋 Foydalanuvchilar ro‘yxati")
).add(
    KeyboardButton("⬅ Asosiy menyu")
)

# -------------- REGIONS DATA --------------
REGIONS = {
   "Toshkent shahri": ["Bektemir", "Chilonzor", "Mirzo Ulug‘bek", "Mirobod", "Olmazor", "Shayxontohur", "Sergeli", "Uchtepa", "Yashnobod", "Yakkasaroy", "Yunusobod"],
    "Toshkent viloyati": ["Bekabad", "Bo‘ka", "Bo‘stonliq", "Chinoz", "Chirchiq", "Ohangaron", "Oqqo‘rg‘on", "Parkent", "Piskent", "Quyichirchiq", "O‘rtachirchiq", "Yangiyo‘l", "Toshkent", "Yuqorichirchiq", "Zangiota", "Nurafshon", "Olmaliq", "Angren"],
    "Andijon": ["Andijon shahri", "Asaka", "Baliqchi", "Bo‘ston", "Buloqboshi", "Izboskan", "Jalaquduq", "Marhamat", "Oltinko‘l", "Paxtaobod", "Paytug‘", "Qo‘rg‘ontepa", "Shahriston", "Xo‘jaobod"],
    "Farg‘ona": ["Beshariq", "Buvayda", "Dang‘ara", "Farg‘ona shahri", "Ferghana tumani", "Furqat", "Qo‘qon", "Quva", "Rishton", "So‘x", "Toshloq", "Uchko‘prik", "Yozyovon", "Oltiariq"],
    "Namangan": ["Chortoq", "Chust", "Kosonsoy", "Namangan shahri", "Norin", "Pop", "To‘raqo‘rg‘on", "Uychi", "Uchqo‘rg‘on", "Yangiqo‘rg‘on", "Yangihayot"],
    "Samarqand": ["Bulung‘ur", "Ishtixon", "Jomboy", "Kattakurgan", "Oqdaryo", "Payariq", "Pastdarg‘om", "Qo‘shrabot", "Samarqand shahri", "Toyloq", "Urgut"],
    "Buxoro": ["Buxoro shahri", "Buxoro tumani", "G‘ijduvon", "Jondor", "Kogon", "Olot", "Peshku", "Qorako‘l", "Qorovulbozor", "Romitan", "Shofirkon", "Vobkent"],
    "Jizzax": ["Baxmal", "Chiroqchi", "Do‘stlik", "Forish", "G‘allaorol", "Zafarobod", "Zarbdor", "Zomin", "Zafar", "Yangiobod", "Jizzax shahri", "Mirzacho‘l"],
    "Navoiy": ["Bespah", "Karmana", "Konimex", "Navbahor", "Nurota", "Tomdi", "Xatirchi", "Uchquduq", "Navoiy shahri", "Zarafshon"],
    "Qashqadaryo": ["Chiroqchi", "G‘uzor", "Qarshi", "Kitob", "Koson", "Mirishkor", "Muborak", "Nishon", "Shahrisabz", "Dehqonobod", "Yakkabog‘"],
    "Surxondaryo": ["Angor", "Bandixon", "Denov", "Jarqo‘rg‘on", "Muzrabot", "Oltinsoy", "Sariosiyo", "Sherobod", "Sho‘rchi", "Termiz", "Uzun", "Boysun"],
    "Sirdaryo": ["Guliston", "Guliston tumani", "Mirzaobod", "Oqoltin", "Sardoba", "Sayxunobod", "Sirdaryo tumani", "Xovos", "Boyovut", "Yangiyer"],
    "Xorazm": ["Bog‘ot", "Gurlan", "Hazorasp", "Khiva", "Qo‘shko‘pir", "Shovot", "Urganch tumani", "Xonqa", "Yangiariq", "Yangibozor", "Tuproqqal’a", "Urganch shahri"],
    "Qoraqalpog‘iston": ["Amudaryo", "Beruniy", "Chimboy", "Ellikqala", "Kegeyli", "Mo‘ynoq", "Nukus", "Qanliko‘l", "Qo‘ng‘irot", "Taxiatosh", "To‘rtko‘l", "Xo‘jayli"]
}


# -------------- DATABASE --------------
DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        child_name TEXT,
        parent_name TEXT,
        region TEXT,
        district TEXT,
        mahalla TEXT,
        age INTEGER,
        phone TEXT,
        registered_at TEXT
    )
    ''')
    conn.commit()
    conn.close()

def save_user(user_id, data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO users (user_id, child_name, parent_name, region, district, mahalla, age, phone, registered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        data.get("child_name"),
        data.get("parent_name"),
        data.get("region"),
        data.get("district"),
        data.get("mahalla"),
        int(data.get("age")) if data.get("age") else None,
        data.get("phone"),
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, child_name, parent_name, region, district, mahalla, age, phone, registered_at FROM users")
    res = c.fetchall()
    conn.close()
    return res

# -------------- ACTIVE TESTS MEMORY --------------
ACTIVE_TESTS = {}

# -------------- TEST PARSING FUNCTION --------------
def parse_test_txt(text):
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    questions = []
    for b in blocks:
        lines = [l.strip() for l in b.splitlines() if l.strip()]
        q_text = None
        opts = []
        ans = None
        for ln in lines:
            low = ln.lower()
            if low.startswith("savol") or (ln.endswith("?") and not q_text):
                parts = ln.split(":", 1)
                q_text = parts[1].strip() if len(parts) > 1 else ln.strip()
                continue
            if len(ln) >= 2 and ln[0].upper() in ("A", "B", "C", "D") and ln[1] in (")", "."):
                split_idx = ln.find(")")
                if split_idx == -1:
                    split_idx = 1
                opts.append(ln[split_idx+1:].strip())
                continue
            if low.startswith("javob"):
                parts = ln.split(":", 1)
                ans = parts[1].strip().upper() if len(parts) > 1 else ln.split()[-1].strip().upper()
        if q_text and len(opts) >= 2 and ans in ("A","B","C","D"):
            questions.append({"question": q_text, "options": opts[:4], "answer": ans})
    return questions

# -------------- COMMANDS AND HANDLERS --------------

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    except:
        chat_member = None

    if not chat_member or chat_member.status not in ["member", "administrator", "creator"]:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("✉️ Obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        keyboard.add(InlineKeyboardButton("✅ Obuna bo'ldim", callback_data="check_sub"))
        await message.answer("✉️ Iltimos, quyidagi kanalga obuna bo‘ling:", reply_markup=keyboard)
        await Registration.check_subscription.set()
        return

    if user_id in ADMIN_IDS:
        await message.answer("👋 Salom, Admin! Botga xush kelibsiz.", reply_markup=admin_menu)
    else:
        await message.answer("👋 Salom! 'KITOBXON KIDS' botiga xush kelibsiz!", reply_markup=menu)

@dp.callback_query_handler(lambda c: c.data == "check_sub", state=Registration.check_subscription)
async def check_subscription(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    except:
        chat_member = None

    if chat_member and chat_member.status in ["member", "administrator", "creator"]:
        await query.message.edit_text("✅ Obunangiz tasdiqlandi! Endi davom etishingiz mumkin.")
        await query.answer()
        await state.finish()
        if user_id in ADMIN_IDS:
            await bot.send_message(user_id, "👋 Salom, Admin! Botga xush kelibsiz.", reply_markup=admin_menu)
        else:
            await bot.send_message(user_id, "👋 Salom! 'KITOBXON KIDS' botiga xush kelibsiz!", reply_markup=menu)
    else:
        await query.answer("❗ Siz hali kanalga obuna bo‘lmadingiz.", show_alert=True)

# Ro'yxatdan o'tish bosqichlari (misol uchun faqat child_name):
@dp.message_handler(lambda message: message.text == "📝 Ro‘yxatdan o‘tish")
async def registration_start(message: types.Message):
    await message.answer("👶 Farzandingizning ismini kiriting:")
    await Registration.child_name.set()

@dp.message_handler(state=Registration.child_name)
async def registration_child_name(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.isalpha() or len(text) < 2:
        await message.answer("❗ Iltimos, faqat harflardan iborat to‘g‘ri ism kiriting.")
        return
    await state.update_data(child_name=text)
    await message.answer("🧑‍🦱 Ota/onangizning ismini kiriting:")
    await Registration.parent_name.set()

@dp.message_handler(state=Registration.parent_name)
async def registration_parent_name(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.replace(" ", "").isalpha() or len(text) < 2:
        await message.answer("❗ Iltimos, faqat harflardan iborat to‘g‘ri ism kiriting.")
        return
    await state.update_data(parent_name=text)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*[KeyboardButton(r) for r in REGIONS.keys()])
    await message.answer("🌍 Viloyatni tanlang:", reply_markup=keyboard)
    await Registration.region.set()

@dp.message_handler(state=Registration.region)
async def registration_region(message: types.Message, state: FSMContext):
    region = message.text.strip()
    if region not in REGIONS:
        await message.answer("❗ Iltimos, ro‘yxatdagi viloyatlardan birini tanlang.")
        return
    await state.update_data(region=region)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*[KeyboardButton(d) for d in REGIONS[region]])
    await message.answer("🏘 Tumanni tanlang:", reply_markup=keyboard)
    await Registration.district.set()

@dp.message_handler(state=Registration.district)
async def registration_district(message: types.Message, state: FSMContext):
    data = await state.get_data()
    region = data.get("region")
    district = message.text.strip()
    if region is None or district not in REGIONS.get(region, []):
        await message.answer("❗ Iltimos, ro‘yxatdagi tumandan birini tanlang.")
        return
    await state.update_data(district=district)
    await message.answer("🏡 Mahallani kiriting (matn sifatida):", reply_markup=ReplyKeyboardRemove())
    await Registration.mahalla.set()

@dp.message_handler(state=Registration.mahalla)
async def registration_mahalla(message: types.Message, state: FSMContext):
    mahalla = message.text.strip()
    if len(mahalla) < 3:
        await message.answer("❗ Mahalla nomi juda qisqa. Iltimos to‘liq kiriting.")
        return
    await state.update_data(mahalla=mahalla)
    await message.answer("🎂 Farzandingiz yoshini kiriting (raqam bilan):")
    await Registration.age.set()

@dp.message_handler(state=Registration.age)
async def registration_age(message: types.Message, state: FSMContext):
    age_text = message.text.strip()
    if not age_text.isdigit():
        await message.answer("❗ Iltimos, yoshni faqat raqam bilan kiriting.")
        return
    age = int(age_text)
    if age < 7 or age > 14:
        await message.answer("❗ Yosh 7 dan 14 gacha bo‘lishi kerak.")
        return
    await state.update_data(age=age)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("☎️ Telefon raqamni yuborish", request_contact=True))
    await message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=keyboard)
    await Registration.phone.set()

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Registration.phone)
async def registration_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else None
    if not phone:
        await message.answer("❗ Telefon raqam noto‘g‘ri yuborildi. Qaytadan yuboring.")
        return
    await state.update_data(phone=phone)
    data = await state.get_data()
    user_id = message.from_user.id
    save_user(user_id, data)
    await message.answer("✅ Ro‘yxatdan o‘tish yakunlandi!", reply_markup=menu)
    await state.finish()

# ---------------- Test boshlandi ----------------
@dp.message_handler(lambda message: message.text == "📖 Testni boshlash")
async def user_start_test(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT age FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        await message.answer("❗ Avval ro‘yxatdan o‘tishingiz kerak.", reply_markup=menu)
        return
    user_age = int(row[0])

    # Test fayllni o'qish (matn formatida)
    questions_7_10 = []
    questions_11_14 = []

    try:
        with open("test_7_10.txt", "r", encoding="utf-8") as f:
            questions_7_10 = parse_test_txt(f.read())
    except FileNotFoundError:
        pass

    try:
        with open("test_11_14.txt", "r", encoding="utf-8") as f:
            questions_11_14 = parse_test_txt(f.read())
    except FileNotFoundError:
        pass

    total_questions = 25
    count_7_10 = min(len(questions_7_10), total_questions // 2)
    count_11_14 = total_questions - count_7_10

    selected_7_10 = random.sample(questions_7_10, count_7_10) if questions_7_10 else []
    selected_11_14 = random.sample(questions_11_14, count_11_14) if questions_11_14 else []

    questions = selected_7_10 + selected_11_14
    random.shuffle(questions)

    if not questions:
        await message.answer("❗ Test savollari topilmadi. Iltimos admin bilan bog'laning.")
        return

    ACTIVE_TESTS[user_id] = {
        "questions": questions,
        "q_index": 0,
        "correct_count": 0,
        "answers": []
    }

    await message.answer(f"🧪 Test boshlandi! Jami savollar: {len(questions)}. Har bir savolga 60 soniya vaqt beriladi.", reply_markup=ReplyKeyboardRemove())
    await send_question_to_user(user_id)

async def send_question_to_user(user_id):
    test = ACTIVE_TESTS.get(user_id)
    if not test:
        return
    q_index = test["q_index"]
    questions = test["questions"]

    if q_index >= len(questions):
        await finish_test(user_id)
        return

    q = questions[q_index]
    question_text = f"<b>Savol {q_index + 1}:</b>\n{q['question']}\n\n"
    options = q["options"]
    options_text = "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)])
    await bot.send_message(user_id, question_text + options_text, parse_mode="HTML")

@dp.message_handler(lambda message: message.text in ["A", "B", "C", "D"])
async def answer_handler(message: types.Message):
    user_id = message.from_user.id
    test = ACTIVE_TESTS.get(user_id)
    if not test:
        await message.answer("❗ Sizda faol test mavjud emas. Testni boshlash uchun 📖 Testni boshlash tugmasini bosing.", reply_markup=menu)
        return

    q_index = test["q_index"]
    questions = test["questions"]

    if q_index >= len(questions):
        await message.answer("❗ Test allaqachon tugagan.")
        return

    user_answer = message.text.upper()
    correct_answer = questions[q_index]["answer"].upper()

    if user_answer == correct_answer:
        test["correct_count"] += 1
    test["answers"].append({
        "question": questions[q_index]["question"],
        "user_answer": user_answer,
        "correct_answer": correct_answer
    })

    test["q_index"] += 1

    if test["q_index"] < len(questions):
        await send_question_to_user(user_id)
    else:
        await finish_test(user_id)

async def finish_test(user_id):
    test = ACTIVE_TESTS.get(user_id)
    if not test:
        return
    total = len(test["questions"])
    correct = test["correct_count"]
    percent = round((correct / total) * 100, 2) if total > 0 else 0.0

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT child_name, parent_name, region, district, mahalla, age, phone FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()

    child_name = row[0] if row else "Noma'lum"
    parent_name = row[1] if row else "Noma'lum"
    region = row[2] if row else "Noma'lum"
    district = row[3] if row else "Noma'lum"
    mahalla = row[4] if row else "Noma'lum"
    age = row[5] if row else "Noma'lum"
    phone = row[6] if row else "Noma'lum"

    await bot.send_message(user_id,
        f"✅ Test yakunlandi!\n\n"
        f"👧 Farzand: {child_name}\n"
        f"👨‍👩‍👧 Ota/onasi: {parent_name}\n"
        f"🌍 Hudud: {region} - {district} - {mahalla}\n"
        f"🎂 Yosh: {age}\n"
        f"📞 Telefon: {phone}\n\n"
        f"✅ To‘g‘ri javoblar: {correct} / {total}\n"
        f"📊 Natija: {percent}%",
        reply_markup=menu
    )

    # Natijani adminlarga yuborish
    result_msg = (
        f"📝 Yangi test natijasi:\n\n"
        f"👧 Farzand: {child_name}\n"
        f"👨‍👩‍👧 Ota/onasi: {parent_name}\n"
        f"🌍 Hudud: {region} - {district} - {mahalla}\n"
        f"🎂 Yosh: {age}\n"
        f"📞 Telefon: {phone}\n\n"
        f"✅ To‘g‘ri javoblar: {correct} / {total}\n"
        f"📊 Natija: {percent}%\n\n"
        f"🕒 Vaqt: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    )
    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, result_msg)

    # Testni tozalash
    ACTIVE_TESTS.pop(user_id, None)

# -------------- Admin uchun test yuklash --------------

@dp.message_handler(lambda message: message.text == "🆕 Test yuklash", user_id=ADMIN_IDS)
async def admin_upload_test(message: types.Message):
    await message.answer("📤 Iltimos, test faylini matn (.txt) formatida yuboring.")

    # State boshqarish uchun qo'shimcha kerak bo'lsa, qo'shish mumkin

@dp.message_handler(content_types=types.ContentType.DOCUMENT, user_id=ADMIN_IDS)
async def admin_receive_test_file(message: types.Message):
    doc = message.document
    if not doc.file_name.endswith(".txt"):
        await message.answer("❗ Iltimos, faqat matn (.txt) formatidagi faylni yuboring.")
        return

    file_path = await doc.download()
    await message.answer(f"✅ Fayl qabul qilindi: {doc.file_name}")

    # Faylni saqlash va keyin test fayliga ko‘chirish
    if "7_10" in doc.file_name:
        os.rename(file_path.name, "test_7_10.txt")
    elif "11_14" in doc.file_name:
        os.rename(file_path.name, "test_11_14.txt")
    else:
        await message.answer("❗ Fayl nomida yosh guruh ko‘rsatilmagan (7_10 yoki 11_14).")
        return

    await message.answer("✅ Test fayli saqlandi va ishga tayyor.")

# -------------- Foydalanuvchilar ro‘yxati --------------

@dp.message_handler(lambda message: message.text == "📋 Foydalanuvchilar ro‘yxati", user_id=ADMIN_IDS)
async def admin_show_users(message: types.Message):
    users = get_all_users()
    if not users:
        await message.answer("👤 Hozircha foydalanuvchi yo‘q.")
        return
    text = "👤 Ro‘yxatdan o‘tgan foydalanuvchilar:\n\n"
    for u in users:
        text += f"ID: {u[0]}\nFarzand: {u[1]}\nOta/onasi: {u[2]}\nHudud: {u[3]}-{u[4]}-{u[5]}\nYosh: {u[6]}\nTelefon: {u[7]}\n\n"
    await message.answer(text)

# -------------- Asosiy menyuga qaytish --------------

@dp.message_handler(lambda message: message.text == "⬅ Asosiy menyu", user_id=ADMIN_IDS)
async def admin_back_to_main(message: types.Message):
    await message.answer("🔙 Asosiy menyuga qaytildi.", reply_markup=admin_menu)

@dp.message_handler(lambda message: message.text == "📚 Loyiha haqida")
async def about_project(message: types.Message):
    about_text = (
        "📚 Kitobxon Kids loyihasi haqida:\n\n"
        "1. 7-10 yosh bolalar uchun testlar mavjud.\n"
        "2. 11-14 yosh toifasi qo‘shildi.\n"
        "3. Foydalanuvchi ma’lumotlari xavfsiz saqlanadi.\n"
        "4. Fikr-mulohazalaringizni kutamiz.\n"
        "5. Loyihani doimiy yangilab boramiz.\n"
    )
    await message.answer(about_text)

@dp.message_handler(lambda message: message.text == "💬 Fikr va maslahatlar")
async def feedback_start(message: types.Message):
    await message.answer("💬 Fikringizni kiriting:")
    await Registration.feedback.set()

@dp.message_handler(state=Registration.feedback)
async def feedback_receive(message: types.Message, state: FSMContext):
    feedback = message.text.strip()
    if len(feedback) < 3:
        await message.answer("❗ Iltimos, aniq va qisqa fikr kiriting.")
        return
    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, f"💬 Fikr-mulohaza:\n\n{feedback}\n\nFoydalanuvchi: {message.from_user.full_name} (ID: {message.from_user.id})")
    await message.answer("✅ Fikringiz uchun rahmat!", reply_markup=menu)
    await state.finish()

# -------------- RUN BOT --------------

if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)


