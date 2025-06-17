import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties

TOKEN = "7570796885:AAHYqVOda8L8qKBfq6i6qe_TFv2IDmXsU0Y"  # 🔑 Tokeningizni bu yerga yozing
ADMIN_IDS = [6578706277, 7853664401]  # Admin ID-lar

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# 📌 Viloyat va tumanlar
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
    # ... boshqa viloyatlar va tumanlarni qo‘shing
}

# 📌 Keyboard yaratish
def get_viloyat_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=region)] for region in regions],
        resize_keyboard=True
    )

def get_tuman_keyboard(region_name):
    tumans = regions.get(region_name, [])
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t)] for t in tumans],
        resize_keyboard=True
    )

phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]],
    resize_keyboard=True
)

# 📌 FSM holatlar
class Registration(StatesGroup):
    phone = State()
    child_name = State()
    parent_name = State()
    region = State()
    district = State()
    mahalla = State()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Assalomu alaykum!\n<b>KITOBXON KIDS</b> loyihasi botiga xush kelibsiz!\n\nRo‘yxatdan o‘tish uchun <b>'📋 Ro‘yxatdan o‘tish'</b> tugmasini bosing.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📋 Ro‘yxatdan o‘tish")]],
            resize_keyboard=True
        )
    )

@dp.message(lambda msg: msg.text == "📋 Ro‘yxatdan o‘tish")
async def ask_phone(message: types.Message, state: FSMContext):
    await message.answer("📞 Iltimos, telefon raqamingizni yuboring:", reply_markup=phone_keyboard)
    await state.set_state(Registration.phone)

@dp.message(Registration.phone)
async def get_phone(message: types.Message, state: FSMContext):
    if not message.contact:
        await message.answer("📞 Tugmadan foydalangan holda telefon raqamingizni yuboring.")
        return
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("👶 Farzandingiz ism familiyasini kiriting:")
    await state.set_state(Registration.child_name)

@dp.message(Registration.child_name)
async def get_child_name(message: types.Message, state: FSMContext):
    await state.update_data(child_name=message.text)
    await message.answer("👨‍👩‍👧‍👦 Ota yoki onaning ism familiyasini kiriting:")
    await state.set_state(Registration.parent_name)

@dp.message(Registration.parent_name)
async def get_parent_name(message: types.Message, state: FSMContext):
    await state.update_data(parent_name=message.text)
    await message.answer("📍 Viloyatni tanlang:", reply_markup=get_viloyat_keyboard())
    await state.set_state(Registration.region)

@dp.message(Registration.region)
async def get_region(message: types.Message, state: FSMContext):
    region = message.text
    if region not in regions:
        await message.answer("❌ Iltimos, ro‘yxatdan viloyat tanlang.")
        return
    await state.update_data(region=region)
    await message.answer("🏙 Tumanni tanlang:", reply_markup=get_tuman_keyboard(region))
    await state.set_state(Registration.district)

@dp.message(Registration.district)
async def get_district(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in regions.get(data['region'], []):
        await message.answer("❌ Iltimos, mavjud tumanlardan birini tanlang.")
        return
    await state.update_data(district=message.text)
    await message.answer("🏘 Mahallangiz nomini yozing:")
    await state.set_state(Registration.mahalla)

@dp.message(Registration.mahalla)
async def finish_registration(message: types.Message, state: FSMContext):
    await state.update_data(mahalla=message.text)
    user_data = await state.get_data()

    reg_text = (
        "📝 <b>Yangi ro‘yxatdan o‘tgan foydalanuvchi:</b>\n\n"
        f"👶 Farzand: {user_data['child_name']}\n"
        f"👨‍👩‍👧 Ota/ona: {user_data['parent_name']}\n"
        f"📍 Viloyat: {user_data['region']}\n"
        f"🏙 Tuman: {user_data['district']}\n"
        f"🏘 Mahalla: {user_data['mahalla']}\n"
        f"📞 Tel: {user_data['phone']}"
    )

    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, reg_text)

    await message.answer("✅ Ro‘yxatdan o‘tish muvaffaqiyatli yakunlandi. Rahmat!", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

# ▶️ Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
