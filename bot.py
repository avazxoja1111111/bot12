import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties

# 🔑 Token va Admin ID-lar
TOKEN = "7570796885:AAHYqVOda8L8qKBfq6i6qe_TFv2IDmXsU0Y"
ADMIN_IDS = [6578706277]  # ⚠️ Admin ID o‘rnatildi

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

# 📌 Tuman tanlash
tumanlar = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=t) for t in ["Yunusobod", "Shayxontohur", "Mirobod"]],
    [KeyboardButton(text=t) for t in ["Uchtepa", "Olmazor", "Yakkasaroy"]],
    [KeyboardButton(text=t) for t in ["Chilonzor", "Sergeli", "Bektemir"]],
    [KeyboardButton(text=t) for t in ["Mirzo Ulug‘bek", "Yashnobod", "Yangihayot"]]
], resize_keyboard=True)

# 📌 Yosh tanlash
yosh_tanlash = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=str(y)) for y in range(7, 11)]
], resize_keyboard=True)

# 📌 Telefon raqamni yuborish
phone_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]
], resize_keyboard=True)

# 📌 Ro‘yxatdan o‘tish uchun FSM
class Registration(StatesGroup):
    child_name = State()
    parent_name = State()
    region = State()
    age = State()
    phone = State()
    feedback = State()

# 📌 /start buyrug‘i
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Salom! 'KITOBXON KIDS' botiga xush kelibsiz!", reply_markup=menu)

# 📋 Ro‘yxatdan o‘tish
@dp.message(lambda message: message.text == "📋 Ro‘yxatdan o‘tish")
async def register_start(message: types.Message, state: FSMContext):
    await message.answer("👶 Farzandingiz ismini kiriting:")
    await state.set_state(Registration.child_name)

@dp.message(Registration.child_name)
async def register_child_name(message: types.Message, state: FSMContext):
    await state.update_data(child_name=message.text)
    await message.answer("👨‍👩‍👦 Ota-onaning ismini kiriting:")
    await state.set_state(Registration.parent_name)

@dp.message(Registration.parent_name)
async def register_parent_name(message: types.Message, state: FSMContext):
    await state.update_data(parent_name=message.text)
    await message.answer("🌍 Tumanni tanlang:", reply_markup=tumanlar)
    await state.set_state(Registration.region)

@dp.message(Registration.region)
async def register_region(message: types.Message, state: FSMContext):
    await state.update_data(region=message.text)
    await message.answer("📅 Yoshni tanlang:", reply_markup=yosh_tanlash)
    await state.set_state(Registration.age)

@dp.message(Registration.age)
async def register_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
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

    # 📤 Adminlarga xabar yuborish
    reg_info = f"📋 Yangi ro‘yxatdan o‘tish:\n👶 Farzand: {user_data['child_name']}\n👨‍👩‍👦 Ota-ona: {user_data['parent_name']}\n🌍 Tuman: {user_data['region']}\n📅 Yosh: {user_data['age']}\n📞 Telefon: {phone_number}"

    for admin in ADMIN_IDS:
        await bot.send_message(admin, reg_info)

    await message.answer("✅ Ro‘yxatdan o‘tish muvaffaqiyatli yakunlandi!", reply_markup=menu)
    await state.clear()


    # 📤 Adminlarga xabar yuborish
    reg_info = f"📋 Yangi ro‘yxatdan o‘tish:\n👶 Farzand: {user_data['child_name']}\n👨‍👩‍👦 Ota-ona: {user_data['parent_name']}\n🌍 Tuman: {user_data['region']}\n📅 Yosh: {user_data['age']}\n📞 Telefon: {phone_number}"

    for admin in ADMIN_IDS:
        await bot.send_message(admin, reg_info)

    await message.answer("✅ Ro‘yxatdan o‘tish muvaffaqiyatli yakunlandi!", reply_markup=menu)
    await state.clear()

# 📢 Fikr-mulohaza qoldirish
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

# **Botni ishga tushirish**
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
