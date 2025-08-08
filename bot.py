# main.py
import asyncio
import logging
import os
import random
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    ContentType
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ---------------- Configuration ----------------
TOKEN = "7570796885:AAHHfpXanemNYvW-wVT2Rv40U0xq-XjxSwk"
ADMIN_IDS = [6578706277, 7853664401]
CHANNEL_USERNAME = "@Kitobxon_Kids"

# ---------------- Logging & bot/dispatcher ----------------
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ---------------- Menus ----------------
menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📖 Testni boshlash")],
    [KeyboardButton(text="📚 Loyiha haqida"), KeyboardButton(text="💬 Fikr va maslahatlar")]
], resize_keyboard=True)

admin_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🆕 Test yuklash"), KeyboardButton(text="🗑 Testni o‘chirish")],
    [KeyboardButton(text="📋 Foydalanuvchilar ro‘yxati")],
    [KeyboardButton(text="⬅ Asosiy menyu")]
], resize_keyboard=True)

# ---------------- Regions ----------------
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

# ---------------- FSM States ----------------
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

# ---------------- Files & DB ----------------
DATA_DIR = Path("data")
if DATA_DIR.exists() and not DATA_DIR.is_dir():
    DATA_DIR.unlink()
DATA_DIR.mkdir(exist_ok=True)

TEST_FILE_7_10 = DATA_DIR / "test_7_10.txt"
TEST_FILE_11_14 = DATA_DIR / "test_11_14.txt"

DB_PATH = Path("users.db")
RESULTS_CSV = Path("results.csv")
if not RESULTS_CSV.exists():
    RESULTS_CSV.write_text("timestamp,user_id,child,parent,region,district,mahalla,age,phone,correct,total,percent\n", encoding="utf-8")

# ---------------- SQLite helpers ----------------
def init_db() -> None:
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

def save_user(user_id: int, data: Dict[str, Any]) -> None:
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
        int(data.get("age")) if data.get("age") is not None else None,
        data.get("phone"),
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

def get_all_users() -> List[tuple]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, child_name, parent_name, region, district, mahalla, age, phone, registered_at FROM users")
    res = c.fetchall()
    conn.close()
    return res

# ---------------- Test parsing ----------------
def parse_test_txt(text: str) -> List[Dict[str, Any]]:
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    questions: List[Dict[str, Any]] = []
    for b in blocks:
        lines = [l.strip() for l in b.splitlines() if l.strip()]
        q_text = None
        opts: List[str] = []
        ans = None
        for ln in lines:
            low = ln.lower()
            if low.startswith("savol") or (ln.endswith("?") and q_text is None):
                if q_text is None:
                    parts = ln.split(":", 1)
                    q_text = parts[1].strip() if len(parts) > 1 else ln.strip()
                    continue
            if len(ln) >= 2 and ln[0].upper() in ("A","B","C","D") and ln[1] in (")", "."):
                split_idx = ln.find(")")
                if split_idx == -1:
                    split_idx = 1
                opt_text = ln[split_idx+1:].strip()
                opts.append(opt_text)
                continue
            if low.startswith("javob"):
                parts = ln.split(":", 1)
                if len(parts) >= 2:
                    ans = parts[1].strip().upper()
                else:
                    ans = ln.split()[-1].strip().upper()
        if q_text and len(opts) >= 2 and ans in ("A","B","C","D"):
            questions.append({"question": q_text, "options": opts[:4], "answer": ans})
    return questions

# ---------------- Active tests memory ----------------
ACTIVE_TESTS: Dict[int, Dict[str, Any]] = {}

# ---------------- /start and subscription check ----------------
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    except Exception:
        chat_member = None

    if chat_member and chat_member.status not in ["member", "administrator", "creator"]:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="check_sub")]
        ])
        await message.answer("✉️ Iltimos, quyidagi kanalga obuna bo‘ling:", reply_markup=keyboard)
        await state.set_state(Registration.check_subscription)
        return

    if user_id in ADMIN_IDS:
        await message.answer("👋 Salom, Admin! Botga xush kelibsiz.", reply_markup=admin_menu)
    else:
        await message.answer("👋 Salom! 'KITOBXON KIDS' botiga xush kelibsiz!", reply_markup=menu)

@dp.callback_query(F.data == "check_sub")
async def check_subscription(query, state: FSMContext):
    user_id = query.from_user.id
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    except Exception:
        chat_member = None

    if chat_member and chat_member.status in ["member", "administrator", "creator"]:
        await query.message.edit_text("✅ Obunangiz tasdiqlandi! Endi davom etishingiz mumkin.")
        await query.answer()
        await state.clear()
        if user_id in ADMIN_IDS:
            await bot.send_message(user_id, "👋 Salom, Admin! Botga xush kelibsiz.", reply_markup=admin_menu)
        else:
            await bot.send_message(user_id, "👋 Salom! 'KITOBXON KIDS' botiga xush kelibsiz!", reply_markup=menu)
    else:
        await query.answer("❗ Siz hali kanalga obuna bo‘lmadingiz.", show_alert=True)

# ---------------- Registration flow ----------------
@dp.message(F.text == "📝 Ro‘yxatdan o‘tish")
async def registration_start(message: Message, state: FSMContext):
    await message.answer("👶 Farzandingizning ismini kiriting:")
    await state.set_state(Registration.child_name)

@dp.message(Registration.child_name)
async def registration_child_name(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isalpha() or len(text) < 2:
        await message.answer("❗ Iltimos, faqat harflardan iborat to‘g‘ri ism kiriting.")
        return
    await state.update_data(child_name=text)
    await message.answer("🧑‍🦱 Ota/onangizning ismini kiriting:")
    await state.set_state(Registration.parent_name)

@dp.message(Registration.parent_name)
async def registration_parent_name(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.replace(" ", "").isalpha() or len(text) < 2:
        await message.answer("❗ Iltimos, faqat harflardan iborat to‘g‘ri ism kiriting.")
        return
    await state.update_data(parent_name=text)
    regions_buttons = [[KeyboardButton(text=r)] for r in REGIONS.keys()]
    keyboard = ReplyKeyboardMarkup(keyboard=regions_buttons, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("🌍 Viloyatni tanlang:", reply_markup=keyboard)
    await state.set_state(Registration.region)

@dp.message(Registration.region)
async def registration_region(message: Message, state: FSMContext):
    region = message.text.strip()
    if region not in REGIONS:
        await message.answer("❗ Iltimos, ro‘yxatdagi viloyatlardan birini tanlang.")
        return
    await state.update_data(region=region)
    districts_buttons = [[KeyboardButton(text=d)] for d in REGIONS[region]]
    keyboard = ReplyKeyboardMarkup(keyboard=districts_buttons, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("🏘 Tumanni tanlang:", reply_markup=keyboard)
    await state.set_state(Registration.district)

@dp.message(Registration.district)
async def registration_district(message: Message, state: FSMContext):
    data = await state.get_data()
    region = data.get("region")
    district = message.text.strip()
    if region is None or district not in REGIONS.get(region, []):
        await message.answer("❗ Iltimos, ro‘yxatdagi tumandan birini tanlang.")
        return
    await state.update_data(district=district)
    await message.answer("🏡 Mahallani kiriting (matn sifatida):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.mahalla)

@dp.message(Registration.mahalla)
async def registration_mahalla(message: Message, state: FSMContext):
    mahalla = message.text.strip()
    if len(mahalla) < 3:
        await message.answer("❗ Mahalla nomi juda qisqa. Iltimos to‘liq kiriting.")
        return
    await state.update_data(mahalla=mahalla)
    await message.answer("🎂 Farzandingiz yoshini kiriting (raqam bilan):")
    await state.set_state(Registration.age)

@dp.message(Registration.age)
async def registration_age(message: Message, state: FSMContext):
    age_text = message.text.strip()
    if not age_text.isdigit():
        await message.answer("❗ Iltimos, yoshni faqat raqam bilan kiriting.")
        return
    age = int(age_text)
    if age < 7 or age > 14:
        await message.answer("❗ Yosh 7 dan 14 gacha bo‘lishi kerak.")
        return
    await state.update_data(age=age)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="☎️ Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=keyboard)
    await state.set_state(Registration.phone)

@dp.message(Registration.phone, F.content_type == ContentType.CONTACT)
async def registration_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else None
    if not phone:
        await message.answer("❗ Telefon raqam noto‘g‘ri yuborildi. Qaytadan yuboring.")
        return
    await state.update_data(phone=phone)
    data = await state.get_data()
    user_id = message.from_user.id
    save_user(user_id, data)
    await message.answer("✅ Ro‘yxatdan o‘tish yakunlandi!", reply_markup=menu)
    await state.clear()

# ---------------- Test start & flow ----------------
@dp.message(F.text == "📖 Testni boshlash")
async def user_start_test(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # Foydalanuvchini yoshini bazadan olish
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT age FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        await message.answer("❗ Avval ro‘yxatdan o‘tishingiz kerak.", reply_markup=menu)
        return
    user_age = int(row[0])

    # Savollarni o'qish
    questions_7_10 = []
    questions_11_14 = []

    if TEST_FILE_7_10.exists():
        text_7_10 = TEST_FILE_7_10.read_text(encoding="utf-8")
        questions_7_10 = parse_test_txt(text_7_10)

    if TEST_FILE_11_14.exists():
        text_11_14 = TEST_FILE_11_14.read_text(encoding="utf-8")
        questions_11_14 = parse_test_txt(text_11_14)

    total_questions = 25
    # 7-10 yosh uchun savol soni (agar savollar yetarli bo'lsa)
    count_7_10 = min(len(questions_7_10), total_questions // 2)
    count_11_14 = total_questions - count_7_10

    selected_7_10 = random.sample(questions_7_10, count_7_10) if questions_7_10 else []
    selected_11_14 = random.sample(questions_11_14, count_11_14) if questions_11_14 else []

    questions = selected_7_10 + selected_11_14
    random.shuffle(questions)

    if not questions:
        await message.answer("❗ Test savollari topilmadi. Iltimos admin bilan bog'laning.")
        return

    # Testni xotirada saqlash
    ACTIVE_TESTS[user_id] = {
        "questions": questions,
        "q_index": 0,
        "correct_count": 0,
        "answers": []
    }

    await message.answer(f"🧪 Test boshlandi! Jami savollar: {len(questions)}. Har bir savolga 60 soniya vaqt beriladi.", reply_markup=ReplyKeyboardRemove())
    await send_question_to_user(user_id)

async def send_question_to_user(user_id: int):
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
    await bot.send_message(user_id, question_text + options_text)

@dp.message(F.text.in_({"A", "B", "C", "D"}))
async def answer_handler(message: Message):
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
    test["answers"].append({"question": questions[q_index]["question"], "user_answer": user_answer, "correct_answer": correct_answer})

    test["q_index"] += 1

    if test["q_index"] < len(questions):
        await send_question_to_user(user_id)
    else:
        await finish_test(user_id)

async def finish_test(user_id: int):
    test = ACTIVE_TESTS.get(user_id)
    if not test:
        return
    total = len(test["questions"])
    correct = test["correct_count"]
    percent = round((correct / total) * 100, 2) if total > 0 else 0.0

    # Foydalanuvchi ma'lumotlarini olish
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

    # Natijani CSV faylga yozish
    with open(RESULTS_CSV, "a", encoding="utf-8") as f:
        f.write(f"{datetime.utcnow().isoformat()},{user_id},{child_name},{parent_name},{region},{district},{mahalla},{age},{phone},{correct},{total},{percent}\n")

    # Testni xotiradan o'chirish
    ACTIVE_TESTS.pop(user_id, None)

# ---------------- Feedback ----------------
@dp.message(F.text == "💬 Fikr va maslahatlar")
async def feedback_start(message: Message, state: FSMContext):
    await message.answer("Fikringizni yozing:")
    await state.set_state(Registration.feedback)

@dp.message(Registration.feedback)
async def feedback_process(message: Message, state: FSMContext):
    text = message.text.strip()
    user_id = message.from_user.id
    if len(text) < 5:
        await message.answer("❗ Iltimos, fikringizni aniqroq yozing.")
        return

    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, f"Fikr-mulohaza ({message.from_user.full_name}):\n\n{text}")

    await message.answer("✅ Fikringiz uchun rahmat!", reply_markup=menu)
    await state.clear()

# ---------------- Admin commands ----------------
@dp.message(Command("users"))
async def list_users(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❗ Siz admin emassiz.")
        return
    users = get_all_users()
    if not users:
        await message.answer("Foydalanuvchilar topilmadi.")
        return
    text = "Foydalanuvchilar ro‘yxati:\n"
    for u in users:
        text += f"{u[1]} ({u[0]}) — {u[5]}, yosh: {u[6]}\n"
    await message.answer(text)

# ---------------- Helper ----------------
@dp.message(F.text == "📚 Loyiha haqida")
async def about_project(message: Message):
    text = (
        "<b>Kitobxon Kids loyihasi haqida:</b>\n\n"
        "Bu loyiha 7-14 yoshdagi bolalar uchun mo‘ljallangan o‘quv platformasi.\n"
        "Foydalanuvchilar ro‘yxatdan o‘tib, testlarni yechishlari mumkin.\n"
        "Yosh toifasiga qarab testlar taqdim etiladi.\n\n"
        "Loyihaning maqsadi - bolalarning bilim darajasini oshirish va ularni qo‘llab-quvvatlash."
    )
    await message.answer(text)

# ---------------- Entry point ----------------
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
