import logging
import asyncio
import json
import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
import tempfile
from functools import lru_cache
import aiofiles
from asyncio import Semaphore

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, 
    InlineKeyboardButton, BufferedInputFile
)
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties

# Excel library for admin exports only
try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from io import BytesIO
except ImportError:
    print("Required libraries not installed. Install with: pip install openpyxl")

# PDF library for admin reports only
try:
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.pagesizes import letter, A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
except ImportError:
    print("Required libraries not installed. Install with: pip install reportlab")

# 🔑 Configuration
TOKEN = os.getenv("BOT_TOKEN", "7570796885:AAHHfpXanemNYvW-wVT2Rv40U0xq-XjxSwk")
SUPER_ADMIN_ID = int(os.getenv("SUPER_ADMIN_ID", "6578706277"))
SPECIAL_ADMIN_IDS = [6578706277, 7853664401]  # Only these can manage super-admins
CHANNEL_USERNAME = "@Kitobxon_Kids"

# O'zbekiston vaqti (UTC+5)
UZBEKISTAN_TZ = timezone(timedelta(hours=5))

def get_uzbekistan_time():
    """O'zbekiston vaqti bo'yicha hozirgi vaqtni qaytaradi"""
    return datetime.now(UZBEKISTAN_TZ)

# 🛠 Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Performance optimization settings
MAX_CONCURRENT_OPERATIONS = 100  # Semaphore limit
FILE_CACHE_TTL = 300  # Cache TTL in seconds
MAX_BROADCAST_BATCH = 50  # Batch size for broadcasts

# Semaphores for concurrency control
file_semaphore = Semaphore(MAX_CONCURRENT_OPERATIONS)
broadcast_semaphore = Semaphore(10)  # Limit broadcast operations

# In-memory cache for frequently accessed data
_cache = {}
_cache_timestamps = {}

# 🤖 Bot and Dispatcher with optimized settings
bot = Bot(
    token=TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=None  # Use default session with connection pooling
)
dp = Dispatcher()

# 📁 Data storage files
DATA_DIR = "bot_data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
ADMINS_FILE = os.path.join(DATA_DIR, "admins.json")
TESTS_FILE = os.path.join(DATA_DIR, "tests.json")
RESULTS_FILE = os.path.join(DATA_DIR, "results.json")
BROADCASTS_FILE = os.path.join(DATA_DIR, "broadcasts.json")
STATISTICS_FILE = os.path.join(DATA_DIR, "statistics.json")

# 📌 Complete Uzbekistan regions data with all districts and mahallas
REGIONS = {
    "Toshkent shahri": {
        "Bektemir": [
            "Bektemir", "Qoraxon", "Yangihayot", "Yangiobod", "Bog'bon", 
            "Markaziy", "Tinchlik", "Mustaqillik", "Yoshlik", "Do'stlik"
        ],
        "Chilonzor": [
            "Chilonzor", "Qatartol", "Yashnobod", "Navbahor", "Almazar",
            "O'zbekiston", "Tinchlik", "Buyuk Ipak yo'li", "Kichik Halqa", "Katta Halqa"
        ],
        "Mirzo Ulug'bek": [
            "Mirzo Ulug'bek", "Bobur", "Qoraqamish", "Universitet", "Sebzor",
            "Markaziy", "Yangiobod", "Bog'ishamol", "Xadra", "Qo'yliq"
        ],
        "Mirobod": [
            "Mirobod", "Kichik halqa", "Katta halqa", "Arxitektor", "Sebzor",
            "Markaziy", "Sharaf Rashidov", "Xadichalar", "Qorasu", "Yangiobod"
        ],
        "Olmazor": [
            "Olmazor", "Kichik Olmazor", "Katta Olmazor", "Bog'bon", "Yunusota",
            "Kichikhalqa", "Kattahalqa", "Markaziy", "Tinchlik", "Yangiabad"
        ],
        "Shayxontohur": [
            "Shayxontohur", "Beruniy", "Chorsu", "Eski shahar", "Yunusobod",
            "Markaziy", "Sebzor", "Bog'ishamol", "Qoraqamish", "Yangiqishloq"
        ],
        "Sergeli": [
            "Sergeli", "Qo'shtepa", "Yangiobod", "Markaziy", "Bog'bon",
            "Tinchlik", "Xonobod", "Yangihayot", "Do'stlik", "Mustaqillik"
        ],
        "Uchtepa": [
            "Uchtepa", "Kichik Uchtepa", "Katta Uchtepa", "Bog'bon", "Markaziy",
            "Tinchlik", "Yangiobod", "Do'stlik", "Mustaqillik", "Navbahor"
        ],
        "Yashnobod": [
            "Yashnobod", "Kichik Yashnobod", "Katta Yashnobod", "Markaziy", "Bog'bon",
            "Tinchlik", "Yangiobod", "Do'stlik", "Navbahor", "Sebzor"
        ],
        "Yakkasaroy": [
            "Yakkasaroy", "Markaziy", "Bog'ishamol", "Sebzor", "Qoraqamish",
            "Tinchlik", "Yangiobod", "Do'stlik", "Navbahor", "Mustaqillik"
        ],
        "Yunusobod": [
            "Yunusobod", "Kichik Yunusobod", "Katta Yunusobod", "Markaziy", "Bog'bon",
            "Tinchlik", "Yangiobod", "Do'stlik", "Navbahor", "Sebzor"
        ]
    },
    "Toshkent viloyati": {
        "Bekabad": ["Bekabad shahri", "Markaziy", "Bog'bon", "Yangiobod", "Tinchlik"],
        "Bo'ka": ["Bo'ka", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Bo'stonliq": ["Bo'stonliq", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Chinoz": ["Chinoz", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Chirchiq": ["Chirchiq shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Ohangaron": ["Ohangaron shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Oqqo'rg'on": ["Oqqo'rg'on", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Parkent": ["Parkent", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Piskent": ["Piskent", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Quyichirchiq": ["Quyichirchiq", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "O'rtachirchiq": ["O'rtachirchiq", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Yangiyo'l": ["Yangiyo'l shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Toshkent": ["Toshkent tumani", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Yuqorichirchiq": ["Yuqorichirchiq", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Zangiota": ["Zangiota", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Nurafshon": ["Nurafshon shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Olmaliq": ["Olmaliq shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Angren": ["Angren shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"]
    },
    "Andijon": {
        "Andijon shahri": ["1-mahalla", "2-mahalla", "3-mahalla", "4-mahalla", "5-mahalla"],
        "Asaka": ["Asaka shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Baliqchi": ["Baliqchi", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Bo'ston": ["Bo'ston", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Buloqboshi": ["Buloqboshi", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Izboskan": ["Izboskan", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Jalaquduq": ["Jalaquduq", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Marhamat": ["Marhamat", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Oltinko'l": ["Oltinko'l", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Paxtaobod": ["Paxtaobod", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Paytug'": ["Paytug'", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Qo'rg'ontepa": ["Qo'rg'ontepa", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Shahriston": ["Shahriston", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Xo'jaobod": ["Xo'jaobod", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"]
    },
    "Farg'ona": {
        "Beshariq": ["Beshariq", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Buvayda": ["Buvayda", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Dang'ara": ["Dang'ara", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Farg'ona shahri": ["1-mahalla", "2-mahalla", "3-mahalla", "4-mahalla", "5-mahalla"],
        "Ferghana tumani": ["Ferghana", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Furqat": ["Furqat", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Qo'qon": ["Qo'qon shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Quva": ["Quva", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Rishton": ["Rishton", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "So'x": ["So'x", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Toshloq": ["Toshloq", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Uchko'prik": ["Uchko'prik", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Yozyovon": ["Yozyovon", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Oltiariq": ["Oltiariq", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"]
    },
    "Namangan": {
        "Chortoq": ["Chortoq", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Chust": ["Chust", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Kosonsoy": ["Kosonsoy", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Namangan shahri": ["1-mahalla", "2-mahalla", "3-mahalla", "4-mahalla", "5-mahalla"],
        "Norin": ["Norin", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Pop": ["Pop", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "To'raqo'rg'on": ["To'raqo'rg'on", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Uychi": ["Uychi", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Uchqo'rg'on": ["Uchqo'rg'on", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Yangiqo'rg'on": ["Yangiqo'rg'on", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Yangihayot": ["Yangihayot", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"]
    },
    "Samarqand": {
        "Bulung'ur": ["Bulung'ur", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Ishtixon": ["Ishtixon", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Jomboy": ["Jomboy", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Kattakurgan": ["Kattakurgan shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Oqdaryo": ["Oqdaryo", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Payariq": ["Payariq", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Pastdarg'om": ["Pastdarg'om", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Qo'shrabot": ["Qo'shrabot", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Samarqand shahri": ["1-mahalla", "2-mahalla", "3-mahalla", "4-mahalla", "5-mahalla"],
        "Toyloq": ["Toyloq", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Urgut": ["Urgut", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Taxta ko'prik": ["Taxta ko'prik", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Narpay": ["Narpay", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"]
    },
    "Buxoro": {
        "Buxoro shahri": ["1-mahalla", "2-mahalla", "3-mahalla", "4-mahalla", "5-mahalla"],
        "Buxoro tumani": ["Buxoro", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "G'ijduvon": ["G'ijduvon", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Jondor": ["Jondor", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Kogon": ["Kogon shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Olot": ["Olot", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Peshku": ["Peshku", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Qorako'l": ["Qorako'l", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Qorovulbozor": ["Qorovulbozor", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Romitan": ["Romitan", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Shofirkon": ["Shofirkon", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Vobkent": ["Vobkent", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"]
    },
    "Jizzax": {
        "Baxmal": ["Baxmal", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Chiroqchi": ["Chiroqchi", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Do'stlik": ["Do'stlik", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Forish": ["Forish", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "G'allaorol": ["G'allaorol", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Zarafshon": ["Zarafshon", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Zarbdor": ["Zarbdor", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Zomin": ["Zomin", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Zafarobod": ["Zafarobod", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Yangiobod": ["Yangiobod", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Jizzax shahri": ["1-mahalla", "2-mahalla", "3-mahalla", "4-mahalla", "5-mahalla"],
        "Mirzacho'l": ["Mirzacho'l", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"]
    },
    "Navoiy": {
        "Karmana": ["Karmana", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Konimex": ["Konimex", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Navbahor": ["Navbahor", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Nurota": ["Nurota", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Tomdi": ["Tomdi", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Xatirchi": ["Xatirchi", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Uchquduq": ["Uchquduq shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Navoiy shahri": ["1-mahalla", "2-mahalla", "3-mahalla", "4-mahalla", "5-mahalla"],
        "Zarafshon": ["Zarafshon shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Qiziltepa": ["Qiziltepa", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"]
    },
    "Qashqadaryo": {
        "Chiroqchi": ["Chiroqchi", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "G'uzor": ["G'uzor", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Qarshi": ["Qarshi shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Kitob": ["Kitob", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Koson": ["Koson", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Mirishkor": ["Mirishkor", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Muborak": ["Muborak", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Nishon": ["Nishon", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Shahrisabz": ["Shahrisabz shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Dehqonobod": ["Dehqonobod", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Yakkabog'": ["Yakkabog'", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Qamashi": ["Qamashi", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Kasbi": ["Kasbi", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Guzar": ["Guzar shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"]
    },
    "Surxondaryo": {
        "Angor": ["Angor", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Bandixon": ["Bandixon", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Denov": ["Denov", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Jarqo'rg'on": ["Jarqo'rg'on", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Muzrabot": ["Muzrabot", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Oltinsoy": ["Oltinsoy", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Sariosiyo": ["Sariosiyo", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Sherobod": ["Sherobod", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Sho'rchi": ["Sho'rchi", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Termiz": ["Termiz shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Uzun": ["Uzun", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Boysun": ["Boysun", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Qumqo'rg'on": ["Qumqo'rg'on", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"]
    },
    "Sirdaryo": {
        "Guliston": ["Guliston shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Guliston tumani": ["Guliston", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Mirzaobod": ["Mirzaobod", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Oqoltin": ["Oqoltin", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Sardoba": ["Sardoba shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Sayxunobod": ["Sayxunobod", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Sirdaryo tumani": ["Sirdaryo", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Xovos": ["Xovos", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Boyovut": ["Boyovut", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Yangiyer": ["Yangiyer shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"]
    },
    "Xorazm": {
        "Bog'ot": ["Bog'ot", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Gurlan": ["Gurlan", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Hazorasp": ["Hazorasp", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Khiva": ["Khiva shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Qo'shko'pir": ["Qo'shko'pir", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Shovot": ["Shovot", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Urganch tumani": ["Urganch", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Xonqa": ["Xonqa", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Yangiariq": ["Yangiariq", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Yangibozor": ["Yangibozor", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Tuproqqal'a": ["Tuproqqal'a", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Urganch shahri": ["1-mahalla", "2-mahalla", "3-mahalla", "4-mahalla", "5-mahalla"]
    },
    "Qoraqalpog'iston": {
        "Amudaryo": ["Amudaryo", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Beruniy": ["Beruniy", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Chimboy": ["Chimboy", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Ellikqala": ["Ellikqala", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Kegeyli": ["Kegeyli", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Mo'ynoq": ["Mo'ynoq", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Nukus": ["Nukus shahri", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Qanliko'l": ["Qanliko'l", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Qo'ng'irot": ["Qo'ng'irot", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Taxiatosh": ["Taxiatosh", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "To'rtko'l": ["To'rtko'l", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"],
        "Xo'jayli": ["Xo'jayli", "Markaziy", "Yangiobod", "Bog'bon", "Tinchlik"]
    }
}

# 📌 Cache management functions
@lru_cache(maxsize=100)
def get_cached_file_data(file_path: str, cache_key: str) -> Any:
    """Cached file reading with TTL"""
    current_time = datetime.now().timestamp()
    
    # Check if cache is valid
    if cache_key in _cache_timestamps:
        if current_time - _cache_timestamps[cache_key] < FILE_CACHE_TTL:
            return _cache.get(cache_key)
    
    # Load fresh data
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        _cache[cache_key] = data
        _cache_timestamps[cache_key] = current_time
        return data
    except (json.JSONDecodeError, FileNotFoundError):
        return {} if cache_key != "results" else []

def invalidate_cache(cache_key: str):
    """Invalidate specific cache entry"""
    if cache_key in _cache:
        del _cache[cache_key]
    if cache_key in _cache_timestamps:
        del _cache_timestamps[cache_key]

# 📌 Optimized data management functions
async def load_json_data(file_path: str, default_data: Any = None) -> Any:
    """Async load data from JSON file with caching"""
    async with file_semaphore:
        cache_key = os.path.basename(file_path)
        
        if not os.path.exists(file_path):
            return default_data or ({} if cache_key != "results.json" else [])
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
                
                # Update cache
                _cache[cache_key] = data
                _cache_timestamps[cache_key] = datetime.now().timestamp()
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return default_data or ({} if cache_key != "results.json" else [])

async def save_json_data(file_path: str, data: Any) -> None:
    """Async save data to JSON file"""
    async with file_semaphore:
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            
            # Update cache
            cache_key = os.path.basename(file_path)
            _cache[cache_key] = data
            _cache_timestamps[cache_key] = datetime.now().timestamp()
        except Exception as e:
            logging.error(f"Error saving data to {file_path}: {e}")

async def get_users() -> Dict:
    """Get all registered users"""
    return await load_json_data(USERS_FILE, {})

async def save_user(user_id: str, user_data: Dict) -> None:
    """Save user data"""
    users = await get_users()
    users[user_id] = user_data
    await save_json_data(USERS_FILE, users)

async def get_admins() -> Dict:
    """Get all admins"""
    default_admins = {str(SUPER_ADMIN_ID): {"role": "super_admin", "added_by": "system", "added_date": get_uzbekistan_time().isoformat()}}
    return await load_json_data(ADMINS_FILE, default_admins)

async def save_admin(admin_id: str, admin_data: Dict) -> None:
    """Save admin data"""
    admins = await get_admins()
    admins[admin_id] = admin_data
    await save_json_data(ADMINS_FILE, admins)

async def remove_admin(admin_id: str) -> bool:
    """Remove admin by ID"""
    try:
        admins = await get_admins()
        if admin_id in admins:
            del admins[admin_id]
            await save_json_data(ADMINS_FILE, admins)
            return True
        return False
    except Exception as e:
        logging.error(f"Error removing admin data: {e}")
        return False

async def get_tests() -> Dict:
    """Get all tests"""
    return await load_json_data(TESTS_FILE, {"7-10": {}, "11-14": {}})

async def save_test(test_data: Dict) -> None:
    """Save test data"""
    tests = await get_tests()
    age_group = test_data["age_group"]
    test_id = str(uuid.uuid4())
    
    if age_group not in tests:
        tests[age_group] = {}
    
    tests[age_group][test_id] = test_data
    await save_json_data(TESTS_FILE, tests)

async def get_results() -> List:
    """Get all test results"""
    return await load_json_data(RESULTS_FILE, [])

async def save_result(result_data: Dict) -> None:
    """Save test result"""
    results = await get_results()
    results.append(result_data)
    await save_json_data(RESULTS_FILE, results)

async def get_broadcasts() -> List:
    """Get all broadcast history"""
    return await load_json_data(BROADCASTS_FILE, [])

async def save_broadcast(broadcast_data: Dict) -> None:
    """Save broadcast data"""
    broadcasts = await get_broadcasts()
    broadcasts.append(broadcast_data)
    await save_json_data(BROADCASTS_FILE, broadcasts)

async def get_statistics() -> Dict:
    """Get statistics data"""
    return await load_json_data(STATISTICS_FILE, {})

async def update_statistics() -> None:
    """Update comprehensive statistics"""
    users = await get_users()
    results = await get_results()
    
    # Regional statistics
    regional_stats = {}
    for region, districts in REGIONS.items():
        regional_stats[region] = {
            "total_users": 0,
            "districts": {}
        }
        
        for district in districts.keys():
            regional_stats[region]["districts"][district] = 0
    
    # Count users by region and district
    for user_data in users.values():
        region = user_data.get("region", "Unknown")
        district = user_data.get("district", "Unknown")
        
        if region in regional_stats:
            regional_stats[region]["total_users"] += 1
            if district in regional_stats[region]["districts"]:
                regional_stats[region]["districts"][district] += 1
    
    # Test statistics
    test_stats = {
        "total_tests_taken": len(results),
        "average_score": 0,
        "high_scorers_70plus": 0,
        "age_group_stats": {
            "7-10": {"count": 0, "avg_score": 0},
            "11-14": {"count": 0, "avg_score": 0}
        }
    }
    
    if results:
        total_score = sum(result.get("score", 0) for result in results)
        test_stats["average_score"] = round(total_score / len(results), 2)
        test_stats["high_scorers_70plus"] = len([r for r in results if r.get("score", 0) >= 70])
        
        # Age group statistics
        age_7_10 = [r for r in results if r.get("age") in ["7", "8", "9", "10"]]
        age_11_14 = [r for r in results if r.get("age") in ["11", "12", "13", "14"]]
        
        if age_7_10:
            test_stats["age_group_stats"]["7-10"]["count"] = len(age_7_10)
            test_stats["age_group_stats"]["7-10"]["avg_score"] = round(
                sum(r.get("score", 0) for r in age_7_10) / len(age_7_10), 2
            )
        
        if age_11_14:
            test_stats["age_group_stats"]["11-14"]["count"] = len(age_11_14)
            test_stats["age_group_stats"]["11-14"]["avg_score"] = round(
                sum(r.get("score", 0) for r in age_11_14) / len(age_11_14), 2
            )
    
    # Top performers ranking
    ranking_data = []
    for result in results:
        ranking_data.append({
            "user_name": result.get("user_name", "Unknown"),
            "score": result.get("score", 0),
            "percentage": result.get("percentage", 0),
            "age": result.get("age", "Unknown"),
            "region": result.get("region", "Unknown"),
            "date": result.get("date", "Unknown")
        })
    
    # Sort by score (descending)
    ranking_data.sort(key=lambda x: x["score"], reverse=True)
    
    statistics = {
        "last_updated": get_uzbekistan_time().isoformat(),
        "total_registered_users": len(users),
        "regional_statistics": regional_stats,
        "test_statistics": test_stats,
        "top_performers": ranking_data[:100]  # Top 100 performers
    }
    
    await save_json_data(STATISTICS_FILE, statistics)

async def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    admins = await get_admins()
    return str(user_id) in admins

async def is_super_admin(user_id: int) -> bool:
    """Check if user is super admin"""
    admins = await get_admins()
    return str(user_id) in admins and admins[str(user_id)].get("role") == "super_admin"

def has_special_privileges(user_id: int) -> bool:
    """Check if user has special admin privileges"""
    return user_id in SPECIAL_ADMIN_IDS

# 📌 FSM States
class Registration(StatesGroup):
    check_subscription = State()
    child_name = State()
    parent_name = State()
    region = State()
    district = State()
    mahalla = State()
    manual_mahalla = State()
    age = State()
    phone = State()
    feedback = State()

class AdminStates(StatesGroup):
    add_admin = State()
    remove_admin = State()
    promote_super_admin = State()
    add_test_age = State()
    add_test_book = State()
    add_test_content = State()
    add_test_questions = State()
    delete_test_age = State()
    delete_test_select = State()
    broadcast_message = State()
    broadcast_confirm = State()
    view_statistics = State()
    view_rankings = State()

class TestStates(StatesGroup):
    taking_test = State()
    test_question = State()

# 📌 Keyboards
def get_main_menu():
    """Main menu keyboard"""
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📋 Ro'yxatdan o'tish")],
        [KeyboardButton(text="📝 Test topshirish")],
        [KeyboardButton(text="💬 Fikr va maslahatlar")],
        [KeyboardButton(text="📚 Loyiha haqida")]
    ], resize_keyboard=True)

def get_admin_menu(is_super: bool = False):
    """Admin menu keyboard"""
    keyboard = [
        [KeyboardButton(text="👥 Foydalanuvchilar ro'yxati")],
        [KeyboardButton(text="➕ Test qo'shish")]
    ]
    
    if is_super:
        keyboard.extend([
            [KeyboardButton(text="👨‍💼 Adminlar ro'yxati")],
            [KeyboardButton(text="➕ Admin qo'shish")],
            [KeyboardButton(text="⬆️ Super Admin tayinlash")],
            [KeyboardButton(text="➖ Admin o'chirish")],
            [KeyboardButton(text="🗑 Test o'chirish")],
            [KeyboardButton(text="📊 Statistikalar")],
            [KeyboardButton(text="📢 Xabar yuborish")]
        ])
    
    keyboard.append([KeyboardButton(text="🔙 Asosiy menyu")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_region_keyboard():
    """Region selection keyboard"""
    keyboard = []
    for region in REGIONS.keys():
        keyboard.append([KeyboardButton(text=region)])
    
    keyboard.append([KeyboardButton(text="🔙 Orqaga")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_district_keyboard(region: str):
    """District selection keyboard"""
    keyboard = []
    if region in REGIONS:
        for district in REGIONS[region].keys():
            keyboard.append([KeyboardButton(text=district)])
    
    keyboard.append([KeyboardButton(text="🔙 Orqaga")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_mahalla_keyboard(region: str, district: str):
    """Mahalla selection keyboard with manual entry option"""
    keyboard = []
    if region in REGIONS and district in REGIONS[region]:
        for mahalla in REGIONS[region][district]:
            keyboard.append([KeyboardButton(text=mahalla)])
    
    keyboard.append([KeyboardButton(text="✏️ Qo'lda kiritish")])
    keyboard.append([KeyboardButton(text="🔙 Orqaga")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_age_keyboard():
    """Age selection keyboard"""
    keyboard = []
    for age in range(7, 15):
        keyboard.append([KeyboardButton(text=str(age))])
    
    keyboard.append([KeyboardButton(text="🔙 Orqaga")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_test_keyboard(age_group: str):
    """Test selection keyboard"""
    keyboard = []
    keyboard.append([KeyboardButton(text=f"{age_group} yosh test")])
    keyboard.append([KeyboardButton(text="🔙 Orqaga")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# 📌 Start handler
@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Check if user is admin
    is_user_admin = await is_admin(user_id)
    is_user_super_admin = await is_super_admin(user_id)
    
    if is_user_admin:
        menu = get_admin_menu(is_user_super_admin)
        welcome_text = "👨‍💼 Admin paneliga xush kelibsiz!"
    else:
        menu = get_main_menu()
        welcome_text = f"""🌟 <b>Kitobxon Kids</b> botiga xush kelibsiz!

👋 Assalomu alaykum, {message.from_user.first_name}!

Bu bot orqali siz:
📋 Ro'yxatdan o'tishingiz
📝 Testlarni topshirishingiz
📊 Natijalarni ko'rishingiz mumkin

Boshlash uchun quyidagi tugmalardan birini tanlang 👇"""
    
    await message.answer(welcome_text, reply_markup=menu)
    await state.clear()

# 📌 Registration handlers
@dp.message(F.text == "📋 Ro'yxatdan o'tish")
async def registration_start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    users = await get_users()
    
    if user_id in users:
        await message.answer("Siz allaqachon ro'yxatdan o'tgansiz! ✅", reply_markup=get_main_menu())
        return
    
    await message.answer(
        f"""📋 <b>Ro'yxatdan o'tish</b>

Iltimos, {CHANNEL_USERNAME} kanaliga obuna bo'ling va "Obuna bo'ldim" tugmasini bosing.

Obuna bo'lmasdan test topshira olmaysiz.""",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="✅ Obuna bo'ldim")],
            [KeyboardButton(text="🔙 Orqaga")]
        ], resize_keyboard=True)
    )
    await state.set_state(Registration.check_subscription)

@dp.message(Registration.check_subscription, F.text == "✅ Obuna bo'ldim")
async def check_subscription(message: types.Message, state: FSMContext):
    try:
        # Get user's subscription status
        user_channel_status = await bot.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
        if user_channel_status.status in ['member', 'administrator', 'creator']:
            await message.answer(
                "👶 Bolangizning to'liq ismini kiriting:",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    [KeyboardButton(text="🔙 Orqaga")]
                ], resize_keyboard=True)
            )
            await state.set_state(Registration.child_name)
        else:
            await message.answer("❌ Siz hali kanalga obuna bo'lmagansiz. Iltimos, avval obuna bo'ling!")
    except Exception:
        # If can't check subscription, proceed anyway
        await message.answer(
            "👶 Bolangizning to'liq ismini kiriting:",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text="🔙 Orqaga")]
            ], resize_keyboard=True)
        )
        await state.set_state(Registration.child_name)

@dp.message(Registration.child_name)
async def get_child_name(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Asosiy menyu:", reply_markup=get_main_menu())
        await state.clear()
        return
    
    await state.update_data(child_name=message.text)
    await message.answer(
        "👨‍👩‍👧‍👦 Ota-onaning to'liq ismini kiriting:",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="🔙 Orqaga")]
        ], resize_keyboard=True)
    )
    await state.set_state(Registration.parent_name)

@dp.message(Registration.parent_name)
async def get_parent_name(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.set_state(Registration.child_name)
        await message.answer("👶 Bolangizning to'liq ismini kiriting:")
        return
    
    await state.update_data(parent_name=message.text)
    await message.answer(
        "🗺 Viloyatingizni tanlang:",
        reply_markup=get_region_keyboard()
    )
    await state.set_state(Registration.region)

@dp.message(Registration.region)
async def get_region(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.set_state(Registration.parent_name)
        await message.answer("👨‍👩‍👧‍👦 Ota-onaning to'liq ismini kiriting:")
        return
    
    if message.text not in REGIONS:
        await message.answer("❌ Iltimos, ro'yxatdan viloyat tanlang!")
        return
    
    await state.update_data(region=message.text)
    await message.answer(
        "🏘 Tumaningizni tanlang:",
        reply_markup=get_district_keyboard(message.text)
    )
    await state.set_state(Registration.district)

@dp.message(Registration.district)
async def get_district(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.set_state(Registration.region)
        await message.answer("🗺 Viloyatingizni tanlang:", reply_markup=get_region_keyboard())
        return
    
    data = await state.get_data()
    region = data.get("region")
    
    if not region or region not in REGIONS or message.text not in REGIONS[region]:
        await message.answer("❌ Iltimos, ro'yxatdan tuman tanlang!")
        return
    
    await state.update_data(district=message.text)
    await message.answer(
        "🏠 Mahallangizni tanlang:",
        reply_markup=get_mahalla_keyboard(region, message.text)
    )
    await state.set_state(Registration.mahalla)

@dp.message(Registration.mahalla)
async def get_mahalla(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        data = await state.get_data()
        region = data.get("region")
        await state.set_state(Registration.district)
        await message.answer("🏘 Tumaningizni tanlang:", reply_markup=get_district_keyboard(region))
        return
    
    if message.text == "✏️ Qo'lda kiritish":
        await message.answer(
            "✏️ Mahalla nomini qo'lda kiriting:",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text="🔙 Orqaga")]
            ], resize_keyboard=True)
        )
        await state.set_state(Registration.manual_mahalla)
        return
    
    data = await state.get_data()
    region = data.get("region")
    district = data.get("district")
    
    if (region and district and region in REGIONS and 
        district in REGIONS[region] and 
        message.text not in REGIONS[region][district]):
        await message.answer("❌ Iltimos, ro'yxatdan mahalla tanlang yoki 'Qo'lda kiritish' tugmasini bosing!")
        return
    
    await state.update_data(mahalla=message.text)
    await message.answer(
        "🎂 Bolangizning yoshini tanlang:",
        reply_markup=get_age_keyboard()
    )
    await state.set_state(Registration.age)

@dp.message(Registration.manual_mahalla)
async def get_manual_mahalla(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        data = await state.get_data()
        region = data.get("region")
        district = data.get("district")
        await state.set_state(Registration.mahalla)
        await message.answer("🏠 Mahallangizni tanlang:", reply_markup=get_mahalla_keyboard(region, district))
        return
    
    await state.update_data(mahalla=message.text)
    await message.answer(
        "🎂 Bolangizning yoshini tanlang:",
        reply_markup=get_age_keyboard()
    )
    await state.set_state(Registration.age)

@dp.message(Registration.age)
async def get_age(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        data = await state.get_data()
        region = data.get("region")
        district = data.get("district")
        await state.set_state(Registration.mahalla)
        await message.answer("🏠 Mahallangizni tanlang:", reply_markup=get_mahalla_keyboard(region, district))
        return
    
    try:
        age = int(message.text)
        if age < 7 or age > 14:
            await message.answer("❌ Yosh 7 dan 14 gacha bo'lishi kerak!")
            return
    except ValueError:
        await message.answer("❌ Iltimos, to'g'ri yosh kiriting!")
        return
    
    await state.update_data(age=message.text)
    await message.answer(
        "📱 Telefon raqamingizni kiriting (+998901234567):",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📱 Kontaktni ulashish", request_contact=True)],
            [KeyboardButton(text="🔙 Orqaga")]
        ], resize_keyboard=True)
    )
    await state.set_state(Registration.phone)

@dp.message(Registration.phone)
async def get_phone(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.set_state(Registration.age)
        await message.answer("🎂 Bolangizning yoshini tanlang:", reply_markup=get_age_keyboard())
        return
    
    phone = None
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text
    
    if not phone:
        await message.answer("❌ Iltimos, telefon raqamini kiriting!")
        return
    
    # Save user data
    data = await state.get_data()
    user_data = {
        "child_name": data.get("child_name"),
        "parent_name": data.get("parent_name"),
        "region": data.get("region"),
        "district": data.get("district"),
        "mahalla": data.get("mahalla"),
        "age": data.get("age"),
        "phone": phone,
        "telegram_id": message.from_user.id,
        "username": message.from_user.username or "No username",
        "registration_date": get_uzbekistan_time().isoformat()
    }
    
    await save_user(str(message.from_user.id), user_data)
    await update_statistics()
    
    await message.answer(
        "✅ <b>Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!</b>\n\n"
        "Endi siz testlarni topshirishingiz mumkin.\n\n"
        "📝 Test topshirish uchun tegishli tugmani bosing.",
        reply_markup=get_main_menu()
    )
    await state.clear()

# 📌 Test handlers
@dp.message(F.text == "📝 Test topshirish")
async def test_start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    users = await get_users()
    
    if user_id not in users:
        await message.answer(
            "❌ Avval ro'yxatdan o'ting!",
            reply_markup=get_main_menu()
        )
        return
    
    user_age = int(users[user_id]["age"])
    age_group = "7-10" if user_age <= 10 else "11-14"
    
    tests = await get_tests()
    if age_group not in tests or not tests[age_group]:
        await message.answer(
            f"❌ {age_group} yosh guruhi uchun testlar mavjud emas.",
            reply_markup=get_main_menu()
        )
        return
    
    # Show available tests
    keyboard = []
    for test_id, test_data in tests[age_group].items():
        keyboard.append([InlineKeyboardButton(
            text=f"📖 {test_data.get('book_name', 'Test')}",
            callback_data=f"take_test:{test_id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")])
    
    await message.answer(
        f"📝 <b>{age_group} yosh uchun mavjud testlar:</b>\n\n"
        "Test tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@dp.callback_query(F.data.startswith("take_test:"))
async def start_test(callback: types.CallbackQuery, state: FSMContext):
    test_id = callback.data.split(":")[1]
    tests = await get_tests()
    
    # Find test
    test_data = None
    for age_group in tests:
        if test_id in tests[age_group]:
            test_data = tests[age_group][test_id]
            break
    
    if not test_data:
        await callback.answer("❌ Test topilmadi!")
        return
    
    questions = test_data.get("questions", [])
    if not questions:
        await callback.answer("❌ Testda savollar mavjud emas!")
        return
    
    await state.update_data(
        test_id=test_id,
        test_data=test_data,
        questions=questions,
        current_question=0,
        answers=[],
        start_time=get_uzbekistan_time().isoformat()
    )
    
    # Show first question
    question = questions[0]
    keyboard = []
    for option in ["A", "B", "C", "D"]:
        keyboard.append([InlineKeyboardButton(
            text=f"{option}) {question.get(option, '')}",
            callback_data=f"answer:{option}"
        )])
    
    await callback.message.edit_text(
        f"📚 <b>{test_data.get('book_name', 'Test')}</b>\n\n"
        f"❓ <b>Savol 1/{len(questions)}:</b>\n\n"
        f"{question.get('question', '')}\n\n"
        f"Javobni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await state.set_state(TestStates.test_question)

@dp.callback_query(F.data.startswith("answer:"), TestStates.test_question)
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    answer = callback.data.split(":")[1]
    data = await state.get_data()
    
    questions = data["questions"]
    current_q = data["current_question"]
    answers = data["answers"]
    
    # Save answer
    answers.append(answer)
    await state.update_data(answers=answers)
    
    # Check if test is complete
    if current_q + 1 >= len(questions):
        # Calculate score
        correct_answers = 0
        for i, user_answer in enumerate(answers):
            if i < len(questions) and questions[i].get("correct") == user_answer:
                correct_answers += 1
        
        score = correct_answers
        percentage = round((correct_answers / len(questions)) * 100, 2)
        
        # Save result
        user_id = str(callback.from_user.id)
        users = await get_users()
        user_data = users.get(user_id, {})
        
        result_data = {
            "user_id": user_id,
            "user_name": user_data.get("child_name", "Unknown"),
            "test_id": data["test_id"],
            "test_name": data["test_data"].get("book_name", "Test"),
            "score": score,
            "total_questions": len(questions),
            "percentage": percentage,
            "answers": answers,
            "correct_answers": [q.get("correct") for q in questions],
            "age": user_data.get("age", "Unknown"),
            "region": user_data.get("region", "Unknown"),
            "district": user_data.get("district", "Unknown"),
            "date": get_uzbekistan_time().isoformat(),
            "start_time": data.get("start_time"),
            "end_time": get_uzbekistan_time().isoformat()
        }
        
        await save_result(result_data)
        await update_statistics()
        
        # Show result
        status = "🎉 A'lo!" if percentage >= 90 else "👍 Yaxshi!" if percentage >= 70 else "📖 Ko'proq o'qing!"
        
        await callback.message.edit_text(
            f"✅ <b>Test yakunlandi!</b>\n\n"
            f"📊 <b>Natijangiz:</b>\n"
            f"• To'g'ri javoblar: {correct_answers}/{len(questions)}\n"
            f"• Foiz: {percentage}%\n"
            f"• Baho: {status}\n\n"
            f"📚 Test nomi: {data['test_data'].get('book_name', 'Test')}\n\n"
            f"Boshqa testlarni ham topshirishingiz mumkin!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main")]
            ])
        )
        await state.clear()
        return
    
    # Show next question
    next_q = current_q + 1
    await state.update_data(current_question=next_q)
    
    question = questions[next_q]
    keyboard = []
    for option in ["A", "B", "C", "D"]:
        keyboard.append([InlineKeyboardButton(
            text=f"{option}) {question.get(option, '')}",
            callback_data=f"answer:{option}"
        )])
    
    await callback.message.edit_text(
        f"📚 <b>{data['test_data'].get('book_name', 'Test')}</b>\n\n"
        f"❓ <b>Savol {next_q + 1}/{len(questions)}:</b>\n\n"
        f"{question.get('question', '')}\n\n"
        f"Javobni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

# 📌 Admin handlers
@dp.message(F.text == "👥 Foydalanuvchilar ro'yxati")
async def admin_users_list(message: types.Message):
    if not await is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqlari yo'q!")
        return
    
    users = await get_users()
    if not users:
        await message.answer("📝 Hozircha foydalanuvchilar yo'q.")
        return
    
    # Create Excel file
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Foydalanuvchilar"
        
        # Headers
        headers = [
            "ID", "Bola ismi", "Ota-ona ismi", "Viloyat", "Tuman", 
            "Mahalla", "Yosh", "Telefon", "Username", "Ro'yxatdan o'tgan sana"
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        # Data
        for row, (user_id, user_data) in enumerate(users.items(), 2):
            ws.cell(row=row, column=1, value=user_id)
            ws.cell(row=row, column=2, value=user_data.get("child_name", ""))
            ws.cell(row=row, column=3, value=user_data.get("parent_name", ""))
            ws.cell(row=row, column=4, value=user_data.get("region", ""))
            ws.cell(row=row, column=5, value=user_data.get("district", ""))
            ws.cell(row=row, column=6, value=user_data.get("mahalla", ""))
            ws.cell(row=row, column=7, value=user_data.get("age", ""))
            ws.cell(row=row, column=8, value=user_data.get("phone", ""))
            ws.cell(row=row, column=9, value=user_data.get("username", ""))
            ws.cell(row=row, column=10, value=user_data.get("registration_date", ""))
        
        # Auto-adjust columns
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save to bytes
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Send file
        document = BufferedInputFile(
            output.getvalue(),
            filename=f"foydalanuvchilar_{get_uzbekistan_time().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        await message.answer_document(
            document=document,
            caption=f"📊 <b>Foydalanuvchilar ro'yxati</b>\n\n"
                   f"Jami: {len(users)} ta foydalanuvchi\n"
                   f"Sana: {get_uzbekistan_time().strftime('%d.%m.%Y %H:%M')}"
        )
        
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")

@dp.message(F.text == "➕ Admin qo'shish")
async def admin_add_start(message: types.Message, state: FSMContext):
    if not await is_super_admin(message.from_user.id):
        await message.answer("❌ Sizda super admin huquqlari yo'q!")
        return
    
    await message.answer(
        "👤 Yangi admin qo'shish uchun uning Telegram ID raqamini kiriting:",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="🔙 Orqaga")]
        ], resize_keyboard=True)
    )
    await state.set_state(AdminStates.add_admin)

@dp.message(AdminStates.add_admin)
async def admin_add_process(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Admin menyu:", reply_markup=get_admin_menu(True))
        await state.clear()
        return
    
    try:
        admin_id = int(message.text)
        admin_id_str = str(admin_id)
        
        admins = await get_admins()
        if admin_id_str in admins:
            await message.answer("❌ Bu foydalanuvchi allaqachon admin!")
            return
        
        # Add as regular admin
        admin_data = {
            "role": "admin",
            "added_by": str(message.from_user.id),
            "added_date": get_uzbekistan_time().isoformat()
        }
        
        await save_admin(admin_id_str, admin_data)
        
        await message.answer(
            f"✅ Foydalanuvchi {admin_id} admin qilib tayinlandi!",
            reply_markup=get_admin_menu(True)
        )
        await state.clear()
        
    except ValueError:
        await message.answer("❌ To'g'ri Telegram ID kiriting!")

@dp.message(F.text == "⬆️ Super Admin tayinlash")
async def promote_super_admin_start(message: types.Message, state: FSMContext):
    if not has_special_privileges(message.from_user.id):
        await message.answer("❌ Faqat maxsus huquqli adminlar super admin tayinlay oladi!")
        return
    
    await message.answer(
        "👑 Super admin tayinlash uchun Telegram ID raqamini kiriting:",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="🔙 Orqaga")]
        ], resize_keyboard=True)
    )
    await state.set_state(AdminStates.promote_super_admin)

@dp.message(AdminStates.promote_super_admin)
async def promote_super_admin_process(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Admin menyu:", reply_markup=get_admin_menu(True))
        await state.clear()
        return
    
    try:
        admin_id = int(message.text)
        admin_id_str = str(admin_id)
        
        # Add/update as super admin
        admin_data = {
            "role": "super_admin",
            "added_by": str(message.from_user.id),
            "added_date": get_uzbekistan_time().isoformat()
        }
        
        await save_admin(admin_id_str, admin_data)
        
        await message.answer(
            f"✅ Foydalanuvchi {admin_id} super admin qilib tayinlandi!",
            reply_markup=get_admin_menu(True)
        )
        await state.clear()
        
    except ValueError:
        await message.answer("❌ To'g'ri Telegram ID kiriting!")

@dp.message(F.text == "➖ Admin o'chirish")
async def admin_remove_start(message: types.Message, state: FSMContext):
    if not await is_super_admin(message.from_user.id):
        await message.answer("❌ Sizda super admin huquqlari yo'q!")
        return
    
    await message.answer(
        "🗑 Admin o'chirish uchun uning Telegram ID raqamini kiriting:",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="🔙 Orqaga")]
        ], resize_keyboard=True)
    )
    await state.set_state(AdminStates.remove_admin)

@dp.message(AdminStates.remove_admin)
async def admin_remove_process(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Admin menyu:", reply_markup=get_admin_menu(True))
        await state.clear()
        return
    
    try:
        admin_id = int(message.text)
        admin_id_str = str(admin_id)
        
        # Don't allow removing system admin
        if admin_id == SUPER_ADMIN_ID:
            await message.answer("❌ Tizim adminini o'chirib bo'lmaydi!")
            return
        
        if await remove_admin(admin_id_str):
            await message.answer(
                f"✅ Admin {admin_id} o'chirildi!",
                reply_markup=get_admin_menu(True)
            )
        else:
            await message.answer("❌ Bu ID admin emas!")
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ To'g'ri Telegram ID kiriting!")

@dp.message(F.text == "👨‍💼 Adminlar ro'yxati")
async def admin_list(message: types.Message):
    if not await is_super_admin(message.from_user.id):
        await message.answer("❌ Sizda super admin huquqlari yo'q!")
        return
    
    admins = await get_admins()
    if not admins:
        await message.answer("📝 Adminlar mavjud emas.")
        return
    
    text = "👨‍💼 <b>Adminlar ro'yxati:</b>\n\n"
    for admin_id, admin_data in admins.items():
        role = admin_data.get("role", "admin")
        role_emoji = "👑" if role == "super_admin" else "👤"
        added_date = admin_data.get("added_date", "Unknown")
        
        text += f"{role_emoji} <b>{admin_id}</b> - {role}\n"
        text += f"   Qo'shilgan: {added_date[:10] if added_date != 'Unknown' else 'Unknown'}\n\n"
    
    await message.answer(text)

@dp.message(F.text == "➕ Test qo'shish")
async def add_test_start(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqlari yo'q!")
        return
    
    await message.answer(
        "📚 Qaysi yosh guruhi uchun test qo'shasiz?",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="7-10 yosh")],
            [KeyboardButton(text="11-14 yosh")],
            [KeyboardButton(text="🔙 Orqaga")]
        ], resize_keyboard=True)
    )
    await state.set_state(AdminStates.add_test_age)

@dp.message(AdminStates.add_test_age)
async def add_test_age(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        is_super = await is_super_admin(message.from_user.id)
        await message.answer("Admin menyu:", reply_markup=get_admin_menu(is_super))
        await state.clear()
        return
    
    if message.text not in ["7-10 yosh", "11-14 yosh"]:
        await message.answer("❌ Iltimos, tugmalardan birini tanlang!")
        return
    
    age_group = message.text.split()[0]  # "7-10" or "11-14"
    await state.update_data(age_group=age_group)
    
    await message.answer(
        "📖 Kitob nomini kiriting:",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="🔙 Orqaga")]
        ], resize_keyboard=True)
    )
    await state.set_state(AdminStates.add_test_book)

@dp.message(AdminStates.add_test_book)
async def add_test_book(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.set_state(AdminStates.add_test_age)
        await message.answer("📚 Qaysi yosh guruhi uchun test qo'shasiz?")
        return
    
    await state.update_data(book_name=message.text)
    
    await message.answer(
        "📝 Test savollarini quyidagi formatda kiriting:\n\n"
        "Savol matni?\n"
        "A) Variant 1\n"
        "B) Variant 2\n"
        "C) Variant 3\n"
        "D) Variant 4\n"
        "Javob: A\n\n"
        "---\n\n"
        "Keyingi savol...\n\n"
        "Barcha savollarni bir xabar ichida yuboring.",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="🔙 Orqaga")]
        ], resize_keyboard=True)
    )
    await state.set_state(AdminStates.add_test_questions)

@dp.message(AdminStates.add_test_questions)
async def add_test_questions(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.set_state(AdminStates.add_test_book)
        await message.answer("📖 Kitob nomini kiriting:")
        return
    
    try:
        # Parse questions
        questions = []
        question_blocks = message.text.split("---")
        
        for block in question_blocks:
            lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
            if len(lines) < 6:  # Question + 4 options + Answer
                continue
            
            question_text = lines[0]
            options = {}
            correct_answer = None
            
            for line in lines[1:]:
                if line.startswith(('A)', 'A )')):
                    options['A'] = line[2:].strip()
                elif line.startswith(('B)', 'B )')):
                    options['B'] = line[2:].strip()
                elif line.startswith(('C)', 'C )')):
                    options['C'] = line[2:].strip()
                elif line.startswith(('D)', 'D )')):
                    options['D'] = line[2:].strip()
                elif line.lower().startswith('javob:'):
                    correct_answer = line.split(':')[1].strip().upper()
            
            if len(options) == 4 and correct_answer in ['A', 'B', 'C', 'D']:
                questions.append({
                    'question': question_text,
                    'A': options['A'],
                    'B': options['B'],
                    'C': options['C'],
                    'D': options['D'],
                    'correct': correct_answer
                })
        
        if not questions:
            await message.answer("❌ Savollar to'g'ri formatda emas! Qayta kiriting.")
            return
        
        # Save test
        data = await state.get_data()
        test_data = {
            "book_name": data["book_name"],
            "age_group": data["age_group"],
            "questions": questions,
            "created_by": str(message.from_user.id),
            "created_date": get_uzbekistan_time().isoformat()
        }
        
        await save_test(test_data)
        
        is_super = await is_super_admin(message.from_user.id)
        await message.answer(
            f"✅ Test muvaffaqiyatli qo'shildi!\n\n"
            f"📖 Kitob: {data['book_name']}\n"
            f"👥 Yosh guruhi: {data['age_group']}\n"
            f"❓ Savollar soni: {len(questions)}",
            reply_markup=get_admin_menu(is_super)
        )
        await state.clear()
        
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")

@dp.message(F.text == "📊 Statistikalar")
async def admin_statistics(message: types.Message):
    if not await is_super_admin(message.from_user.id):
        await message.answer("❌ Sizda super admin huquqlari yo'q!")
        return
    
    await update_statistics()
    stats = await get_statistics()
    
    text = "📊 <b>Bot statistikalari:</b>\n\n"
    text += f"👥 Jami foydalanuvchilar: {stats.get('total_registered_users', 0)}\n"
    text += f"📝 Topshirilgan testlar: {stats.get('test_statistics', {}).get('total_tests_taken', 0)}\n"
    text += f"📈 O'rtacha ball: {stats.get('test_statistics', {}).get('average_score', 0)}\n"
    text += f"🏆 70%+ natija: {stats.get('test_statistics', {}).get('high_scorers_70plus', 0)} ta\n\n"
    
    text += "🗺 <b>Viloyatlar bo'yicha:</b>\n"
    regional_stats = stats.get('regional_statistics', {})
    for region, data in list(regional_stats.items())[:5]:  # Show top 5
        text += f"• {region}: {data.get('total_users', 0)} ta\n"
    
    if len(regional_stats) > 5:
        text += f"• Va boshqa {len(regional_stats) - 5} ta viloyat...\n"
    
    text += f"\n🕐 Oxirgi yangilanish: {stats.get('last_updated', 'Unknown')[:16]}"
    
    await message.answer(text)

@dp.message(F.text == "📢 Xabar yuborish")
async def broadcast_start(message: types.Message, state: FSMContext):
    if not await is_super_admin(message.from_user.id):
        await message.answer("❌ Sizda super admin huquqlari yo'q!")
        return
    
    await message.answer(
        "📢 Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni kiriting:",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="🔙 Orqaga")]
        ], resize_keyboard=True)
    )
    await state.set_state(AdminStates.broadcast_message)

@dp.message(AdminStates.broadcast_message)
async def broadcast_message(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Admin menyu:", reply_markup=get_admin_menu(True))
        await state.clear()
        return
    
    await state.update_data(broadcast_text=message.text)
    
    users = await get_users()
    await message.answer(
        f"📢 Xabaringiz:\n\n{message.text}\n\n"
        f"👥 {len(users)} ta foydalanuvchiga yuboriladi.\n\n"
        f"Tasdiqlaysizmi?",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="✅ Ha, yuborish")],
            [KeyboardButton(text="❌ Yo'q, bekor qilish")]
        ], resize_keyboard=True)
    )
    await state.set_state(AdminStates.broadcast_confirm)

@dp.message(AdminStates.broadcast_confirm)
async def broadcast_confirm(message: types.Message, state: FSMContext):
    if message.text == "❌ Yo'q, bekor qilish":
        await message.answer("❌ Xabar yuborish bekor qilindi.", reply_markup=get_admin_menu(True))
        await state.clear()
        return
    
    if message.text != "✅ Ha, yuborish":
        await message.answer("❌ Iltimos, tugmalardan birini tanlang!")
        return
    
    data = await state.get_data()
    broadcast_text = data["broadcast_text"]
    
    users = await get_users()
    success_count = 0
    fail_count = 0
    
    status_message = await message.answer("📤 Xabar yuborilmoqda...")
    
    # Send in batches to avoid rate limits
    async with broadcast_semaphore:
        for i, user_id in enumerate(users.keys()):
            try:
                await bot.send_message(int(user_id), f"📢 <b>Kitobxon Kids jamoasidan xabar:</b>\n\n{broadcast_text}")
                success_count += 1
            except Exception as e:
                fail_count += 1
                logging.warning(f"Failed to send message to {user_id}: {e}")
            
            # Update status every 10 users
            if (i + 1) % 10 == 0:
                try:
                    await status_message.edit_text(
                        f"📤 Yuborilmoqda... {i + 1}/{len(users)}\n"
                        f"✅ Muvaffaqiyatli: {success_count}\n"
                        f"❌ Xatolik: {fail_count}"
                    )
                except:
                    pass
    
    # Save broadcast record
    broadcast_data = {
        "message": broadcast_text,
        "sent_by": str(message.from_user.id),
        "sent_date": get_uzbekistan_time().isoformat(),
        "total_users": len(users),
        "success_count": success_count,
        "fail_count": fail_count
    }
    await save_broadcast(broadcast_data)
    
    await status_message.edit_text(
        f"✅ <b>Xabar yuborish yakunlandi!</b>\n\n"
        f"👥 Jami: {len(users)} ta foydalanuvchi\n"
        f"✅ Yuborildi: {success_count} ta\n"
        f"❌ Xatolik: {fail_count} ta"
    )
    
    await message.answer("Admin menyu:", reply_markup=get_admin_menu(True))
    await state.clear()

# 📌 Other handlers
@dp.message(F.text == "💬 Fikr va maslahatlar")
async def feedback_start(message: types.Message, state: FSMContext):
    await message.answer(
        "💬 Sizning fikr va maslahatlaringiz biz uchun muhim!\n\n"
        "Iltimos, o'z fikringizni yozing:",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="🔙 Orqaga")]
        ], resize_keyboard=True)
    )
    await state.set_state(Registration.feedback)

@dp.message(Registration.feedback)
async def feedback_process(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Asosiy menyu:", reply_markup=get_main_menu())
        await state.clear()
        return
    
    # Send feedback to admins
    admins = await get_admins()
    feedback_text = (
        f"💬 <b>Yangi fikr-mulohaza!</b>\n\n"
        f"👤 Foydalanuvchi: {message.from_user.first_name} ({message.from_user.id})\n"
        f"📝 Xabar: {message.text}\n"
        f"🕐 Vaqt: {get_uzbekistan_time().strftime('%d.%m.%Y %H:%M')}"
    )
    
    for admin_id in admins.keys():
        try:
            await bot.send_message(int(admin_id), feedback_text)
        except:
            pass
    
    await message.answer(
        "✅ Fikringiz qabul qilindi! Rahmat!\n\n"
        "Tez orada ko'rib chiqamiz.",
        reply_markup=get_main_menu()
    )
    await state.clear()

@dp.message(F.text == "📚 Loyiha haqida")
async def about_project(message: types.Message):
    text = """📚 <b>Kitobxon Kids loyihasi haqida</b>

🎯 <b>Maqsad:</b>
7-14 yosh oralig'idagi bolalarning kitob o'qish qobiliyatini rivojlantirish va baholash

📋 <b>Imkoniyatlar:</b>
• Yosh guruhiga mos testlar
• Natijalarni kuzatish
• Sertifikat olish
• Statistikalarni ko'rish

👥 <b>Yosh guruhlari:</b>
• 7-10 yosh: Boshlang'ich daraja
• 11-14 yosh: O'rta daraja

📞 <b>Aloqa:</b>
Savol va takliflar uchun: {CHANNEL_USERNAME}

💡 <b>Maslahat:</b>
Ko'proq kitob o'qing va testlarni muntazam topshiring!"""
    
    await message.answer(text)

@dp.message(F.text.in_(["🔙 Asosiy menyu", "🔙 Orqaga"]))
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    
    user_id = message.from_user.id
    is_user_admin = await is_admin(user_id)
    is_user_super_admin = await is_super_admin(user_id)
    
    if is_user_admin:
        menu = get_admin_menu(is_user_super_admin)
        text = "👨‍💼 Admin paneli"
    else:
        menu = get_main_menu()
        text = "🏠 Asosiy menyu"
    
    await message.answer(text, reply_markup=menu)

@dp.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    user_id = callback.from_user.id
    is_user_admin = await is_admin(user_id)
    is_user_super_admin = await is_super_admin(user_id)
    
    if is_user_admin:
        menu = get_admin_menu(is_user_super_admin)
        text = "👨‍💼 Admin paneli"
    else:
        menu = get_main_menu()
        text = "🏠 Asosiy menyu"
    
    await callback.message.edit_text(text)
    await callback.message.answer("Menyu:", reply_markup=menu)

# 📌 Main function
async def main():
    """Main function to start the bot"""
    logging.info("Starting Kitobxon Kids Bot...")
    
    # Initialize bot data
    await update_statistics()
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
