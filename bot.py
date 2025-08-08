import logging
import random
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

TOKEN = "7570796885:AAHHfpXanemNYvW-wVT2Rv40U0xq-XjxSwk"
ADMIN_IDS = [6578706277, 7853664401]
CHANNEL_USERNAME = "@Kitobxon_Kids"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

DB_PATH = "users.db"
TEST_FILE_7_10 = "test_7_10.txt"
TEST_FILE_11_14 = "test_11_14.txt"
RESULTS_CSV = "results.csv"

# Viloyat - tumanlar dictionarysi (faqat misol uchun)
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

# FSM holatlar
class Registration(StatesGroup):
    child_name = State()
    parent_name = State()
    region = State()
    district = State()
    mahalla = State()
    age = State()
    phone = State()
    feedback = State()

class TakingTest(StatesGroup):
    answering = State()

# DB funksiyalar
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
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
    """)
    conn.commit()
    conn.close()

def save_user(user_id, data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    INSERT OR REPLACE INTO users (user_id, child_name, parent_name, region, district, mahalla, age, phone, registered_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
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

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return rows

# Test faylini o'qish va parsing
def parse_test_txt(filename):
    questions = []
    try:
        with open(filename, encoding="utf-8") as f:
            content = f.read()
        blocks = [b.strip() for b in content.split("\n\n") if b.strip()]
        for block in blocks:
            lines = block.split("\n")
            q_text = None
            opts = []
            ans = None
            for ln in lines:
                ln = ln.strip()
                if ln.lower().startswith("savol:"):
                    q_text = ln[6:].strip()
                elif len(ln) >= 2 and ln[0].upper() in "ABCD" and ln[1] in (")", "."):
                    opts.append(ln[2:].strip())
                elif ln.lower().startswith("javob:"):
                    ans = ln[6:].strip().upper()
            if q_text and len(opts) == 4 and ans in ("A", "B", "C", "D"):
                questions.append({"question": q_text, "options": opts, "answer": ans})
    except Exception as e:
        logging.error(f"Test faylini o'qishda xatolik: {e}")
    return questions

# GLOBAL for active tests
ACTIVE_TESTS = {}

# Start buyrug'i va obuna tekshirish
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if chat_member.status not in ["member", "administrator", "creator"]:
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(types.InlineKeyboardButton(text="✉️ Obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
            keyboard.add(types.InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="check_sub"))
            await message.answer("✉️ Iltimos, kanalga obuna bo'ling:", reply_markup=keyboard)
            await state.finish()
            return
    except:
        await message.answer("Kanalga obuna bo'lishni tekshirishda xatolik yuz berdi, iltimos, admin bilan bog'laning.")
        return

    if user_id in ADMIN_IDS:
        await message.answer("👋 Salom, Admin! Botga xush kelibsiz.")
    else:
        user = get_user(user_id)
        if user:
            await message.answer(f"👋 Salom, {user[1]}! Testni boshlash uchun '📖 Testni boshlash' tugmasini bosing.")
        else:
            await message.answer("👋 Salom! Iltimos, ro'yxatdan o'tish uchun ismingizni kiriting.")
            await Registration.child_name.set()

# Obuna tasdiqlash (inline tugma)
@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(call: types.CallbackQuery):
    user_id = call.from_user.id
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if chat_member.status in ["member", "administrator", "creator"]:
            await call.message.edit_text("✅ Obunangiz tasdiqlandi! Endi davom etishingiz mumkin.")
            await bot.send_message(user_id, "Xush kelibsiz!")
        else:
            await call.answer("Siz hali kanalga obuna bo‘lmagansiz.", show_alert=True)
    except Exception:
        await call.answer("Kanalga obuna bo'lishni tekshirishda xatolik yuz berdi.", show_alert=True)

# Ro'yxatdan o'tish flow
@dp.message_handler(state=Registration.child_name)
async def reg_child_name(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.isalpha() or len(text) < 2:
        await message.reply("❗ Iltimos, to‘g‘ri ism kiriting (faqat harflar).")
        return
    await state.update_data(child_name=text)
    await message.answer("🧑‍🦱 Ota/onangiz ismini kiriting:")
    await Registration.parent_name.set()

@dp.message_handler(state=Registration.parent_name)
async def reg_parent_name(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.replace(" ", "").isalpha() or len(text) < 2:
        await message.reply("❗ Iltimos, to‘g‘ri ism kiriting (faqat harflar).")
        return
    await state.update_data(parent_name=text)
    regions_buttons = [[types.KeyboardButton(r)] for r in REGIONS.keys()]
    keyboard = types.ReplyKeyboardMarkup(keyboard=regions_buttons, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("🌍 Viloyatni tanlang:", reply_markup=keyboard)
    await Registration.region.set()

@dp.message_handler(state=Registration.region)
async def reg_region(message: types.Message, state: FSMContext):
    region = message.text.strip()
    if region not in REGIONS:
        await message.reply("❗ Iltimos, ro‘yxatdan viloyatni tanlang.")
        return
    await state.update_data(region=region)
    districts_buttons = [[types.KeyboardButton(d)] for d in REGIONS[region]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=districts_buttons, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("🏘 Tumanni tanlang:", reply_markup=keyboard)
    await Registration.district.set()

@dp.message_handler(state=Registration.district)
async def reg_district(message: types.Message, state: FSMContext):
    data = await state.get_data()
    region = data.get("region")
    district = message.text.strip()
    if region is None or district not in REGIONS.get(region, []):
        await message.reply("❗ Iltimos, ro‘yxatdan tumanni tanlang.")
        return
    await state.update_data(district=district)
    await message.answer("🏡 Mahallani kiriting (matn):", reply_markup=types.ReplyKeyboardRemove())
    await Registration.mahalla.set()

@dp.message_handler(state=Registration.mahalla)
async def reg_mahalla(message: types.Message, state: FSMContext):
    mahalla = message.text.strip()
    if len(mahalla) < 3:
        await message.reply("❗ Mahalla nomini to‘liq kiriting.")
        return
    await state.update_data(mahalla=mahalla)
    await message.answer("🎂 Farzandingiz yoshini kiriting (raqam bilan):")
    await Registration.age.set()

@dp.message_handler(state=Registration.age)
async def reg_age(message: types.Message, state: FSMContext):
    age_text = message.text.strip()
    if not age_text.isdigit():
        await message.reply("❗ Iltimos, yoshni raqam bilan kiriting.")
        return
    age = int(age_text)
    if age < 7 or age > 14:
        await message.reply("❗ Yosh 7 dan 14 gacha bo‘lishi kerak.")
        return
    await state.update_data(age=age)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("☎️ Telefon raqamni yuborish", request_contact=True))
    await message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=keyboard)
    await Registration.phone.set()

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Registration.phone)
async def reg_phone_contact(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else None
    if not phone:
        await message.reply("❗ Telefon raqam noto‘g‘ri yuborildi. Qaytadan yuboring.")
        return
    await state.update_data(phone=phone)
    data = await state.get_data()
    save_user(message.from_user.id, data)
    await message.answer("✅ Ro‘yxatdan o‘tish yakunlandi!", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("📖 Testni boshlash"))
    await state.finish()

# Test faylini yuklash (admin)
@dp.message_handler(commands=["uploadtest"])
async def admin_upload_test(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❗ Siz admin emassiz.")
        return
    await message.answer("Iltimos, test faylini .txt formatida yuboring.")

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_doc(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    doc = message.document
    if not doc.file_name.endswith(".txt"):
        await message.answer("Faqat .txt formatdagi fayl yuboring.")
        return
    await doc.download(destination_file=doc.file_name)
    await message.answer(f"Fayl '{doc.file_name}' muvaffaqiyatli yuklandi.")

# Testni boshlash
@dp.message_handler(lambda message: message.text == "📖 Testni boshlash")
async def start_test(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("❗ Iltimos, avval ro'yxatdan o'ting.")
        return
    age = user[6]
    if age is None:
        await message.answer("❗ Yosh ma'lum emas. Iltimos, admin bilan bog'laning.")
        return

    # Test faylini tanlash
    if 7 <= age <= 10:
        filename = TEST_FILE_7_10
    elif 11 <= age <= 14:
        filename = TEST_FILE_11_14
    else:
        await message.answer("❗ Yoshga mos test topilmadi.")
        return

    questions = parse_test_txt(filename)
    if not questions:
        await message.answer("❗ Test savollari topilmadi. Iltimos, admin bilan bog‘laning.")
        return

    sample = random.sample(questions, min(10, len(questions)))
    await state.update_data(test_questions=sample, current=0, correct=0)
    await TakingTest.answering.set()
    await send_question(message.chat.id, state)

async def send_question(chat_id, state):
    data = await state.get_data()
    current = data.get("current", 0)
    questions = data.get("test_questions", [])
    if current >= len(questions):
        correct = data.get("correct", 0)
        await bot.send_message(chat_id, f"✅ Test yakunlandi! To‘g‘ri javoblar: {correct} / {len(questions)}")
        await state.finish()
        return
    q = questions[current]
    text = f"🔹 Savol {current+1}:\n{q['question']}\n\n"
    for i, opt in enumerate(q["options"]):
        text += f"{chr(65+i)}) {opt}\n"
    text += "\nIltimos, javob sifatida A, B, C yoki D yuboring."
    await bot.send_message(chat_id, text)

@dp.message_handler(state=TakingTest.answering)
async def process_answer(message: types.Message, state: FSMContext):
    user_ans = message.text.strip().upper()
    if user_ans not in ("A", "B", "C", "D"):
        await message.reply("❗ Javob sifatida faqat A, B, C yoki D harflarini yuboring.")
        return
    data = await state.get_data()
    current = data.get("current", 0)
    correct = data.get("correct", 0)
    questions = data.get("test_questions", [])
    if current >= len(questions):
        await message.answer("Test allaqachon tugadi.")
        await state.finish()
        return
    correct_ans = questions[current]["answer"].upper()
    if user_ans == correct_ans:
        correct += 1
    current += 1
    await state.update_data(current=current, correct=correct)
    await send_question(message.chat.id, state)

if __name__ == "__main__":
    init_db()
    executor.start_polling(dp, skip_updates=True)
