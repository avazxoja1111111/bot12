import logging
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# --------- CONFIG ---------
TOKEN = "7570796885:AAHHfpXanemNYvW-wVT2Rv40U0xq-XjxSwk"
ADMIN_IDS = [6578706277, 7853664401]
CHANNEL_USERNAME = "@Kitobxon_Kids"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --------- STATE GROUPS ---------
class Registration(StatesGroup):
    check_subscription = State()
    child_name = State()
    parent_name = State()
    region = State()
    district = State()
    mahalla = State()
    age = State()
    phone = State()

class TakingTest(StatesGroup):
    answering = State()

# --------- MENUS ---------
menu = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("📖 Testni boshlash")
).add(
    KeyboardButton("📝 Ro‘yxatdan o‘tish")
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

# --------- REGIONS DATA ---------
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

# --------- DATABASE ---------
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

def get_user_age(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT age FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return int(row[0]) if row else None

# --------- ACTIVE TESTS MEMORY ---------
ACTIVE_TESTS = {}

# --------- TEST PARSING FUNCTION ---------
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

# --------- COMMANDS AND HANDLERS ---------

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    except Exception:
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
    except Exception:
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

# Ro'yxatdan o'tish bosqichlari:
@dp.message_handler(lambda message: message.text == "📝 Ro‘yxatdan o‘tish")
async def registration_start(message: types.Message):
    await message.answer("👶 Farzandingizning ismini kiriting:")
    await Registration.child_name.set()

@dp.message_handler(state=Registration.child_name)
async def registration_child_name(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.replace(" ", "").isalpha() or len(text) < 2:
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
    user_age = get_user_age(user_id)
    if not user_age:
        await message.answer("❗ Avval ro‘yxatdan o‘tishingiz kerak.", reply_markup=menu)
        return

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

    if 7 <= user_age <= 10:
        questions = questions_7_10
    else:
        questions = questions_11_14

    if not questions:
        await message.answer("❗ Testlar mavjud emas. Iltimos, administrator bilan bog‘laning.")
        return

    ACTIVE_TESTS[user_id] = {
        "questions": questions,
        "current_index": 0,
        "score": 0
    }

    question = questions[0]
    options = question["options"]
    keyboard = InlineKeyboardMarkup(row_width=2)
    option_buttons = []
    for i, opt in enumerate(options):
        btn = InlineKeyboardButton(f"{chr(65 + i)}) {opt}", callback_data=f"answer_{chr(65 + i)}")
        option_buttons.append(btn)
    keyboard.add(*option_buttons)

    await message.answer(f"1-savol:\n{question['question']}", reply_markup=keyboard)
    await TakingTest.answering.set()

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("answer_"), state=TakingTest.answering)
async def answer_question(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    user_test = ACTIVE_TESTS.get(user_id)
    if not user_test:
        await query.answer("❗ Sizda faol test topilmadi. Iltimos, testni qayta boshlang.")
        await state.finish()
        return

    selected = query.data.split("_")[1]
    current_index = user_test["current_index"]
    question = user_test["questions"][current_index]

    if selected == question["answer"]:
        user_test["score"] += 1

    user_test["current_index"] += 1

    if user_test["current_index"] < len(user_test["questions"]):
        next_q = user_test["questions"][user_test["current_index"]]
        options = next_q["options"]
        keyboard = InlineKeyboardMarkup(row_width=2)
        option_buttons = []
        for i, opt in enumerate(options):
            btn = InlineKeyboardButton(f"{chr(65 + i)}) {opt}", callback_data=f"answer_{chr(65 + i)}")
            option_buttons.append(btn)
        keyboard.add(*option_buttons)

        await query.message.edit_text(f"{user_test['current_index'] + 1}-savol:\n{next_q['question']}", reply_markup=keyboard)
        await query.answer()
    else:
        score = user_test["score"]
        total = len(user_test["questions"])
        await query.message.edit_text(f"Test yakunlandi!\nSizning natijangiz: {score} / {total}")
        await query.answer()
        ACTIVE_TESTS.pop(user_id, None)
        await state.finish()

# ---------- BOTNI ISHGA TAYYORLASH ----------
if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)
