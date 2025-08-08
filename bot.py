# main.py
import asyncio
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove, Message, ContentType
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# 🔑 Token va Admin ID-lar (sen bergan)
TOKEN = "7570796885:AAHHfpXanemNYvW-wVT2Rv40U0xq-XjxSwk"
ADMIN_IDS = [6578706277, 7853664401]
CHANNEL_USERNAME = "@Kitobxon_Kids"

# 🛠 Logging
logging.basicConfig(level=logging.INFO)

# 🤖 Bot va Dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# 📌 Asosiy menyu (ro'yxatdan o'tgan foydalanuvchilar uchun)
menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📖 Testni boshlash")],
    [KeyboardButton(text="📚 Loyiha haqida"), KeyboardButton(text="💬 Fikr va maslahatlar")]
], resize_keyboard=True)

# 📌 Admin menyu
admin_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🆕 Test yuklash"), KeyboardButton(text="🗑 Testni o‘chirish")],
    [KeyboardButton(text="📋 Foydalanuvchilar ro‘yxati")],
    [KeyboardButton(text="⬅ Asosiy menyu")]
], resize_keyboard=True)

# 📌 Ro‘yxatdagi viloyat-tumanlar (sen bergan to'liq ro'yxat)
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

# 📌 FSM holatlari
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

# 📂 FAYL VA DB SOZLAMALARI
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
ACTIVE_TEST_PATH = DATA_DIR / "active_test.txt"
DB_PATH = Path("users.db")
RESULTS_CSV = Path("results.csv")
if not RESULTS_CSV.exists():
    RESULTS_CSV.write_text("timestamp,user_id,child,parent,region,district,mahalla,age,phone,correct,total,percent\n", encoding="utf-8")

# ======== SQLite yordamchi funksiyalar =========
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
        age TEXT,
        phone TEXT,
        registered_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_user(user_id: int, data: Dict[str, Any]):
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
        str(data.get("age")),
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

# ======== TEST PARSER (.txt) =========
def parse_test_txt(text: str) -> List[Dict[str, Any]]:
    """
    Matn formatini quyidagicha kutadi (savollar bo'sh qatorda ajratilgan):
    Savol 1: ...?
    A) ...
    B) ...
    C) ...
    D) ...
    Javob: B

    Natija: List of dicts: {"question": str, "options": [..4..], "answer": "A"}
    """
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    questions = []
    for b in blocks:
        lines = [l.strip() for l in b.splitlines() if l.strip()]
        q_text = None
        opts = []
        ans = None
        for ln in lines:
            if ln.lower().startswith("savol") or ln.endswith("?") or (ln and not ln[0].upper() in ("A","B","C","D") and not ln.lower().startswith("javob")):
                # attempt to detect question line (very permissive)
                if q_text is None:
                    q_text = ln
                    continue
            if len(ln) >= 2 and ln[0].upper() in ("A","B","C","D") and ln[1] in (")", "."):
                # option
                # split at first space after ")"
                split_idx = ln.find(")")
                if split_idx == -1:
                    split_idx = 1
                opt_text = ln[split_idx+1:].strip()
                opts.append(opt_text)
                continue
            if ln.lower().startswith("javob"):
                # Javob: B
                parts = ln.split(":")
                if len(parts) >= 2:
                    ans = parts[1].strip().upper()
                else:
                    # try last token
                    ans = ln.split()[-1].strip().upper()
        # if insufficient options but lines contain labeled A/B etc maybe earlier parsing failed; fallback:
        if q_text and len(opts) >= 2 and ans in ("A","B","C","D"):
            questions.append({"question": q_text, "options": opts[:4], "answer": ans})
    return questions

# ======== ACTIVE TESTS IN MEMORY =========
# user_id -> {questions, q_index, correct_count, answers, timer_task}
ACTIVE_TESTS: Dict[int, Dict[str, Any]] = {}

# ======== /start va obuna tekshiruvi =========
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    except Exception:
        # agar kanalga ulanishda muammo bo'lsa, tasdiqlashni o'tkazib yuboramiz
        chat_member = None
    if chat_member and chat_member.status not in ["member", "administrator", "creator"]:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="check_sub")]
        ])
        await message.answer("✉️ Iltimos, quyidagi kanalga obuna bo‘ling:", reply_markup=keyboard)
        await state.set_state(Registration.check_subscription)
    else:
        # Agar admin bo'lsa, admin menyuni, aks holda oddiy asosiy menyuni ko'rsat
        if user_id in ADMIN_IDS:
            await message.answer("👋 Salom, Admin! Botga xush kelibsiz.", reply_markup=admin_menu)
        else:
            await message.answer("👋 Salom! 'KITOBXON KIDS' botiga xush kelibsiz!", reply_markup=menu)

@dp.callback_query(lambda c: c.data == "check_sub")
async def cb_check_sub(q: types.CallbackQuery, state: FSMContext):
    user_id = q.from_user.id
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    except Exception:
        chat_member = None
    if chat_member and chat_member.status in ["member", "administrator", "creator"]:
        if user_id in ADMIN_IDS:
            await bot.send_message(user_id, "👋 Salom, Admin! Botga xush kelibsiz.", reply_markup=admin_menu)
        else:
            await bot.send_message(user_id, "👋 Salom! 'KITOBXON KIDS' botiga xush kelibsiz!", reply_markup=menu)
        await state.clear()
    else:
        await q.answer("❌ Hali ham obuna emassiz!", show_alert=True)

# ======== RO'YXATDAN O'TISH =========
@dp.message(lambda message: message.text == "📋 Ro‘yxatdan o‘tish")
async def register_start(message: Message, state: FSMContext):
    await message.answer("👶 Farzandingiz ism familiyasini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.child_name)

@dp.message(Registration.child_name)
async def register_child_name(message: Message, state: FSMContext):
    # saqlash
    await state.update_data(child_name=message.text.strip())
    await message.answer("👨‍👩‍👦 Ota-onaning ism familiyasini kiriting:")
    await state.set_state(Registration.parent_name)

@dp.message(Registration.parent_name)
async def register_parent_name(message: Message, state: FSMContext):
    await state.update_data(parent_name=message.text.strip())
    # ko'rsat viloyat tugmalari
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for region in REGIONS.keys():
        kb.add(KeyboardButton(text=region))
    await message.answer("🌍 Viloyatni tanlang:", reply_markup=kb)
    await state.set_state(Registration.region)

@dp.message(Registration.region)
async def register_region(message: Message, state: FSMContext):
    region = message.text.strip()
    if region not in REGIONS:
        await message.answer("Iltimos, ro'yxatdan birini tanlang.")
        return
    await state.update_data(region=region)
    districts = REGIONS[region]
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for d in districts:
        kb.add(KeyboardButton(text=d))
    await message.answer("🏙 Tumaningizni tanlang:", reply_markup=kb)
    await state.set_state(Registration.district)

@dp.message(Registration.district)
async def register_district(message: Message, state: FSMContext):
    await state.update_data(district=message.text.strip())
    await message.answer("🏘 Mahallangiz nomini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.mahalla)

@dp.message(Registration.mahalla)
async def register_mahalla(message: Message, state: FSMContext):
    await state.update_data(mahalla=message.text.strip())
    # yosh tanlash (7-14)
    yosh_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    yosh_kb.row(KeyboardButton("7"), KeyboardButton("8"), KeyboardButton("9"), KeyboardButton("10"))
    yosh_kb.row(KeyboardButton("11"), KeyboardButton("12"), KeyboardButton("13"), KeyboardButton("14"))
    await message.answer("📅 Yoshni tanlang (raqam bilan):", reply_markup=yosh_kb)
    await state.set_state(Registration.age)

@dp.message(Registration.age)
async def register_age(message: Message, state: FSMContext):
    txt = message.text.strip()
    if not txt.isdigit() or not (7 <= int(txt) <= 14):
        await message.answer("Iltimos 7 dan 14 gacha bo'lgan yoshni tanlang.")
        return
    await state.update_data(age=int(txt))
    # request contact
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))
    await message.answer("📞 Telefon raqamingizni yuboring (tugma orqali):", reply_markup=kb)
    await state.set_state(Registration.phone)

@dp.message(Registration.phone, content_types=types.ContentType.ANY)
async def register_phone(message: Message, state: FSMContext):
    # foydalanuvchi contact yuborishi kerak
    if not message.contact:
        await message.answer("📞 Iltimos, tugma orqali telefon raqam yuboring.")
        return
    user_data = await state.get_data()
    phone_number = message.contact.phone_number
    user_data['phone'] = phone_number
    # saqlash DBga
    save_user(message.from_user.id, user_data)
    # yuborish adminlarga
    reg_info = (
        f"📋 Yangi ro‘yxatdan o‘tish:\n"
        f"👶 Farzand: {user_data.get('child_name')}\n"
        f"👨‍👩‍👦 Ota-ona: {user_data.get('parent_name')}\n"
        f"🌍 Viloyat: {user_data.get('region')}\n"
        f"🏙 Tuman: {user_data.get('district')}\n"
        f"🏘 Mahalla: {user_data.get('mahalla')}\n"
        f"📅 Yosh: {user_data.get('age')}\n"
        f"📞 Telefon: {phone_number}\n"
        f"Telegram: @{message.from_user.username or 'no_username'} ({message.from_user.id})"
    )
    for admin in ADMIN_IDS:
        try:
            await bot.send_message(admin, reg_info)
        except Exception:
            pass
    # tasdiq va menyu
    await message.answer("✅ Ro‘yxatdan o‘tish muvaffaqiyatli yakunlandi!", reply_markup=menu)
    await state.clear()

# ======== FIKR VA LOYIHA HAQIDA =========
@dp.message(lambda message: message.text == "💬 Fikr va maslahatlar")
async def feedback_prompt(message: Message, state: FSMContext):
    await message.answer("✍️ Fikringizni yozing:")
    await state.set_state(Registration.feedback)

@dp.message(Registration.feedback)
async def save_feedback(message: Message, state: FSMContext):
    feedback = f"💬 Fikr:\n👤 {message.from_user.full_name} (@{message.from_user.username}): {message.text}"
    for admin in ADMIN_IDS:
        try:
            await bot.send_message(admin, feedback)
        except Exception:
            pass
    await message.answer("✅ Fikringiz uchun rahmat!", reply_markup=menu)
    await state.clear()

@dp.message(lambda message: message.text == "📚 Loyiha haqida")
async def project_info(message: Message):
    text = """<b>“Kitobxon kids” tanlovini tashkil etish va o‘tkazish to‘g‘risidagi NIZOM</b>

🔹 <b>Umumiy qoidalar:</b>
• Mazkur Nizom yoshlar o‘rtasida “Kitobxon Kids” tanlovini o‘tkazish tartibini belgilaydi.
• Tanlov 7–10 va 11–14 yoshdagi bolalar uchun mo‘ljallangan.
• Tanlov kitobxonlik madaniyatini oshirishga qaratilgan.

🔹 <b>Tashkilotchilar:</b>
• Yoshlar ishlari agentligi,
• Maktabgacha va maktab ta’limi vazirligi,
• O‘zbekiston bolalar tashkiloti.
"""
    await message.answer(text)

# ======== SPAM/REKLAMA BLOKLASH =========
@dp.message(lambda message: message.chat.type == "private" and isinstance(message.text, str) and any(x in message.text.lower() for x in ["t.me", "http", "@"]))
async def block_ads(message: Message):
    try:
        await message.delete()
    except Exception:
        pass

# ======== ADMIN PANEL =========
@dp.message(lambda message: message.text == "🆕 Test yuklash")
async def admin_upload_prompt(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Siz admin emassiz.")
        return
    await message.answer("📎 Iltimos .txt formatidagi test faylini fayl sifatida yuboring (har bir savol bo'sh qatorda ajratilgan).", reply_markup=admin_menu)

@dp.message(lambda message: message.document is not None and message.document.file_name.endswith(".txt"))
async def handle_test_file_upload(message: Message):
    # faqat adminlar yuklashi mumkin
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Siz admin emassiz.")
        return
    # yuklab olish
    try:
        await message.document.download(destination_file=ACTIVE_TEST_PATH)
        await message.answer("✅ Test fayli muvaffaqiyatli yuklandi va aktiv qilindi.", reply_markup=admin_menu)
        logging.info("Test yuklandi: %s", ACTIVE_TEST_PATH)
    except Exception as e:
        logging.exception("Faylni saqlashda xato")
        await message.answer(f"❌ Faylni saqlashda xatolik: {e}", reply_markup=admin_menu)

@dp.message(lambda message: message.text == "🗑 Testni o‘chirish")
async def admin_delete_test(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Siz admin emassiz.")
        return
    if ACTIVE_TEST_PATH.exists():
        try:
            ACTIVE_TEST_PATH.unlink()
            await message.answer("🗑 Test muvaffaqiyatli o‘chirildi.", reply_markup=admin_menu)
            logging.info("Test o'chirildi.")
        except Exception as e:
            await message.answer(f"❌ Testni o‘chirishda xato: {e}", reply_markup=admin_menu)
    else:
        await message.answer("❗ Test fayli topilmadi.", reply_markup=admin_menu)

@dp.message(lambda message: message.text == "📋 Foydalanuvchilar ro‘yxati")
async def admin_show_users(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Siz admin emassiz.")
        return
    users = get_all_users()
    if not users:
        await message.answer("❗ Ro‘yxat bo‘sh.")
        return
    lines = []
    for u in users:
        uid, child_name, parent_name, region, district, mahalla, age, phone, reg_at = u
        lines.append(f"{uid} | {child_name} ({age}) | {region} - {district} | {phone}")
    # agar juda uzun bo'lsa, bo'lib yuborish
    chunk_size = 20
    for i in range(0, len(lines), chunk_size):
        await message.answer("\n".join(lines[i:i+chunk_size]))

@dp.message(lambda message: message.text == "⬅ Asosiy menyu")
async def back_to_main(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Admin menyuga qaytdingiz.", reply_markup=admin_menu)
    else:
        await message.answer("Asosiy menyu.", reply_markup=menu)

# ======== TEST BOSHLASH (FOYDALANUVCHI) =========
@dp.message(lambda message: message.text == "📖 Testni boshlash")
async def user_start_test(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # tekshir: foydalanuvchi ro'yxatdan o'tganmi?
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT child_name, parent_name, region, district, mahalla, age, phone FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        await message.answer("❗ Avval ro‘yxatdan o‘tishingiz kerak. Iltimos, 📋 Ro‘yxatdan o‘tish tugmasini bosing.")
        return

    if not ACTIVE_TEST_PATH.exists():
        await message.answer("❗ Hozirda hech qanday test yuklanmagan. Keyinroq urinib ko‘ring.")
        return

    # faylni o'qish va parse qilish
    text = ACTIVE_TEST_PATH.read_text(encoding="utf-8")
    questions = parse_test_txt(text)
    if not questions:
        await message.answer("❌ Testni o'qishda yoki formatida xatolik bor. Admin bilan bog'laning.")
        return

    # random yoki tartib bo'yicha — bu yerda random tartib qilamiz
    import random
    random.shuffle(questions)
    # limit 25 ta
    questions = questions[:25]

    # store active test
    ACTIVE_TESTS[user_id] = {
        "questions": questions,
        "q_index": 0,
        "correct_count": 0,
        "answers": [],
        "user_info": {
            "child_name": row[0], "parent_name": row[1], "region": row[2], "district": row[3], "mahalla": row[4], "age": row[5], "phone": row[6]
        },
        "timer_task": None
    }
    await message.answer(f"🧪 Test boshlanmoqda — jami savollar: {len(questions)}. Har bir savolga 60 soniya vaqt. Javobni faqat A/B/C/D harfi bilan yuboring.", reply_markup=ReplyKeyboardRemove())
    # yubor birinchi savol
    await send_question_to_user(user_id)

async def send_question_to_user(user_id: int):
    data = ACTIVE_TESTS.get(user_id)
    if not data:
        return
    idx = data["q_index"]
    questions = data["questions"]
    if idx >= len(questions):
        await finish_test_for_user(user_id)
        return
    q = questions[idx]
    # formatlash
    opts = q.get("options", [])
    opts_text = "\n".join([f"{chr(65+i)}) {opts[i]}" for i in range(min(4, len(opts)))])
    msg = f"<b>Savol {idx+1}:</b>\n{q.get('question')}\n\n{opts_text}\n\nJavobingizni A/B/C/D bilan yuboring."
    try:
        await bot.send_message(user_id, msg)
    except Exception:
        logging.exception("Savol yuborilmadi userga %s", user_id)
    # timer
    # cancel previous
    prev = data.get("timer_task")
    if prev and not prev.done():
        prev.cancel()
    data["timer_task"] = asyncio.create_task(question_timeout(user_id, 60))

async def question_timeout(user_id: int, seconds: int):
    try:
        await asyncio.sleep(seconds)
        data = ACTIVE_TESTS.get(user_id)
        if not data:
            return
        idx = data["q_index"]
        # mark as no answer
        data["answers"].append({"index": idx, "answer": None, "correct": False, "time_up": True})
        data["q_index"] += 1
        await bot.send_message(user_id, "⏱ Vaqt tugadi — bu savolga javob qabul qilinmadi. Keyingi savolga o'tamiz.")
        await send_question_to_user(user_id)
    except asyncio.CancelledError:
        return

@dp.message()
async def catch_answer(message: Message):
    user_id = message.from_user.id
    if user_id not in ACTIVE_TESTS:
        return  # not in test — ignore
    text = (message.text or "").strip().upper()
    if text not in ("A","B","C","D"):
        await message.answer("Iltimos javobni faqat A, B, C yoki D harfi bilan yuboring.")
        return
    data = ACTIVE_TESTS[user_id]
    idx = data["q_index"]
    if idx >= len(data["questions"]):
        await finish_test_for_user(user_id)
        return
    q = data["questions"][idx]
    correct = (text == q.get("answer","").upper())
    if correct:
        data["correct_count"] += 1
    data["answers"].append({"index": idx, "answer": text, "correct": correct, "time_up": False})
    # cancel timer
    t = data.get("timer_task")
    if t and not t.done():
        t.cancel()
    data["q_index"] += 1
    # feedback
    await message.answer("✅ Javob qabul qilindi." + ("\nTo‘g‘ri!" if correct else "\nNoto‘g‘ri."))
    # qisqa kutish va keyingi savol
    await asyncio.sleep(0.6)
    await send_question_to_user(user_id)

async def finish_test_for_user(user_id: int):
    data = ACTIVE_TESTS.get(user_id)
    if not data:
        return
    total = len(data["questions"])
    correct = data["correct_count"]
    percent = round((correct/total)*100) if total>0 else 0
    user_info = data["user_info"]
    # xabar foydalanuvchiga
    try:
        await bot.send_message(user_id,
                               f"🏁 Test yakunlandi!\nTo‘g‘ri javoblar: {correct}/{total}\nNatija: {percent}%\nNatijangiz saqlandi.",
                               reply_markup=menu)
    except Exception:
        pass
    # saqlash CSV
    row = [
        datetime.utcnow().isoformat(),
        str(user_id),
        user_info.get("child_name",""),
        user_info.get("parent_name",""),
        user_info.get("region",""),
        user_info.get("district",""),
        user_info.get("mahalla",""),
        str(user_info.get("age","")),
        user_info.get("phone",""),
        str(correct),
        str(total),
        str(percent)
    ]
    try:
        with open(RESULTS_CSV, "a", encoding="utf-8") as f:
            f.write(",".join([r.replace(",",";") for r in row]) + "\n")
    except Exception:
        logging.exception("Natijani CSVga yozishda xato.")
    # yuborish adminlarga
    admin_msg = (f"📊 Test natijasi:\nUser: {user_id}\n"
                 f"Ism: {user_info.get('child_name')}\n"
                 f"Test: aktiv\nTo'g'ri: {correct}/{total} ({percent}%)\nVaqt: {datetime.utcnow().isoformat()}")
    for admin in ADMIN_IDS:
        try:
            await bot.send_message(admin, admin_msg)
        except Exception:
            pass
    # tozalash
    t = data.get("timer_task")
    if t and not t.done():
        t.cancel()
    del ACTIVE_TESTS[user_id]

# ======== BOTNI ISHGA TUSHURISH =========
async def main():
    init_db()
    logging.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi.")
