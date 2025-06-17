import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties

TOKEN = "7570796885:AAHYqVOda8L8qKBfq6i6qe_TFv2IDmXsU0Y"
ADMIN_IDS = [6578706277, 7853664401]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# 📌 Viloyat va tumanlar

REGIONS = {
    "Toshkent shahri": [
        "Bektemir", "Chilonzor", "Mirzo Ulug‘bek", "Mirobod", "Olmazor",
        "Sergeli", "Shayxontohur", "Uchtepa", "Yakkasaroy", "Yashnobod", "Yunusobod"
    ],
    "Toshkent viloyati": [
        "Bekobod", "Bo‘ka", "Bo‘stonliq", "Chinoz", "Qibray", "Ohangaron", "Oqqo‘rg‘on",
        "Parkent", "Piskent", "Quyichirchiq", "Toshkent tumani", "Yangiyo‘l", "Yuqorichirchiq", "Zangiota"
    ],
    "Andijon": [
        "Andijon shahri", "Andijon tumani", "Asaka", "Baliqchi", "Bo‘ston", "Buloqboshi",
        "Izboskan", "Jalaquduq", "Qo‘rg‘ontepa", "Marhamat", "Oltinko‘l", "Paxtaobod", "Shahrixon", "Ulug‘nor", "Xo‘jaobod"
    ],
    "Namangan": [
        "Chortoq", "Chust", "Kosonsoy", "Mingbuloq", "Namangan shahri", "Namangan tumani",
        "Norin", "Pop", "To‘raqo‘rg‘on", "Uychi", "Uchqo‘rg‘on", "Yangiqo‘rg‘on"
    ],
    "Farg‘ona": [
        "Bag‘dod", "Beshariq", "Buvayda", "Dang‘ara", "Farg‘ona shahri", "Farg‘ona tumani",
        "Furqat", "Qo‘shtepa", "Oltiariq", "Quva", "Quvasoy", "Rishton", "So‘x", "Toshloq", "Uchko‘prik", "Yozyovon"
    ],
    "Samarqand": [
        "Bulung‘ur", "Ishtixon", "Jomboy", "Kattaqo‘rg‘on shahri", "Kattaqo‘rg‘on tumani", "Narpay", "Nurobod",
        "Oqdaryo", "Paxtachi", "Pastdarg‘om", "Payariq", "Samarqand shahri", "Samarqand tumani", "Tayloq", "Urgut"
    ],
    "Buxoro": [
        "Buxoro shahri", "Buxoro tumani", "G‘ijduvon", "Jondor", "Kogon", "Kogon tumani", "Olot", "Peshku", "Qorako‘l",
        "Qorovulbozor", "Romitan", "Shofirkon", "Vobkent"
    ],
    "Navoiy": [
        "Karmana", "Konimex", "Navbahor", "Navoiy shahri", "Nurota", "Xatirchi", "Zarafshon", "Qiziltepa", "Tomdi", "Uchquduq"
    ],
    "Qashqadaryo": [
        "Dehqonobod", "G‘uzor", "Qamashi", "Qarshi shahri", "Qarshi tumani", "Kasbi", "Kitob",
        "Koson", "Mirishkor", "Muborak", "Nishon", "Shahrisabz shahri", "Shahrisabz tumani", "Yakkabog‘"
    ],
    "Surxondaryo": [
        "Angor", "Bandixon", "Boysun", "Denov", "Jarqo‘rg‘on", "Muzrabot", "Oltinsoy", "Qiziriq",
        "Qumqo‘rg‘on", "Sariosiyo", "Sherobod", "Sho‘rchi", "Termiz shahri", "Termiz tumani", "Uzun"
    ],
    "Jizzax": [
        "Arnasoy", "Baxmal", "Do‘stlik", "Forish", "G‘allaorol", "Sharof Rashidov", "Mirzacho‘l",
        "Paxtakor", "Yangiobod", "Zarbdor", "Zafarobod", "Zomin"
    ],
    "Sirdaryo": [
        "Boyovut", "Guliston shahri", "Guliston tumani", "Mirzaobod", "Oqoltin", "Sayxunobod",
        "Sardoba", "Sirdaryo", "Xavos", "Shirin", "Yangiyer"
    ],
    "Xorazm": [
        "Bog‘ot", "Gurlan", "Xiva shahri", "Xiva tumani", "Hazorasp", "Shovot", "Urganch shahri", "Urganch tumani",
        "Yangibozor", "Yangiariq", "Qo‘shko‘pir"
    ],
    "Qoraqalpog‘iston": [
        "Amudaryo", "Beruniy", "Chimboy", "Ellikqal‘a", "Kegeyli", "Mo‘ynoq", "Nukus shahri", "Nukus tumani",
        "Qanliko‘l", "Qo‘ng‘irot", "Qorao‘zak", "Shumanay", "Taxtako‘pir", "To‘rtko‘l", "Xo‘jayli"
    ]
}


def get_viloyat_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=region)] for region in REGIONS],
        resize_keyboard=True
    )

def get_tuman_keyboard(region_name):
    tumans = REGIONS.get(region_name, [])
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t)] for t in tumans],
        resize_keyboard=True
    )

phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]],
    resize_keyboard=True
)

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
    await message.answer("👶 Farzandingiz <b>familiyasi, ismi, otasining ismi</b>ni kiriting.\n\nMasalan: <i>Shukurullaxo'djayev Avazxo'ja O'ktamxo'ja o'g'li</i>")
    await state.set_state(Registration.child_name)

@dp.message(Registration.child_name)
async def get_child_name(message: types.Message, state: FSMContext):
    await state.update_data(child_name=message.text)
    await message.answer("👨‍👩‍👧‍👦 Ota yoki onaning <b>familiyasi, ismi, otasining ismi</b>ni kiriting.\n\nMasalan: <i>Shukurullaxo'djayev O'ktamxo'ja Inomxo'ja o'g'li</i>")
    await state.set_state(Registration.parent_name)

@dp.message(Registration.parent_name)
async def get_parent_name(message: types.Message, state: FSMContext):
    await state.update_data(parent_name=message.text)
    await message.answer("📍 Viloyatni tanlang:", reply_markup=get_viloyat_keyboard())
    await state.set_state(Registration.region)

@dp.message(Registration.region)
async def get_region(message: types.Message, state: FSMContext):
    region = message.text
    if region not in REGIONS:
        await message.answer("❌ Iltimos, ro‘yxatdan viloyat tanlang.")
        return
    await state.update_data(region=region)
    await message.answer("🏙 Tumanni tanlang:", reply_markup=get_tuman_keyboard(region))
    await state.set_state(Registration.district)

@dp.message(Registration.district)
async def get_district(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in REGIONS.get(data['region'], []):
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

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
