import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties

# 🔑 Token va Admin ID-lar
TOKEN = "7570796885:AAHYqVOda8L8qKBfq6i6qe_TFv2IDmXsU0Y"
ADMIN_IDS = [6578706277, 7853664401]
CHANNEL_USERNAME = "@Kitobxon_Kids"

# 🛠 Logging sozlamalari
logging.basicConfig(level=logging.INFO)

# 🤖 Bot va Dispatcher yaratish
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# 📌 Klaviatura tugmalari
menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📋 Ro‘yxatdan o‘tish")],
    [KeyboardButton(text="💬 Fikr va maslahatlar")],
    [KeyboardButton(text="📚 Loyiha haqida")]
], resize_keyboard=True)

# 📌 Viloyatlar va tumanlar
REGIONS = {
    "Toshkent shahri": ["Bektemir", "Chilonzor", "Mirzo Ulug‘bek", "Mirobod", "Olmazor", "Shayxontohur", "Sergeli", "Uchtepa", "Yashnobod", "Yakkasaroy", "Yunusobod"],
    "Toshkent viloyati": ["Bekabad", "Bo‘ka", "Bo‘stonliq", "Chinoz", "Chirchiq", "Ohangaron", "Oqqo‘rg‘on", "Parkent", "Piskent", "Quyichirchiq", "O‘rtachirchiq", "Yangiyo‘l", "Yuqorichirchiq", "Zangiota", "Nurafshon", "Olmaliq", "Angren"],
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

# 📌 Ro‘yxatdan o‘tish uchun FSM
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

# 📌 /start buyrug‘i va majburiy obuna tekshiruvi
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    if chat_member.status not in ["member", "administrator", "creator"]:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Obuna bo'lish", url=f"https://t.me/{Kitobxon_Kids[1:]}")],
            [InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="check_sub")]
        ])
        await message.answer("✉️ Iltimos, quyidagi kanalga obuna bo'ling:", reply_markup=keyboard)
        await state.set_state(Registration.check_subscription)
    else:
        await message.answer("👋 Salom! 'KITOBXON KIDS' botiga xush kelibsiz!", reply_markup=menu)

@dp.callback_query(lambda c: c.data == "check_sub")
async def check_subscription(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    if chat_member.status not in ["member", "administrator", "creator"]:
        await callback_query.answer("❌ Hali ham obuna emassiz!", show_alert=True)
    else:
        await bot.send_message(user_id, "👋 Salom! 'KITOBXON KIDS' botiga xush kelibsiz!", reply_markup=menu)
        await state.clear()

# Quyidagi handlerlar avvalgi holatida qoladi (Ro‘yxatdan o‘tish, fikr yuborish)
# ➥ Agar xohlasangiz, ularni ham to‘liq quyida beraman.

# 📋 Ro‘yxatdan o‘tish jarayoni va boshqa qism ham siz bergan kod bilan to‘liq saqlangan
# 📋 Ro‘yxatdan o‘tish
@dp.message(lambda message: message.text == "📋 Ro‘yxatdan o‘tish")
async def register_start(message: types.Message, state: FSMContext):
    await message.answer("👶 Farzandingiz ism familiyasini kiriting:")
    await state.set_state(Registration.child_name)

@dp.message(Registration.child_name)
async def register_child_name(message: types.Message, state: FSMContext):
    await state.update_data(child_name=message.text)
    await message.answer("👨‍👩‍👦 Ota-onaning ism familiyasini kiriting:")
    await state.set_state(Registration.parent_name)

@dp.message(Registration.parent_name)
async def register_parent_name(message: types.Message, state: FSMContext):
    await state.update_data(parent_name=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=region)] for region in REGIONS.keys()],
        resize_keyboard=True
    )
    await message.answer("🌍 Viloyatni tanlang:", reply_markup=keyboard)
    await state.set_state(Registration.region)

@dp.message(Registration.region)
async def register_region(message: types.Message, state: FSMContext):
    region = message.text
    await state.update_data(region=region)
    districts = REGIONS.get(region, [])
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=dist)] for dist in districts],
        resize_keyboard=True
    )
    await message.answer("🏙 Tumaningizni tanlang:", reply_markup=keyboard)
    await state.set_state(Registration.district)

@dp.message(Registration.district)
async def register_district(message: types.Message, state: FSMContext):
    await state.update_data(district=message.text)
    await message.answer("🏘 Mahallangiz nomini kiriting:")
    await state.set_state(Registration.mahalla)

@dp.message(Registration.mahalla)
async def register_mahalla(message: types.Message, state: FSMContext):
    await state.update_data(mahalla=message.text)
    yosh_tanlash = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=str(y)) for y in range(7, 11)]], resize_keyboard=True)
    await message.answer("📅 Yoshni tanlang:", reply_markup=yosh_tanlash)
    await state.set_state(Registration.age)

@dp.message(Registration.age)
async def register_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    phone_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]], resize_keyboard=True)
    await message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=phone_button)
    await state.set_state(Registration.phone)

@dp.message(Registration.phone)
async def register_phone(message: types.Message, state: FSMContext):
    if not message.contact:
        await message.answer("📞 Iltimos, 'Telefon raqamni yuborish' tugmasi orqali raqamingizni jo‘nating.")
        return

    user_data = await state.get_data()
    phone_number = message.contact.phone_number
    user_data['phone'] = phone_number

    reg_info = (
        f"📋 Yangi ro‘yxatdan o‘tish:\n"
        f"👶 Farzand: {user_data['child_name']}\n"
        f"👨‍👩‍👦 Ota-ona: {user_data['parent_name']}\n"
        f"🌍 Viloyat: {user_data['region']}\n"
        f"🏙 Tuman: {user_data['district']}\n"
        f"🏘 Mahalla: {user_data['mahalla']}\n"
        f"📅 Yosh: {user_data['age']}\n"
        f"📞 Telefon: {phone_number}"
    )

    for admin in ADMIN_IDS:
        await bot.send_message(admin, reg_info)

    await message.answer("✅ Ro‘yxatdan o‘tish muvaffaqiyatli yakunlandi!", reply_markup=menu)
    await state.clear()

@dp.message(lambda message: message.text == "💬 Fikr va maslahatlar")
async def feedback_prompt(message: types.Message, state: FSMContext):
    await message.answer("✍️ Fikringizni yozing:")
    await state.set_state(Registration.feedback)

@dp.message(Registration.feedback)
async def save_feedback(message: types.Message, state: FSMContext):
    feedback = f"💬 Fikr-mulohaza:\n👤 {message.from_user.full_name} (@{message.from_user.username}): {message.text}"
    for admin in ADMIN_IDS:
        await bot.send_message(admin, feedback)
    await message.answer("✅ Fikringiz uchun rahmat!", reply_markup=menu)
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
 
