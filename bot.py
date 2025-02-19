import logging
import re
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties

# 🔑 Token va Admin ID-lar
TOKEN = "7627279076:AAGXu8XLQLvPOWE2S3ZnP9Bk_N0H6o2jWg8"
ADMIN_IDS = [6578706277]  # ⚠️ Admin ID-larni shu yerga yozing!

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

# 📌 Ro‘yxatdan o‘tish uchun FSM
class Registration(StatesGroup):
    child_name = State()
    parent_name = State()
    age = State()
    phone = State()

# 📌 /start buyrug‘i
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Salom! 'KITOBXON KIDS' botiga xush kelibsiz!", reply_markup=menu)

# 📋 Ro‘yxatdan o‘tish tugmasi
@dp.message(lambda message: message.text == "📋 Ro‘yxatdan o‘tish")
async def register(message: types.Message, state: FSMContext):
    await message.answer("👶 Farzandingizning ismi va familiyasini kiriting:")
    await state.set_state(Registration.child_name)

@dp.message(Registration.child_name)
async def get_child_name(message: types.Message, state: FSMContext):
    await state.update_data(child_name=message.text)
    await message.answer("👤 Ota yoki onangizning ismi va familiyasini kiriting:")
    await state.set_state(Registration.parent_name)

@dp.message(Registration.parent_name)
async def get_parent_name(message: types.Message, state: FSMContext):
    await state.update_data(parent_name=message.text)
    await message.answer("📅 Farzandingiz yoshini kiriting (7-10 oralig‘ida):")
    await state.set_state(Registration.age)

@dp.message(Registration.age)
async def get_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (7 <= int(message.text) <= 10):
        await message.answer("❌ Yoshingiz noto‘g‘ri! Faqat 7 dan 10 yoshgacha bo‘lgan bolalar ro‘yxatdan o‘ta oladi. Qayta kiriting:")
        return
    await state.update_data(age=message.text)
    await message.answer("📞 Telefon raqamingizni kiriting (998XXYYYYYYY formatida):")
    await state.set_state(Registration.phone)

@dp.message(Registration.phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone_pattern = re.compile(r"^998\d{9}$")
    if not phone_pattern.match(message.text):
        await message.answer("❌ Telefon raqami noto‘g‘ri! 998XXYYYYYYY formatida kiriting:")
        return

    await state.update_data(phone=message.text)
    data = await state.get_data()

    # 📂 Ma'lumotlarni faylga yozish
    with open("users.txt", "a", encoding="utf-8") as file:
        file.write(f"{data['child_name']}, {data['parent_name']}, {data['age']}, {data['phone']}\n")

    await message.answer(
        f"✅ Ro‘yxatdan o‘tish tugadi!\n\n"
        f"📌 <b>Ma’lumotlaringiz:</b>\n"
        f"👶 Farzandingiz: {data['child_name']}\n"
        f"👤 Ota/ona: {data['parent_name']}\n"
        f"📅 Yosh: {data['age']}\n"
        f"📞 Telefon: {data['phone']}",
        parse_mode=ParseMode.HTML
    )
    await state.clear()

# 📌 💬 Fikr va maslahatlar
class Feedback(StatesGroup):
    text = State()

@dp.message(lambda message: message.text == "💬 Fikr va maslahatlar")
async def ask_feedback(message: types.Message, state: FSMContext):
    await message.answer("✍️ Fikr va takliflaringizni yozing:")
    await state.set_state(Feedback.text)

@dp.message(Feedback.text)
async def receive_feedback(message: types.Message, state: FSMContext):
    feedback_text = message.text
    user_id = message.from_user.id
    username = message.from_user.username if message.from_user.username else "No username"

    # 📂 Fikrni faylga yozish
    with open("feedbacks.txt", "a", encoding="utf-8") as file:
        file.write(f"User ID: {user_id}, Username: {username}, Feedback: {feedback_text}\n")

    # 📩 Adminlarga yuborish
    admin_message = (
        f"📩 <b>Yangi fikr va taklif:</b>\n"
        f"👤 <b>Foydalanuvchi:</b> @{username} (ID: {user_id})\n"
        f"💬 <b>Fikr:</b> {feedback_text}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_message, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"⚠️ Admin {admin_id} ga habar yuborishda xatolik: {e}")

    await message.answer("✅ Fikringiz uchun rahmat! Takliflaringiz inobatga olinadi.")
    await state.clear()

# 📚 Loyiha haqida
@dp.message(lambda message: message.text == "📚 Loyiha haqida")
async def about_project(message: types.Message):
    await message.answer(
        "📖 'KITOBXON KIDS' loyihasi bolalar uchun kitobxonlikni targ‘ib qilishga qaratilgan.\n\n"
        "☎️ <b>Bog‘lanish uchun:</b>\n"
        "📩 @Fotima0123\n"
        "📞 +998882802806 / +998946442069",
        parse_mode=ParseMode.HTML
    )

# **Botni ishga tushirish**
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
