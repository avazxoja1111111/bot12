#!/usr/bin/env python3
"""
Configuration module for Kitobxon Kids Educational Bot
Contains all configuration constants, regional data, and system settings
"""

import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════════
# CORE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════════

# Bot token from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Super admin user ID
SUPER_ADMIN_ID = int(os.getenv("SUPER_ADMIN_ID", "6578706277"))

# Data directory
DATA_DIR = Path("bot_data")

# Performance configuration
MAX_CONCURRENT_USERS = 10000
CONNECTION_POOL_SIZE = 100
CONNECTION_PER_HOST = 30
REQUEST_TIMEOUT = 30
CACHE_TIMEOUT = 300  # 5 minutes

# File size limits
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
MAX_TEXT_LENGTH = 10000

# ═══════════════════════════════════════════════════════════════════════════════════
# REGIONAL DATA FOR UZBEKISTAN
# ═══════════════════════════════════════════════════════════════════════════════════

REGIONS_DATA = {
    "Toshkent shahri": {
        "Bektemir": ["Kuyluk", "Sarabon", "Bunyodkor", "Quyosh", "Guliston"],
        "Chilonzor": ["Chilonzor", "Kimyogarlar", "Namuna", "Chilonzor-1", "Chilonzor-2"],
        "Mirobod": ["Mirobod", "Ulugbek", "Makhmudov", "Markaziy", "Sharq"],
        "Mirzo Ulugbek": ["Qoraqamish", "Beruni", "Maksim Gorkiy", "Ibn Sino", "Nurafshon"],
        "Olmazar": ["Olmazar", "Mavlon Qori", "Bobur", "Farobiy", "Tinchlik"],
        "Sergeli": ["Sergeli", "Qipchoq", "Yangi Sergeli", "Dustlik", "Mehnat"],
        "Shayhontohur": ["Shayhontohur", "Berdaq", "Pakhtakor", "Markaziy", "Yangi Hayot"],
        "Uchtepa": ["Uchtepa", "Kukcha", "Qadamjoy", "Bog'ishamol", "Gulshan"],
        "Yakkasaroy": ["Yakkasaroy", "Kucha", "Vodnik", "Markaziy", "Parkent"],
        "Yashnobod": ["Yashnobod", "Shifokor", "Muqimiy", "Navoi", "Istiqlol"],
        "Yunusobod": ["Yunusobod", "Buyuk Ipak Yoli", "Bobur", "Amir Temur", "Mustaqillik"],
        "Yashil": ["Yashil", "Doston", "Temur Malik", "Bog'bon", "Tinchlik"]
    },
    "Andijon": {
        "Andijon shahri": ["Markaziy", "Sharqiy", "Shimoliy", "G'arbiy", "Janubiy"],
        "Asaka": ["Asaka", "Kasr", "Navoiy", "Guliston", "Mustaqillik"],
        "Baliqchi": ["Baliqchi", "Yangiqishloq", "Qoraqum", "Bog'bon", "Tinchlik"],
        "Bo'z": ["Bo'z", "Xonobod", "Yangi Hayot", "Istiqlol", "Mehnat"],
        "Buloqboshi": ["Buloqboshi", "Tinchlik", "Mustaqillik", "Gulistan", "Navoi"],
        "Izboskan": ["Izboskan", "Markaziy", "Qishloq", "Dustlik", "Yangiobod"],
        "Jalaquduq": ["Jalaquduq", "Bog'ishamol", "Gulzor", "Mehnat", "Istiqlol"],
        "Marhamat": ["Marhamat", "Yangi Marhamat", "Guliston", "Tinchlik", "Navoi"],
        "Oltinko'l": ["Oltinko'l", "Markaziy", "Bog'bon", "Dustlik", "Yangiariq"],
        "Paxtaobod": ["Paxtaobod", "Gulistan", "Mehnat", "Istiqlol", "Navoi"],
        "Paytug'": ["Paytug'", "Markaziy", "Yangiqishloq", "Bog'bon", "Tinchlik"],
        "Qo'rg'ontepa": ["Qo'rg'ontepa", "Gulzor", "Dustlik", "Yangiobod", "Mehnat"],
        "Shahriston": ["Shahriston", "Markaziy", "Bog'ishamol", "Gulistan", "Navoi"],
        "Xo'jaobod": ["Xo'jaobod", "Yangiariq", "Tinchlik", "Istiqlol", "Mehnat"]
    },
    "Buxoro": {
        "Buxoro shahri": ["Abu Ali ibn Sino", "Ismoil Somoniy", "Markaziy", "Sharq", "G'arb"],
        "Kogon": ["Kogon", "Dustlik", "Yangi Hayot", "Gulistan", "Navoi"],
        "Olot": ["Olot", "Tinchlik", "Guliston", "Bog'bon", "Mehrat"],
        "Peshku": ["Peshku", "Bog'bon", "Yangiariq", "Dustlik", "Istiqlol"],
        "Qorako'l": ["Qorako'l", "Samarkand", "Istiqlol", "Gulzor", "Navoi"],
        "Buxoro tumani": ["Markaziy", "Yangiqishloq", "Bog'ishamol", "Gulistan", "Dustlik"],
        "G'ijduvon": ["G'ijduvon", "Markaziy", "Bog'bon", "Tinchlik", "Yangiariq"],
        "Jondor": ["Jondor", "Gulzor", "Mehnat", "Istiqlol", "Navoi"],
        "Qorovulbozor": ["Qorovulbozor", "Bog'ishamol", "Dustlik", "Gulistan", "Tinchlik"],
        "Romitan": ["Romitan", "Markaziy", "Yangiariq", "Bog'bon", "Mehrat"],
        "Shofirkon": ["Shofirkon", "Gulzor", "Istiqlol", "Navoi", "Dustlik"],
        "Vobkent": ["Vobkent", "Bog'ishamol", "Gulistan", "Tinchlik", "Yangiariq"]
    },
    "Jizzax": {
        "Jizzax shahri": ["Markaziy", "Istiqlol", "Mustaqillik", "Sharq", "G'arb"],
        "Arnasoy": ["Arnasoy", "Tinchlik", "Yangiyer", "Bog'bon", "Gulzor"],
        "Baxtiyor": ["Baxtiyor", "Guliston", "Mehnat", "Dustlik", "Navoi"],
        "Do'stlik": ["Do'stlik", "Yangi Hayot", "Bog'bon", "Istiqlol", "Tinchlik"],
        "Forish": ["Forish", "Qizilcha", "Yangiqishloq", "Gulzor", "Mehrat"],
        "Baxmal": ["Baxmal", "Markaziy", "Bog'ishamol", "Dustlik", "Yangiariq"],
        "Chiroqchi": ["Chiroqchi", "Gulistan", "Tinchlik", "Navoi", "Istiqlol"],
        "G'allaorol": ["G'allaorol", "Bog'bon", "Mehrat", "Gulzor", "Dustlik"],
        "Zafarobod": ["Zafarobod", "Yangiqishloq", "Istiqlol", "Tinchlik", "Navoi"],
        "Zarbdor": ["Zarbdor", "Bog'ishamol", "Gulistan", "Mehrat", "Yangiariq"],
        "Zomin": ["Zomin", "Markaziy", "Dustlik", "Bog'bon", "Gulzor"],
        "Mirzacho'l": ["Mirzacho'l", "Yangiobod", "Tinchlik", "Istiqlol", "Navoi"]
    },
    "Qashqadaryo": {
        "Qarshi": ["Markaziy", "Nishon", "Nasaf", "Sharq", "Shimol"],
        "Dehqonobod": ["Dehqonobod", "Guliston", "Yangi Hayot", "Bog'bon", "Dustlik"],
        "Qamashi": ["Qamashi", "Bog'bon", "Tinchlik", "Yangiariq", "Mehrat"],
        "Koson": ["Koson", "Istiqlol", "Mustaqillik", "Gulzor", "Navoi"],
        "Kitob": ["Kitob", "Yangiariq", "Mehnat", "Bog'ishamol", "Dustlik"],
        "Chiroqchi": ["Chiroqchi", "Markaziy", "Gulistan", "Tinchlik", "Istiqlol"],
        "G'uzor": ["G'uzor", "Bog'bon", "Yangiqishloq", "Mehrat", "Navoi"],
        "Mirishkor": ["Mirishkor", "Dustlik", "Gulzor", "Bog'ishamol", "Tinchlik"],
        "Muborak": ["Muborak", "Yangiariq", "Istiqlol", "Gulistan", "Mehrat"],
        "Nishon": ["Nishon", "Markaziy", "Bog'bon", "Dustlik", "Navoi"],
        "Shahrisabz": ["Shahrisabz", "Gulzor", "Tinchlik", "Yangiqishloq", "Istiqlol"],
        "Yakkabog'": ["Yakkabog'", "Bog'ishamol", "Mehrat", "Gulistan", "Yangiariq"]
    },
    "Navoiy": {
        "Navoiy shahri": ["Markaziy", "Kimyogarlar", "Metallurg", "Sharq", "G'arb"],
        "Zarafshon": ["Zarafshon", "Oltin Vodiy", "Yangi Hayot", "Gulistan", "Dustlik"],
        "Xatirchi": ["Xatirchi", "Guliston", "Tinchlik", "Bog'bon", "Yangiariq"],
        "Navbahor": ["Navbahor", "Bog'bon", "Istiqlol", "Mehrat", "Gulzor"],
        "Tomdi": ["Tomdi", "Yangiariq", "Mustaqillik", "Dustlik", "Navoi"],
        "Bespah": ["Bespah", "Bog'ishamol", "Gulistan", "Tinchlik", "Istiqlol"],
        "Karmana": ["Karmana", "Markaziy", "Yangiqishloq", "Mehrat", "Gulzor"],
        "Konimex": ["Konimex", "Dustlik", "Bog'bon", "Navoi", "Yangiariq"],
        "Nurota": ["Nurota", "Gulzor", "Tinchlik", "Istiqlol", "Gulistan"],
        "Uchquduq": ["Uchquduq", "Bog'ishamol", "Mehrat", "Dustlik", "Yangiqishloq"]
    },
    "Namangan": {
        "Namangan shahri": ["Markaziy", "Sharq", "Shimol", "G'arb", "Janub"],
        "Chortoq": ["Chortoq", "Yangi Hayot", "Guliston", "Bog'bon", "Dustlik"],
        "Kosonsoy": ["Kosonsoy", "Bog'bon", "Tinchlik", "Yangiariq", "Mehrat"],
        "Mingbuloq": ["Mingbuloq", "Istiqlol", "Mustaqillik", "Gulzor", "Navoi"],
        "Pop": ["Pop", "Yangiariq", "Mehnat", "Bog'ishamol", "Dustlik"],
        "Chust": ["Chust", "Markaziy", "Gulistan", "Tinchlik", "Istiqlol"],
        "Norin": ["Norin", "Bog'bon", "Yangiqishloq", "Mehrat", "Gulzor"],
        "To'raqo'rg'on": ["To'raqo'rg'on", "Dustlik", "Navoi", "Bog'ishamol", "Yangiariq"],
        "Uychi": ["Uychi", "Gulzor", "Tinchlik", "Istiqlol", "Gulistan"],
        "Uchqo'rg'on": ["Uchqo'rg'on", "Mehrat", "Bog'bon", "Dustlik", "Yangiqishloq"],
        "Yangiqo'rg'on": ["Yangiqo'rg'on", "Bog'ishamol", "Navoi", "Tinchlik", "Gulzor"],
        "Yangihayot": ["Yangihayot", "Yangiariq", "Istiqlol", "Gulistan", "Mehrat"]
    },
    "Samarqand": {
        "Samarqand shahri": ["Markaziy", "Afrosiyob", "Registon", "Sharq", "Shimol"],
        "Bulung'ur": ["Bulung'ur", "Yangi Hayot", "Guliston", "Bog'bon", "Dustlik"],
        "Kattaqo'rg'on": ["Kattaqo'rg'on", "Bog'bon", "Tinchlik", "Yangiariq", "Mehrat"],
        "Ishtixon": ["Ishtixon", "Istiqlol", "Mustaqillik", "Gulzor", "Navoi", "Moxpar", "Moxpar MFY", "Moxpar mahallasi"],
        "Narpay": ["Narpay", "Yangiariq", "Mehnat", "Bog'ishamol", "Dustlik"],
        "Jomboy": ["Jomboy", "Markaziy", "Gulistan", "Tinchlik", "Istiqlol"],
        "Oqdaryo": ["Oqdaryo", "Bog'bon", "Yangiqishloq", "Mehrat", "Gulzor"],
        "Payariq": ["Payariq", "Dustlik", "Navoi", "Bog'ishamol", "Yangiariq", "Bahor"],
        "Pastdarg'om": ["Pastdarg'om", "Gulzor", "Tinchlik", "Istiqlol", "Gulistan"],
        "Qo'shrabot": ["Qo'shrabot", "Mehrat", "Bog'bon", "Dustlik", "Yangiqishloq"],
        "Toyloq": ["Toyloq", "Bog'ishamol", "Navoi", "Tinchlik", "Gulzor"],
        "Urgut": ["Urgut", "Yangiariq", "Istiqlol", "Gulistan", "Mehrat"]
    },
    "Surxondaryo": {
        "Termiz": ["Markaziy", "Amir Temur", "Al-Hakim At-Termiziy", "Sharq", "G'arb"],
        "Angor": ["Angor", "Yangi Hayot", "Guliston", "Bog'bon", "Dustlik"],
        "Boysun": ["Boysun", "Bog'bon", "Tinchlik", "Yangiariq", "Mehrat"],
        "Denov": ["Denov", "Istiqlol", "Mustaqillik", "Gulzor", "Navoi"],
        "Jarqo'rg'on": ["Jarqo'rg'on", "Yangiariq", "Mehnat", "Bog'ishamol", "Dustlik"],
        "Bandixon": ["Bandixon", "Markaziy", "Gulistan", "Tinchlik", "Istiqlol"],
        "Muzrabot": ["Muzrabot", "Bog'bon", "Yangiqishloq", "Mehrat", "Gulzor"],
        "Oltinsoy": ["Oltinsoy", "Dustlik", "Navoi", "Bog'ishamol", "Yangiariq"],
        "Sariosiyo": ["Sariosiyo", "Gulzor", "Tinchlik", "Istiqlol", "Gulistan"],
        "Sherobod": ["Sherobod", "Mehrat", "Bog'bon", "Dustlik", "Yangiqishloq"],
        "Sho'rchi": ["Sho'rchi", "Bog'ishamol", "Navoi", "Tinchlik", "Gulzor"],
        "Uzun": ["Uzun", "Yangiariq", "Istiqlol", "Gulistan", "Mehrat"]
    },
    "Sirdaryo": {
        "Guliston": ["Markaziy", "Istiqlol", "Mustaqillik", "Sharq", "G'arb"],
        "Boyovut": ["Boyovut", "Yangi Hayot", "Guliston", "Bog'bon", "Dustlik"],
        "Mirzaobod": ["Mirzaobod", "Bog'bon", "Tinchlik", "Yangiariq", "Mehrat"],
        "Sayxunobod": ["Sayxunobod", "Yangiariq", "Mehnat", "Bog'ishamol", "Dustlik"],
        "Xovos": ["Xovos", "Oqqo'rg'on", "Dustlik", "Gulzor", "Navoi"],
        "Guliston tumani": ["Markaziy", "Gulistan", "Tinchlik", "Istiqlol", "Mehrat"],
        "Oqoltin": ["Oqoltin", "Bog'bon", "Yangiqishloq", "Gulzor", "Dustlik"],
        "Sardoba": ["Sardoba", "Bog'ishamol", "Navoi", "Tinchlik", "Yangiariq"],
        "Sirdaryo tumani": ["Sirdaryo", "Gulzor", "Istiqlol", "Gulistan", "Mehrat"],
        "Yangiyer": ["Yangiyer", "Yangiariq", "Bog'bon", "Dustlik", "Yangiqishloq"]
    },
    "Toshkent": {
        "Olmaliq": ["Markaziy", "Metallurg", "Kimyogar", "Sharq", "G'arb"],
        "Angren": ["Angren", "Qumtepa", "Yangi Angren", "Gulistan", "Dustlik"],
        "Bekobod": ["Bekobod", "Tinchlik", "Guliston", "Bog'bon", "Yangiariq"],
        "Bo'ka": ["Bo'ka", "Bog'bon", "Yangi Hayot", "Mehrat", "Gulzor"],
        "Bo'stonliq": ["Bo'stonliq", "Istiqlol", "Mustaqillik", "Dustlik", "Navoi"],
        "Chinoz": ["Chinoz", "Markaziy", "Bog'ishamol", "Gulistan", "Tinchlik"],
        "Chirchiq": ["Chirchiq", "Yangiqishloq", "Mehrat", "Gulzor", "Istiqlol"],
        "Ohangaron": ["Ohangaron", "Dustlik", "Navoi", "Bog'bon", "Yangiariq"],
        "Oqqo'rg'on": ["Oqqo'rg'on", "Gulzor", "Tinchlik", "Gulistan", "Mehrat"],
        "Parkent": ["Parkent", "Bog'ishamol", "Yangiqishloq", "Dustlik", "Istiqlol"],
        "Piskent": ["Piskent", "Yangiariq", "Bog'bon", "Navoi", "Gulzor"],
        "Quyichirchiq": ["Quyichirchiq", "Tinchlik", "Gulistan", "Mehrat", "Bog'ishamol"],
        "O'rtachirchiq": ["O'rtachirchiq", "Dustlik", "Yangiqishloq", "Istiqlol", "Yangiariq"],
        "Yangiyo'l": ["Yangiyo'l", "Gulzor", "Navoi", "Bog'bon", "Tinchlik"],
        "Toshkent tumani": ["Toshkent", "Markaziy", "Gulistan", "Mehrat", "Dustlik"],
        "Yuqorichirchiq": ["Yuqorichirchiq", "Bog'ishamol", "Istiqlol", "Yangiariq", "Gulzor"],
        "Zangiota": ["Zangiota", "Tinchlik", "Navoi", "Gulistan", "Yangiqishloq"],
        "Nurafshon": ["Nurafshon", "Mehrat", "Bog'bon", "Dustlik", "Istiqlol"]
    },
    "Farg'ona": {
        "Farg'ona shahri": ["Markaziy", "Yangi Farg'ona", "Qo'qon yo'li", "Sharq", "G'arb"],
        "Marg'ilon": ["Marg'ilon", "Ipakchi", "Hunarmand", "Gulistan", "Dustlik"],
        "Qo'qon": ["Qo'qon", "Amir Temur", "Markaziy", "Bog'bon", "Tinchlik"],
        "Beshariq": ["Beshariq", "Yangi Hayot", "Guliston", "Yangiariq", "Mehrat"],
        "Bog'dod": ["Bog'dod", "Bog'bon", "Tinchlik", "Gulzor", "Navoi"],
        "Buvayda": ["Buvayda", "Istiqlol", "Mustaqillik", "Dustlik", "Bog'ishamol"],
        "Dang'ara": ["Dang'ara", "Markaziy", "Gulistan", "Yangiqishloq", "Mehrat"],
        "Ferghana tumani": ["Ferghana", "Bog'bon", "Tinchlik", "Gulzor", "Yangiariq"],
        "Furqat": ["Furqat", "Dustlik", "Navoi", "Istiqlol", "Bog'ishamol"],
        "Quva": ["Quva", "Gulzor", "Gulistan", "Mehrat", "Tinchlik"],
        "Rishton": ["Rishton", "Yangiqishloq", "Bog'bon", "Dustlik", "Yangiariq"],
        "So'x": ["So'x", "Bog'ishamol", "Navoi", "Gulzor", "Istiqlol"],
        "Toshloq": ["Toshloq", "Tinchlik", "Gulistan", "Mehrat", "Dustlik"],
        "Uchko'prik": ["Uchko'prik", "Yangiariq", "Bog'bon", "Yangiqishloq", "Gulzor"],
        "Yozyovon": ["Yozyovon", "Bog'ishamol", "Navoi", "Istiqlol", "Tinchlik"],
        "Oltiariq": ["Oltiariq", "Gulistan", "Mehrat", "Dustlik", "Yangiariq"]
    },
    "Xorazm": {
        "Urganch": ["Markaziy", "Al-Xorazmiy", "Avesto", "Sharq", "G'arb"],
        "Xiva": ["Xiva", "Ichan Qala", "Toshqo'rg'on", "Gulistan", "Dustlik"],
        "Shovot": ["Shovot", "Yangi Hayot", "Guliston", "Bog'bon", "Tinchlik"],
        "Qo'shko'pir": ["Qo'shko'pir", "Bog'bon", "Tinchlik", "Yangiariq", "Mehrat"],
        "Yangiariq": ["Yangiariq", "Istiqlol", "Mustaqillik", "Gulzor", "Navoi"],
        "Bog'ot": ["Bog'ot", "Markaziy", "Bog'ishamol", "Gulistan", "Dustlik"],
        "Gurlan": ["Gurlan", "Yangiqishloq", "Mehrat", "Gulzor", "Tinchlik"],
        "Hazorasp": ["Hazorasp", "Dustlik", "Navoi", "Bog'bon", "Yangiariq"],
        "Xonqa": ["Xonqa", "Gulzor", "Istiqlol", "Gulistan", "Bog'ishamol"],
        "Yangibozor": ["Yangibozor", "Tinchlik", "Mehrat", "Dustlik", "Yangiqishloq"],
        "Tuproqqal'a": ["Tuproqqal'a", "Yangiariq", "Bog'bon", "Navoi", "Gulzor"],
        "Urganch tumani": ["Urganch", "Bog'ishamol", "Gulistan", "Istiqlol", "Tinchlik"]
    },
    "Qoraqalpog'iston": {
        "Nukus": ["Markaziy", "Berdaqh", "Ajiniyoz", "Sharq", "G'arb"],
        "Xo'jayli": ["Xo'jayli", "Yangi Hayot", "Guliston", "Bog'bon", "Dustlik"],
        "Qo'ng'irot": ["Qo'ng'irot", "Bog'bon", "Tinchlik", "Yangiariq", "Mehrat"],
        "Taxiatosh": ["Taxiatosh", "Istiqlol", "Mustaqillik", "Gulzor", "Navoi"],
        "To'rtko'l": ["To'rtko'l", "Yangiariq", "Mehnat", "Bog'ishamol", "Dustlik"],
        "Amudaryo": ["Amudaryo", "Markaziy", "Gulistan", "Tinchlik", "Gulzor"],
        "Beruniy": ["Beruniy", "Bog'bon", "Yangiqishloq", "Mehrat", "Istiqlol"],
        "Chimboy": ["Chimboy", "Dustlik", "Navoi", "Bog'ishamol", "Yangiariq"],
        "Ellikqala": ["Ellikqala", "Gulzor", "Tinchlik", "Gulistan", "Mehrat"],
        "Kegeyli": ["Kegeyli", "Yangiqishloq", "Bog'bon", "Dustlik", "Istiqlol"],
        "Mo'ynoq": ["Mo'ynoq", "Bog'ishamol", "Navoi", "Yangiariq", "Gulzor"],
        "Qanliko'l": ["Qanliko'l", "Tinchlik", "Gulistan", "Mehrat", "Dustlik"]
    }
}

# Supported document formats
SUPPORTED_FORMATS = {
    'text': ['.txt'],
    'word': ['.doc', '.docx'],
    'excel': ['.xls', '.xlsx'],
    'pdf': ['.pdf']
}

SUPPORTED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain'
}

# Age groups for tests
AGE_GROUPS = {
    "7-10": {"min": 7, "max": 10, "label": "7-10 yosh"},
    "11-14": {"min": 11, "max": 14, "label": "11-14 yosh"}
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "high_error_rate": 50,
    "slow_response_time": 5.0,
    "memory_limit_mb": 500
}

# Export settings
EXPORT_SETTINGS = {
    "max_rows_per_sheet": 65000,
    "excel_font_size": 10,
    "pdf_font_size": 8,
    "max_export_file_size": 100 * 1024 * 1024  # 100MB
}
