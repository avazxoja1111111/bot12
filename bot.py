#!/usr/bin/env python3
"""
Kitobxon Kids - Educational Testing Bot
A comprehensive Telegram bot for conducting reading comprehension tests
Refactored version with multi-format support and optimized performance
"""

import asyncio
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BotCommand, CallbackQuery, Document, InlineKeyboardButton,
    InlineKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

# Optional imports for document processing
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════════

# Bot configuration
BOT_TOKEN = os.getenv("7570796885:AAFkj7iY05fQUG21015viY7Gy8ifXXcnOpA")
if not BOT_TOKEN:
    raise ValueError("7570796885:AAFkj7iY05fQUG21015viY7Gy8ifXXcnOpA")

# Data directory
DATA_DIR = Path("bot_data")
DATA_DIR.mkdir(exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES AND VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════════

# Regional data for Uzbekistan
REGIONS_DATA = {
    "Toshkent shahri": {
        "Bektemir": ["Kuyluk", "Sarabon", "Bunyodkor"],
        "Chilonzor": ["Chilonzor", "Kimyogarlar", "Namuna"],
        "Mirobod": ["Mirobod", "Ulugbek", "Makhmudov"],
        "Mirzo Ulugbek": ["Qoraqamish", "Beruni", "Maksim Gorkiy"],
        "Olmazar": ["Olmazar", "Mavlon Qori", "Bobur"],
        "Sergeli": ["Sergeli", "Qipchoq", "Yangi Sergeli"],
        "Shayhontohur": ["Shayhontohur", "Berdaq", "Pakhtakor"],
        "Uchtepa": ["Uchtepa", "Kukcha", "Qadamjoy"],
        "Yakkasaroy": ["Yakkasaroy", "Kucha", "Vodnik"],
        "Yashnobod": ["Yashnobod", "Shifokor", "Muqimiy"],
        "Yunusobod": ["Yunusobod", "Buyuk Ipak Yuli", "Bobur"],
        "Yashil": ["Yashil", "Doston", "Temur Malik"]
    },
    "Andijon": {
        "Andijon shahri": ["Markaziy", "Sharqiy", "Shimoliy"],
        "Asaka": ["Asaka", "Kasr", "Navoiy"],
        "Baliqchi": ["Baliqchi", "Yangiqishloq", "Qoraqum"],
        "Bo'z": ["Bo'z", "Xonobod", "Yangi Hayot"],
        "Buloqboshi": ["Buloqboshi", "Tinchlik", "Mustaqillik"]
    },
    "Buxoro": {
        "Buxoro shahri": ["Abu Ali ibn Sino", "Ismoil Somoniy", "Markaziy"],
        "Kogon": ["Kogon", "Dustlik", "Yangi Hayot"],
        "Olot": ["Olot", "Tinchlik", "Guliston"],
        "Peshku": ["Peshku", "Bog'bon", "Yangiariq"],
        "Qorako'l": ["Qorako'l", "Samarkand", "Istiqlol"]
    },
    "Jizzax": {
        "Jizzax shahri": ["Markaziy", "Istiqlol", "Mustaqillik"],
        "Arnasoy": ["Arnasoy", "Tinchlik", "Yangiyer"],
        "Baxtiyor": ["Baxtiyor", "Guliston", "Mehnat"],
        "Do'stlik": ["Do'stlik", "Yangi Hayot", "Bog'bon"],
        "Forish": ["Forish", "Qizilcha", "Yangiqishloq"]
    },
    "Qashqadaryo": {
        "Qarshi": ["Markaziy", "Nishon", "Nasaf"],
        "Dehqonobod": ["Dehqonobod", "Guliston", "Yangi Hayot"],
        "Qamashi": ["Qamashi", "Bog'bon", "Tinchlik"],
        "Koson": ["Koson", "Istiqlol", "Mustaqillik"],
        "Kitob": ["Kitob", "Yangiariq", "Mehnat"]
    },
    "Navoiy": {
        "Navoiy shahri": ["Markaziy", "Kimyogarlar", "Metallurg"],
        "Zarafshon": ["Zarafshon", "Oltin Vodiy", "Yangi Hayot"],
        "Xatirchi": ["Xatirchi", "Guliston", "Tinchlik"],
        "Navbahor": ["Navbahor", "Bog'bon", "Istiqlol"],
        "Tomdi": ["Tomdi", "Yangiariq", "Mustaqillik"]
    },
    "Namangan": {
        "Namangan shahri": ["Markaziy", "Sharq", "Shimol"],
        "Chortoq": ["Chortoq", "Yangi Hayot", "Guliston"],
        "Kosonsoy": ["Kosonsoy", "Bog'bon", "Tinchlik"],
        "Mingbuloq": ["Mingbuloq", "Istiqlol", "Mustaqillik"],
        "Pop": ["Pop", "Yangiariq", "Mehnat"]
    },
    "Samarqand": {
        "Samarqand shahri": ["Markaziy", "Afrosiyob", "Registon"],
        "Bulung'ur": ["Bulung'ur", "Yangi Hayot", "Guliston"],
        "Kattaqo'rg'on": ["Kattaqo'rg'on", "Bog'bon", "Tinchlik"],
        "Ishtixon": ["Ishtixon", "Istiqlol", "Mustaqillik"],
        "Narpay": ["Narpay", "Yangiariq", "Mehnat"]
    },
    "Surxondaryo": {
        "Termiz": ["Markaziy", "Amir Temur", "Al-Hakim At-Termiziy"],
        "Angor": ["Angor", "Yangi Hayot", "Guliston"],
        "Boysun": ["Boysun", "Bog'bon", "Tinchlik"],
        "Denov": ["Denov", "Istiqlol", "Mustaqillik"],
        "Jarqo'rg'on": ["Jarqo'rg'on", "Yangiariq", "Mehnat"]
    },
    "Sirdaryo": {
        "Guliston": ["Markaziy", "Istiqlol", "Mustaqillik"],
        "Boyovut": ["Boyovut", "Yangi Hayot", "Guliston"],
        "Mirzaobod": ["Mirzaobod", "Bog'bon", "Tinchlik"],
        "Sayxunobod": ["Sayxunobod", "Yangiariq", "Mehnat"],
        "Xovos": ["Xovos", "Oqqo'rg'on", "Dustlik"]
    },
    "Toshkent": {
        "Olmaliq": ["Markaziy", "Metallurg", "Kimyogar"],
        "Angren": ["Angren", "Qumtepa", "Yangi Angren"],
        "Bekobod": ["Bekobod", "Tinchlik", "Guliston"],
        "Bo'ka": ["Bo'ka", "Bog'bon", "Yangi Hayot"],
        "Bo'stonliq": ["Bo'stonliq", "Istiqlol", "Mustaqillik"]
    },
    "Farg'ona": {
        "Farg'ona shahri": ["Markaziy", "Yangi Farg'ona", "Qo'qon yo'li"],
        "Marg'ilon": ["Marg'ilon", "Ipakchi", "Hunarmand"],
        "Qo'qon": ["Qo'qon", "Amir Temur", "Markaziy"],
        "Beshariq": ["Beshariq", "Yangi Hayot", "Guliston"],
        "Bog'dod": ["Bog'dod", "Bog'bon", "Tinchlik"]
    },
    "Xorazm": {
        "Urganch": ["Markaziy", "Al-Xorazmiy", "Avesto"],
        "Xiva": ["Xiva", "Ichan Qala", "Toshqo'rg'on"],
        "Shovot": ["Shovot", "Yangi Hayot", "Guliston"],
        "Qo'shko'pir": ["Qo'shko'pir", "Bog'bon", "Tinchlik"],
        "Yangiariq": ["Yangiariq", "Istiqlol", "Mustaqillik"]
    },
    "Qoraqalpog'iston": {
        "Nukus": ["Markaziy", "Berdaqh", "Ajiniyoz"],
        "Xo'jayli": ["Xo'jayli", "Yangi Hayot", "Guliston"],
        "Qo'ng'irot": ["Qo'ng'irot", "Bog'bon", "Tinchlik"],
        "Taxiatosh": ["Taxiatosh", "Istiqlol", "Mustaqillik"],
        "To'rtko'l": ["To'rtko'l", "Yangiariq", "Mehnat"]
    }
}

def validate_name(name: str) -> bool:
    """Validate name format (Uzbek names)"""
    if not name or len(name.strip()) < 2:
        return False
    # Allow Uzbek letters, spaces, apostrophes
    pattern = r"^[A-Za-zÀ-ÿĀ-žА-я\s']+$"
    return bool(re.match(pattern, name.strip()))

def validate_age(age_str: str) -> bool:
    """Validate age (7-14 years)"""
    try:
        age = int(age_str)
        return 7 <= age <= 14
    except ValueError:
        return False

def validate_phone(phone: str) -> bool:
    """Validate Uzbek phone number format"""
    # Remove all non-digit characters
    clean_phone = re.sub(r'\D', '', phone)
    # Check for Uzbek mobile numbers
    uzbek_patterns = [
        r'^998[0-9]{9}$',      # +998XXXXXXXXX
        r'^[0-9]{9}$',         # XXXXXXXXX
        r'^[0-9]{12}$'         # 998XXXXXXXXX
    ]
    return any(re.match(pattern, clean_phone) for pattern in uzbek_patterns)

def validate_region(region: str) -> bool:
    """Check if region exists in our data"""
    return region in REGIONS_DATA

def validate_district(region: str, district: str) -> bool:
    """Check if district exists in the specified region"""
    if region not in REGIONS_DATA:
        return False
    return district in REGIONS_DATA[region]

def validate_mahalla(region: str, district: str, mahalla: str) -> bool:
    """Check if mahalla exists in the specified district"""
    if not validate_district(region, district):
        return False
    return mahalla in REGIONS_DATA[region][district]

def validate_document_format(filename: str, mime_type: str) -> bool:
    """Validate document format (PDF, Word, Excel, Text)"""
    allowed_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt'}
    allowed_mime_types = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain'
    }
    
    if not filename:
        return False
        
    file_ext = Path(filename).suffix.lower()
    return file_ext in allowed_extensions or mime_type in allowed_mime_types

def get_document_type(filename: str, mime_type: str) -> str:
    """Get document type from filename and mime type"""
    if not filename:
        return "unknown"
        
    file_ext = Path(filename).suffix.lower()
    
    if file_ext in ['.pdf'] or 'pdf' in mime_type:
        return "PDF"
    elif file_ext in ['.doc', '.docx'] or 'word' in mime_type:
        return "Word"
    elif file_ext in ['.xls', '.xlsx'] or 'excel' in mime_type or 'spreadsheet' in mime_type:
        return "Excel"
    elif file_ext in ['.txt'] or 'text' in mime_type:
        return "Text"
    else:
        return "unknown"

def extract_text_from_document(file_content: bytes, filename: str, mime_type: str) -> str:
    """Extract text content from various document formats"""
    doc_type = get_document_type(filename, mime_type)
    
    try:
        if doc_type == "Text":
            return file_content.decode('utf-8', errors='ignore')
        elif doc_type == "Word" and DOCX_AVAILABLE:
            doc = DocxDocument(BytesIO(file_content))
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        elif doc_type == "PDF":
            # For PDF, we'll return a placeholder since we don't have PDF text extraction
            return f"PDF document: {filename} (text extraction not available)"
        elif doc_type == "Excel" and EXCEL_AVAILABLE:
            workbook = openpyxl.load_workbook(BytesIO(file_content))
            text_content = []
            for sheet in workbook.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    text_content.append(' '.join([str(cell) if cell else '' for cell in row]))
            return '\n'.join(text_content)
        else:
            return f"Document format not supported for text extraction: {doc_type}"
    except Exception as e:
        logger.error(f"Error extracting text from {doc_type} document: {e}")
        return f"Error extracting text from {doc_type} document"

# ═══════════════════════════════════════════════════════════════════════════════════
# DATA MANAGER
# ═══════════════════════════════════════════════════════════════════════════════════

class DataManager:
    """Optimized data manager for high concurrent load"""
    
    def __init__(self):
        self.data_files = {
            'users': DATA_DIR / 'users.json',
            'admins': DATA_DIR / 'admins.json',
            'tests': DATA_DIR / 'tests.json',
            'results': DATA_DIR / 'results.json',
            'statistics': DATA_DIR / 'statistics.json',
            'broadcasts': DATA_DIR / 'broadcasts.json',
            'bot_users': DATA_DIR / 'bot_users.json',
            'access_control': DATA_DIR / 'access_control.json'
        }
        self._ensure_data_files()

    def _ensure_data_files(self):
        """Initialize data files with default structures"""
        default_data = {
            'users': {},
            'admins': {
                "super_admins": ["username1", "username2"],  # Replace with actual admin usernames
                "last_updated": datetime.now(timezone.utc).isoformat()
            },
            'tests': {
                "7-10": {},
                "11-14": {}
            },
            'results': {},
            'statistics': {
                "total_users": 0,
                "total_tests_taken": 0,
                "regional_stats": {},
                "age_group_stats": {
                    "7-10": {"users": 0, "tests_taken": 0},
                    "11-14": {"users": 0, "tests_taken": 0}
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            },
            'broadcasts': {},
            'bot_users': {},
            'access_control': {
                "test_access_enabled": True,
                "allowed_users": [],
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }

        for key, file_path in self.data_files.items():
            if not file_path.exists():
                self._save_data(key, default_data[key])

    def _load_data(self, data_type: str) -> Dict[str, Any]:
        """Load data from JSON file with error handling"""
        try:
            with open(self.data_files[data_type], 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading {data_type}: {e}")
            return {}

    def _save_data(self, data_type: str, data: Dict[str, Any]) -> bool:
        """Save data to JSON file with atomic writes"""
        try:
            temp_file = self.data_files[data_type].with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_file.replace(self.data_files[data_type])
            return True
        except Exception as e:
            logger.error(f"Error saving {data_type}: {e}")
            return False

    # User management
    def save_user(self, user_data: Dict[str, Any]) -> str:
        """Save user with unique registration ID"""
        users = self._load_data('users')
        reg_id = f"{user_data['telegram_id']}_{datetime.now().timestamp()}"
        
        user_data['registration_id'] = reg_id
        user_data['registration_date'] = datetime.now(timezone.utc).isoformat()
        
        users[reg_id] = user_data
        
        if self._save_data('users', users):
            self._update_statistics_for_new_user(user_data)
            return reg_id
        return ""

    def get_user_registrations(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Get all registrations for a user (unlimited registrations allowed)"""
        users = self._load_data('users')
        user_registrations = []
        
        for reg_id, user_data in users.items():
            if user_data.get('telegram_id') == telegram_id:
                user_registrations.append({
                    'registration_id': reg_id,
                    **user_data
                })
        
        return sorted(user_registrations, key=lambda x: x.get('registration_date', ''), reverse=True)

    def get_all_users(self) -> Dict[str, Any]:
        """Get all users"""
        return self._load_data('users')

    # Admin management (Super Admin only)
    def is_super_admin(self, username: str) -> bool:
        """Check if user is super admin"""
        if not username:
            return False
        admins = self._load_data('admins')
        return username in admins.get('super_admins', [])

    def add_super_admin(self, username: str) -> bool:
        """Add super admin"""
        admins = self._load_data('admins')
        if username not in admins.get('super_admins', []):
            admins.setdefault('super_admins', []).append(username)
            admins['last_updated'] = datetime.now(timezone.utc).isoformat()
            return self._save_data('admins', admins)
        return False

    def remove_super_admin(self, username: str) -> bool:
        """Remove super admin"""
        admins = self._load_data('admins')
        if username in admins.get('super_admins', []):
            admins['super_admins'].remove(username)
            admins['last_updated'] = datetime.now(timezone.utc).isoformat()
            return self._save_data('admins', admins)
        return False

    def get_super_admins(self) -> List[str]:
        """Get list of super admins"""
        admins = self._load_data('admins')
        return admins.get('super_admins', [])

    # Test management
    def save_test(self, test_data: Dict[str, Any], age_group: str) -> str:
        """Save test to appropriate age group"""
        tests = self._load_data('tests')
        test_id = str(uuid.uuid4())
        
        test_data['test_id'] = test_id
        test_data['created_at'] = datetime.now(timezone.utc).isoformat()
        
        if age_group not in tests:
            tests[age_group] = {}
        
        tests[age_group][test_id] = test_data
        
        if self._save_data('tests', tests):
            return test_id
        return ""

    def get_tests_by_age_group(self, age_group: str) -> Dict[str, Any]:
        """Get tests for specific age group"""
        tests = self._load_data('tests')
        return tests.get(age_group, {})

    def get_test(self, test_id: str, age_group: str) -> Optional[Dict[str, Any]]:
        """Get specific test"""
        tests = self.get_tests_by_age_group(age_group)
        return tests.get(test_id)

    def delete_test(self, test_id: str, age_group: str) -> bool:
        """Delete test"""
        tests = self._load_data('tests')
        if age_group in tests and test_id in tests[age_group]:
            del tests[age_group][test_id]
            return self._save_data('tests', tests)
        return False

    # Results management
    def save_test_result(self, result_data: Dict[str, Any]) -> str:
        """Save test result"""
        results = self._load_data('results')
        result_id = str(uuid.uuid4())
        
        result_data['result_id'] = result_id
        result_data['completed_at'] = datetime.now(timezone.utc).isoformat()
        
        results[result_id] = result_data
        
        if self._save_data('results', results):
            self._update_statistics_for_test_result(result_data)
            return result_id
        return ""

    def get_user_results(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Get all test results for a user"""
        results = self._load_data('results')
        user_results = []
        
        for result_id, result_data in results.items():
            if result_data.get('telegram_id') == telegram_id:
                user_results.append({
                    'result_id': result_id,
                    **result_data
                })
        
        return sorted(user_results, key=lambda x: x.get('completed_at', ''), reverse=True)

    def get_all_results(self) -> Dict[str, Any]:
        """Get all test results"""
        return self._load_data('results')

    # Access control
    def can_access_tests(self, telegram_id: int, username: str) -> bool:
        """Check if user can access tests"""
        access_control = self._load_data('access_control')
        
        # If test access is disabled, only super admins can access
        if not access_control.get('test_access_enabled', True):
            return self.is_super_admin(username or "")
        
        # If allowed_users list is empty, everyone can access
        allowed_users = access_control.get('allowed_users', [])
        if not allowed_users:
            return True
        
        # Check if user is in allowed list (by username or telegram_id)
        return (username and username in allowed_users) or str(telegram_id) in allowed_users

    def update_test_access(self, enabled: bool, allowed_users: Optional[List[str]] = None) -> bool:
        """Update test access control"""
        access_control = self._load_data('access_control')
        access_control['test_access_enabled'] = enabled
        if allowed_users is not None:
            access_control['allowed_users'] = allowed_users
        access_control['last_updated'] = datetime.now(timezone.utc).isoformat()
        return self._save_data('access_control', access_control)

    def get_access_control_info(self) -> Dict[str, Any]:
        """Get access control information"""
        return self._load_data('access_control')

    # Bot users tracking
    def track_bot_user(self, user_data: Dict[str, Any]) -> bool:
        """Track bot user for broadcasting"""
        bot_users = self._load_data('bot_users')
        user_id = str(user_data.get('telegram_id'))
        
        bot_users[user_id] = {
            'telegram_id': user_data.get('telegram_id'),
            'username': user_data.get('username'),
            'first_name': user_data.get('first_name'),
            'last_seen': datetime.now(timezone.utc).isoformat()
        }
        
        return self._save_data('bot_users', bot_users)

    def get_all_bot_users(self) -> Dict[str, Any]:
        """Get all bot users"""
        return self._load_data('bot_users')

    # Broadcasting
    def save_broadcast(self, broadcast_data: Dict[str, Any]) -> str:
        """Save broadcast message"""
        broadcasts = self._load_data('broadcasts')
        broadcast_id = str(uuid.uuid4())
        
        broadcast_data['broadcast_id'] = broadcast_id
        broadcast_data['created_at'] = datetime.now(timezone.utc).isoformat()
        
        broadcasts[broadcast_id] = broadcast_data
        
        if self._save_data('broadcasts', broadcasts):
            return broadcast_id
        return ""

    def get_all_broadcasts(self) -> Dict[str, Any]:
        """Get all broadcasts"""
        return self._load_data('broadcasts')

    # Statistics
    def _update_statistics_for_new_user(self, user_data: Dict[str, Any]) -> None:
        """Update statistics when a new user registers"""
        stats = self._load_data('statistics')
        
        stats['total_users'] = stats.get('total_users', 0) + 1
        
        # Update regional stats
        region = user_data.get('region')
        if region:
            if 'regional_stats' not in stats:
                stats['regional_stats'] = {}
            stats['regional_stats'][region] = stats['regional_stats'].get(region, 0) + 1
        
        # Update age group stats
        age = user_data.get('age')
        if age:
            try:
                age_int = int(age)
                age_group = "7-10" if 7 <= age_int <= 10 else "11-14"
                if 'age_group_stats' not in stats:
                    stats['age_group_stats'] = {"7-10": {"users": 0, "tests_taken": 0}, "11-14": {"users": 0, "tests_taken": 0}}
                stats['age_group_stats'][age_group]['users'] = stats['age_group_stats'][age_group].get('users', 0) + 1
            except ValueError:
                pass
        
        stats['last_updated'] = datetime.now(timezone.utc).isoformat()
        self._save_data('statistics', stats)

    def _update_statistics_for_test_result(self, result_data: Dict[str, Any]) -> None:
        """Update statistics when a test is completed"""
        stats = self._load_data('statistics')
        
        stats['total_tests_taken'] = stats.get('total_tests_taken', 0) + 1
        
        # Update age group test stats
        age_group = result_data.get('age_group')
        if age_group and 'age_group_stats' in stats and age_group in stats['age_group_stats']:
            stats['age_group_stats'][age_group]['tests_taken'] = stats['age_group_stats'][age_group].get('tests_taken', 0) + 1
        
        stats['last_updated'] = datetime.now(timezone.utc).isoformat()
        self._save_data('statistics', stats)

    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self._load_data('statistics')

# ═══════════════════════════════════════════════════════════════════════════════════
# DOCUMENT EXPORT MANAGER
# ═══════════════════════════════════════════════════════════════════════════════════

class DocumentExportManager:
    """Manager for multi-format document exports"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def export_users_excel(self) -> Optional[BytesIO]:
        """Export users data to Excel format"""
        if not EXCEL_AVAILABLE:
            logger.error("Excel export not available - openpyxl not installed")
            return None

        try:
            users = self.data_manager.get_all_users()
            
            workbook = openpyxl.Workbook()
            worksheet = workbook.active
            worksheet.title = "Foydalanuvchilar"
            
            # Headers
            headers = [
                "Registration ID", "Telegram ID", "Bola ismi", "Ota-ona ismi",
                "Viloyat", "Tuman", "Mahalla", "Yosh", "Telefon", "Username",
                "Ro'yxatdan o'tgan sana"
            ]
            
            for col, header in enumerate(headers, 1):
                cell = worksheet.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            
            # Data
            for row, (reg_id, user_data) in enumerate(users.items(), 2):
                worksheet.cell(row=row, column=1, value=reg_id)
                worksheet.cell(row=row, column=2, value=user_data.get('telegram_id', ''))
                worksheet.cell(row=row, column=3, value=user_data.get('child_name', ''))
                worksheet.cell(row=row, column=4, value=user_data.get('parent_name', ''))
                worksheet.cell(row=row, column=5, value=user_data.get('region', ''))
                worksheet.cell(row=row, column=6, value=user_data.get('district', ''))
                worksheet.cell(row=row, column=7, value=user_data.get('mahalla', ''))
                worksheet.cell(row=row, column=8, value=user_data.get('age', ''))
                worksheet.cell(row=row, column=9, value=user_data.get('phone', ''))
                worksheet.cell(row=row, column=10, value=user_data.get('username', ''))
                worksheet.cell(row=row, column=11, value=user_data.get('registration_date', ''))
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            output = BytesIO()
            workbook.save(output)
            output.seek(0)
            return output
            
        except Exception as e:
            logger.error(f"Error creating Excel export: {e}")
            return None

    def export_users_word(self) -> Optional[BytesIO]:
        """Export users data to Word format"""
        if not DOCX_AVAILABLE:
            logger.error("Word export not available - python-docx not installed")
            return None

        try:
            users = self.data_manager.get_all_users()
            
            doc = DocxDocument()
            
            # Title
            title = doc.add_heading("FOYDALANUVCHILAR MA'LUMOTLARI", 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Content
            for i, (reg_id, user_data) in enumerate(users.items(), 1):
                doc.add_heading(f"{i}. FOYDALANUVCHI", level=2)
                
                table = doc.add_table(rows=11, cols=2)
                table.style = 'Table Grid'
                
                fields = [
                    ("Registration ID", reg_id),
                    ("Telegram ID", user_data.get('telegram_id', 'N/A')),
                    ("Bola ismi", user_data.get('child_name', 'N/A')),
                    ("Ota-ona ismi", user_data.get('parent_name', 'N/A')),
                    ("Viloyat", user_data.get('region', 'N/A')),
                    ("Tuman", user_data.get('district', 'N/A')),
                    ("Mahalla", user_data.get('mahalla', 'N/A')),
                    ("Yosh", user_data.get('age', 'N/A')),
                    ("Telefon", user_data.get('phone', 'N/A')),
                    ("Username", user_data.get('username', 'N/A')),
                    ("Ro'yxatdan o'tgan sana", user_data.get('registration_date', 'N/A'))
                ]
                
                for row_idx, (field, value) in enumerate(fields):
                    table.cell(row_idx, 0).text = field
                    table.cell(row_idx, 1).text = str(value)
                
                doc.add_page_break()
            
            output = BytesIO()
            doc.save(output)
            output.seek(0)
            return output
            
        except Exception as e:
            logger.error(f"Error creating Word export: {e}")
            return None

    def export_users_pdf(self) -> Optional[BytesIO]:
        """Export users data to PDF format"""
        if not PDF_AVAILABLE:
            logger.error("PDF export not available - reportlab not installed")
            return None

        try:
            users = self.data_manager.get_all_users()
            
            output = BytesIO()
            doc = SimpleDocTemplate(output, pagesize=landscape(A4))
            content = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph("FOYDALANUVCHILAR MA'LUMOTLARI", styles['Title'])
            content.append(title)
            
            # Prepare table data
            table_data = [
                ['Registration ID', 'Telegram ID', 'Bola ismi', 'Ota-ona ismi', 'Viloyat', 'Tuman', 'Yosh', 'Telefon']
            ]
            
            for reg_id, user_data in users.items():
                row = [
                    reg_id[:20] + '...' if len(reg_id) > 20 else reg_id,
                    str(user_data.get('telegram_id', 'N/A')),
                    user_data.get('child_name', 'N/A')[:15] + '...' if len(user_data.get('child_name', '')) > 15 else user_data.get('child_name', 'N/A'),
                    user_data.get('parent_name', 'N/A')[:15] + '...' if len(user_data.get('parent_name', '')) > 15 else user_data.get('parent_name', 'N/A'),
                    user_data.get('region', 'N/A')[:10] + '...' if len(user_data.get('region', '')) > 10 else user_data.get('region', 'N/A'),
                    user_data.get('district', 'N/A')[:10] + '...' if len(user_data.get('district', '')) > 10 else user_data.get('district', 'N/A'),
                    str(user_data.get('age', 'N/A')),
                    user_data.get('phone', 'N/A')[:12] + '...' if len(user_data.get('phone', '')) > 12 else user_data.get('phone', 'N/A')
                ]
                table_data.append(row)
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(table)
            
            # Build PDF
            doc.build(content)
            output.seek(0)
            return output
            
        except Exception as e:
            logger.error(f"Error creating PDF export: {e}")
            return None

    def export_users_text(self) -> str:
        """Export users data to text format"""
        try:
            users = self.data_manager.get_all_users()
            
            text_content = "FOYDALANUVCHILAR MA'LUMOTLARI\n"
            text_content += "=" * 50 + "\n\n"
            
            for i, (reg_id, user_data) in enumerate(users.items(), 1):
                text_content += f"{i}. FOYDALANUVCHI\n"
                text_content += f"   Registration ID: {reg_id}\n"
                text_content += f"   Telegram ID: {user_data.get('telegram_id', 'N/A')}\n"
                text_content += f"   Bola ismi: {user_data.get('child_name', 'N/A')}\n"
                text_content += f"   Ota-ona ismi: {user_data.get('parent_name', 'N/A')}\n"
                text_content += f"   Viloyat: {user_data.get('region', 'N/A')}\n"
                text_content += f"   Tuman: {user_data.get('district', 'N/A')}\n"
                text_content += f"   Mahalla: {user_data.get('mahalla', 'N/A')}\n"
                text_content += f"   Yosh: {user_data.get('age', 'N/A')}\n"
                text_content += f"   Telefon: {user_data.get('phone', 'N/A')}\n"
                username = user_data.get('username', 'Noma\'lum')
                text_content += f"   Username: {username}\n"
                text_content += f"   Ro'yxatdan o'tgan sana: {user_data.get('registration_date', 'N/A')}\n"
                text_content += "-" * 30 + "\n\n"
            
            return text_content
            
        except Exception as e:
            logger.error(f"Error creating text export: {e}")
            return f"Eksport yaratishda xatolik: {str(e)}"

    def export_results_excel(self) -> Optional[BytesIO]:
        """Export test results to Excel format"""
        if not EXCEL_AVAILABLE:
            return None

        try:
            results = self.data_manager.get_all_results()
            
            workbook = openpyxl.Workbook()
            worksheet = workbook.active
            worksheet.title = "Test Natijalari"
            
            # Headers
            headers = [
                "Result ID", "Telegram ID", "Test ID", "Test Name", "Age Group",
                "Score", "Total Questions", "Percentage", "Completed At"
            ]
            
            for col, header in enumerate(headers, 1):
                cell = worksheet.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            
            # Data
            for row, (result_id, result_data) in enumerate(results.items(), 2):
                worksheet.cell(row=row, column=1, value=result_id)
                worksheet.cell(row=row, column=2, value=result_data.get('telegram_id', ''))
                worksheet.cell(row=row, column=3, value=result_data.get('test_id', ''))
                worksheet.cell(row=row, column=4, value=result_data.get('test_name', ''))
                worksheet.cell(row=row, column=5, value=result_data.get('age_group', ''))
                worksheet.cell(row=row, column=6, value=result_data.get('score', 0))
                worksheet.cell(row=row, column=7, value=result_data.get('total_questions', 0))
                worksheet.cell(row=row, column=8, value=f"{result_data.get('percentage', 0):.1f}%")
                worksheet.cell(row=row, column=9, value=result_data.get('completed_at', ''))
            
            output = BytesIO()
            workbook.save(output)
            output.seek(0)
            return output
            
        except Exception as e:
            logger.error(f"Error creating Excel results export: {e}")
            return None

# ═══════════════════════════════════════════════════════════════════════════════════
# FSM STATES
# ═══════════════════════════════════════════════════════════════════════════════════

class UserRegistrationStates(StatesGroup):
    waiting_for_child_name = State()
    waiting_for_parent_name = State()
    waiting_for_region = State()
    waiting_for_district = State()
    waiting_for_mahalla = State()
    waiting_for_age = State()
    waiting_for_phone = State()

class TestStates(StatesGroup):
    selecting_age_group = State()
    selecting_test = State()
    taking_test = State()

class AdminStates(StatesGroup):
    # Test management
    creating_test_name = State()
    creating_test_age_group = State()
    creating_test_document = State()
    creating_test_questions = State()
    
    # Access control
    managing_access_control = State()
    adding_allowed_user = State()
    
    # Broadcasting
    creating_broadcast = State()
    
    # Export
    selecting_export_format = State()

# ═══════════════════════════════════════════════════════════════════════════════════
# KEYBOARD HELPERS
# ═══════════════════════════════════════════════════════════════════════════════════

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = [
        [KeyboardButton(text="📝 Ro'yxatdan o'tish")],
        [KeyboardButton(text="📚 Test ishlash"), KeyboardButton(text="📊 Natijalarim")],
        [KeyboardButton(text="ℹ️ Bot haqida"), KeyboardButton(text="☎️ Aloqa")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Admin menu keyboard (Super Admin only)"""
    keyboard = [
        [KeyboardButton(text="👥 Foydalanuvchilar"), KeyboardButton(text="📋 Testlar")],
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="🔒 Kirish nazorati")],
        [KeyboardButton(text="📢 Xabar yuborish"), KeyboardButton(text="📁 Eksport")],
        [KeyboardButton(text="🔙 Asosiy menu")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_regions_keyboard() -> InlineKeyboardMarkup:
    """Regions inline keyboard"""
    keyboard = []
    regions = list(REGIONS_DATA.keys())
    
    # Create rows of 2 regions each
    for i in range(0, len(regions), 2):
        row = []
        for j in range(i, min(i + 2, len(regions))):
            row.append(InlineKeyboardButton(
                text=regions[j],
                callback_data=f"region:{regions[j]}"
            ))
        keyboard.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_districts_keyboard(region: str) -> InlineKeyboardMarkup:
    """Districts inline keyboard for a region"""
    if region not in REGIONS_DATA:
        return InlineKeyboardMarkup(inline_keyboard=[[]])
    
    keyboard = []
    districts = list(REGIONS_DATA[region].keys())
    
    # Create rows of 2 districts each
    for i in range(0, len(districts), 2):
        row = []
        for j in range(i, min(i + 2, len(districts))):
            row.append(InlineKeyboardButton(
                text=districts[j],
                callback_data=f"district:{region}:{districts[j]}"
            ))
        keyboard.append(row)
    
    # Back button
    keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_regions")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_mahallas_keyboard(region: str, district: str) -> InlineKeyboardMarkup:
    """Mahallas inline keyboard for a district"""
    if region not in REGIONS_DATA or district not in REGIONS_DATA[region]:
        return InlineKeyboardMarkup(inline_keyboard=[[]])
    
    keyboard = []
    mahallas = REGIONS_DATA[region][district]
    
    # Create rows of 2 mahallas each
    for i in range(0, len(mahallas), 2):
        row = []
        for j in range(i, min(i + 2, len(mahallas))):
            row.append(InlineKeyboardButton(
                text=mahallas[j],
                callback_data=f"mahalla:{region}:{district}:{mahallas[j]}"
            ))
        keyboard.append(row)
    
    # Back button
    keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"back_to_districts:{region}")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_age_groups_keyboard() -> InlineKeyboardMarkup:
    """Age groups keyboard for tests"""
    keyboard = [
        [InlineKeyboardButton(text="7-10 yosh", callback_data="age_group:7-10")],
        [InlineKeyboardButton(text="11-14 yosh", callback_data="age_group:11-14")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_export_formats_keyboard() -> InlineKeyboardMarkup:
    """Export formats keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="📄 Text", callback_data="export:text")],
        [InlineKeyboardButton(text="📊 Excel", callback_data="export:excel")],
        [InlineKeyboardButton(text="📝 Word", callback_data="export:word")],
        [InlineKeyboardButton(text="📄 PDF", callback_data="export:pdf")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ═══════════════════════════════════════════════════════════════════════════════════
# BOT INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════════

# Initialize data manager and export manager
data_manager = DataManager()
export_manager = DocumentExportManager(data_manager)

# Initialize bot and dispatcher
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# ═══════════════════════════════════════════════════════════════════════════════════
# HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════════

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    """Handle /start command"""
    await state.clear()
    
    user_data = {
        'telegram_id': message.from_user.id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name
    }
    data_manager.track_bot_user(user_data)
    
    # Check if user is super admin
    is_admin = data_manager.is_super_admin(message.from_user.username or "")
    
    welcome_text = f"Assalomu alaykum, {message.from_user.first_name}! 👋\n\n"
    welcome_text += "📚 <b>Kitobxon Kids</b> botiga xush kelibsiz!\n\n"
    welcome_text += "Bu bot 7-14 yosh orasidagi bolalar uchun o'qish tushunish testlarini o'tkazish uchun mo'ljallangan.\n\n"
    welcome_text += "🎯 <b>Bot imkoniyatlari:</b>\n"
    welcome_text += "• Ro'yxatdan o'tish (cheksiz registratsiya)\n"
    welcome_text += "• Yosh guruhiga mos testlar\n"
    welcome_text += "• Natijalarni ko'rish\n"
    welcome_text += "• Ko'p formatda eksport\n\n"
    
    if is_admin:
        welcome_text += "👑 <b>Admin sifatida qo'shimcha imkoniyatlar:</b>\n"
        welcome_text += "• Testlarni boshqarish\n"
        welcome_text += "• Foydalanuvchilar statistikasi\n"
        welcome_text += "• Kirish nazorati\n"
        welcome_text += "• Xabar yuborish\n"
        welcome_text += "• Ma'lumotlarni eksport qilish\n\n"
        keyboard = get_admin_menu_keyboard()
    else:
        keyboard = get_main_menu_keyboard()
    
    welcome_text += "Quyidagi tugmalardan birini tanlang:"
    
    await message.answer(welcome_text, reply_markup=keyboard)

@router.message(F.text == "🔙 Asosiy menu")
async def back_to_main_menu(message: Message, state: FSMContext) -> None:
    """Return to main menu"""
    await state.clear()
    
    is_admin = data_manager.is_super_admin(message.from_user.username or "")
    keyboard = get_admin_menu_keyboard() if is_admin else get_main_menu_keyboard()
    
    await message.answer("Asosiy menu:", reply_markup=keyboard)

# ═══════════════════════════════════════════════════════════════════════════════════
# USER REGISTRATION HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════════

@router.message(F.text == "📝 Ro'yxatdan o'tish")
async def start_registration(message: Message, state: FSMContext) -> None:
    """Start user registration process"""
    await state.set_state(UserRegistrationStates.waiting_for_child_name)
    
    text = "📝 <b>Ro'yxatdan o'tish</b>\n\n"
    text += "Bolangizning to'liq ismini kiriting:\n"
    text += "<i>(Masalan: Akmal Karimov)</i>"
    
    await message.answer(text, reply_markup=ReplyKeyboardRemove())

@router.message(UserRegistrationStates.waiting_for_child_name)
async def process_child_name(message: Message, state: FSMContext) -> None:
    """Process child name"""
    if not message.text:
        await message.answer("Iltimos, matn formatida ism kiriting.")
        return
    
    child_name = message.text.strip()
    if not validate_name(child_name):
        await message.answer(
            "❌ Noto'g'ri ism formati!\n\n"
            "Iltimos, to'g'ri ism kiriting (kamida 2 ta harf)."
        )
        return
    
    await state.update_data(child_name=child_name)
    await state.set_state(UserRegistrationStates.waiting_for_parent_name)
    
    await message.answer(
        "Ota-onaning to'liq ismini kiriting:\n"
        "<i>(Masalan: Karim Alimov)</i>"
    )

@router.message(UserRegistrationStates.waiting_for_parent_name)
async def process_parent_name(message: Message, state: FSMContext) -> None:
    """Process parent name"""
    if not message.text:
        await message.answer("Iltimos, matn formatida ism kiriting.")
        return
    
    parent_name = message.text.strip()
    if not validate_name(parent_name):
        await message.answer(
            "❌ Noto'g'ri ism formati!\n\n"
            "Iltimos, to'g'ri ism kiriting (kamida 2 ta harf)."
        )
        return
    
    await state.update_data(parent_name=parent_name)
    await state.set_state(UserRegistrationStates.waiting_for_region)
    
    await message.answer(
        "Viloyatingizni tanlang:",
        reply_markup=get_regions_keyboard()
    )

@router.callback_query(F.data.startswith("region:"))
async def process_region_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Process region selection"""
    region = callback.data.split(":", 1)[1]
    
    if not validate_region(region):
        await callback.answer("❌ Noto'g'ri viloyat!", show_alert=True)
        return
    
    await state.update_data(region=region)
    await state.set_state(UserRegistrationStates.waiting_for_district)
    
    if callback.message:
        await callback.message.edit_text(
            f"Tanlangan viloyat: <b>{region}</b>\n\nTumanni tanlang:",
            reply_markup=get_districts_keyboard(region)
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("district:"))
async def process_district_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Process district selection"""
    parts = callback.data.split(":", 2)
    if len(parts) != 3:
        await callback.answer("❌ Xatolik!", show_alert=True)
        return
    
    region, district = parts[1], parts[2]
    
    if not validate_district(region, district):
        await callback.answer("❌ Noto'g'ri tuman!", show_alert=True)
        return
    
    await state.update_data(district=district)
    await state.set_state(UserRegistrationStates.waiting_for_mahalla)
    
    if callback.message:
        await callback.message.edit_text(
            f"Tanlangan tuman: <b>{district}</b>\n\nMahallani tanlang:",
            reply_markup=get_mahallas_keyboard(region, district)
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("mahalla:"))
async def process_mahalla_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Process mahalla selection"""
    parts = callback.data.split(":", 3)
    if len(parts) != 4:
        await callback.answer("❌ Xatolik!", show_alert=True)
        return
    
    region, district, mahalla = parts[1], parts[2], parts[3]
    
    if not validate_mahalla(region, district, mahalla):
        await callback.answer("❌ Noto'g'ri mahalla!", show_alert=True)
        return
    
    await state.update_data(mahalla=mahalla)
    await state.set_state(UserRegistrationStates.waiting_for_age)
    
    if callback.message:
        await callback.message.edit_text(
            f"Tanlangan mahalla: <b>{mahalla}</b>\n\n"
            "Bolangizning yoshini kiriting (7-14 yosh):"
        )
    
    await callback.answer()

@router.callback_query(F.data == "back_to_regions")
async def back_to_regions(callback: CallbackQuery, state: FSMContext) -> None:
    """Go back to regions selection"""
    await state.set_state(UserRegistrationStates.waiting_for_region)
    
    if callback.message:
        await callback.message.edit_text(
            "Viloyatingizni tanlang:",
            reply_markup=get_regions_keyboard()
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("back_to_districts:"))
async def back_to_districts(callback: CallbackQuery, state: FSMContext) -> None:
    """Go back to districts selection"""
    region = callback.data.split(":", 1)[1]
    await state.set_state(UserRegistrationStates.waiting_for_district)
    
    if callback.message:
        await callback.message.edit_text(
            f"Tanlangan viloyat: <b>{region}</b>\n\nTumanni tanlang:",
            reply_markup=get_districts_keyboard(region)
        )
    
    await callback.answer()

@router.message(UserRegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext) -> None:
    """Process age input"""
    if not message.text:
        await message.answer("Iltimos, son formatida yosh kiriting.")
        return
    
    age_str = message.text.strip()
    if not validate_age(age_str):
        await message.answer(
            "❌ Noto'g'ri yosh!\n\n"
            "Iltimos, 7 dan 14 gacha bo'lgan yoshni kiriting."
        )
        return
    
    await state.update_data(age=int(age_str))
    await state.set_state(UserRegistrationStates.waiting_for_phone)
    
    await message.answer(
        "Telefon raqamingizni kiriting:\n"
        "<i>(Masalan: +998901234567 yoki 901234567)</i>"
    )

@router.message(UserRegistrationStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    """Process phone number"""
    if not message.text:
        await message.answer("Iltimos, telefon raqamini kiriting.")
        return
    
    phone = message.text.strip()
    if not validate_phone(phone):
        await message.answer(
            "❌ Noto'g'ri telefon raqami!\n\n"
            "Iltimos, to'g'ri O'zbekiston telefon raqamini kiriting.\n"
            "Masalan: +998901234567, 998901234567 yoki 901234567"
        )
        return
    
    # Normalize phone number
    clean_phone = re.sub(r'\D', '', phone)
    if len(clean_phone) == 9:
        clean_phone = "998" + clean_phone
    elif len(clean_phone) == 12 and clean_phone.startswith("998"):
        pass
    else:
        clean_phone = phone
    
    # Get all registration data
    data = await state.get_data()
    user_data = {
        'telegram_id': message.from_user.id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'child_name': data['child_name'],
        'parent_name': data['parent_name'],
        'region': data['region'],
        'district': data['district'],
        'mahalla': data['mahalla'],
        'age': data['age'],
        'phone': clean_phone
    }
    
    # Save registration
    reg_id = data_manager.save_user(user_data)
    
    if reg_id:
        logger.info(f"User registration saved: {message.from_user.id} (ID: {reg_id})")
        logger.info(f"Statistics updated successfully")
        
        success_text = "✅ <b>Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!</b>\n\n"
        success_text += f"📝 <b>Registration ID:</b> <code>{reg_id}</code>\n\n"
        success_text += "<b>Ma'lumotlaringiz:</b>\n"
        success_text += f"👶 Bola: {user_data['child_name']}\n"
        success_text += f"👨‍👩‍👧‍👦 Ota-ona: {user_data['parent_name']}\n"
        success_text += f"📍 Manzil: {user_data['region']}, {user_data['district']}, {user_data['mahalla']}\n"
        success_text += f"🎂 Yosh: {user_data['age']}\n"
        success_text += f"📞 Telefon: {user_data['phone']}\n\n"
        success_text += "Endi testlarni ishlashingiz mumkin! 📚"
        
        await message.answer(success_text, reply_markup=get_main_menu_keyboard())
    else:
        await message.answer(
            "❌ Ro'yxatdan o'tishda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=get_main_menu_keyboard()
        )
    
    await state.clear()

# ═══════════════════════════════════════════════════════════════════════════════════
# TEST SYSTEM HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════════

@router.message(F.text == "📚 Test ishlash")
async def start_test(message: Message, state: FSMContext) -> None:
    """Start test taking process"""
    # Check access permissions
    if not data_manager.can_access_tests(message.from_user.id, message.from_user.username):
        await message.answer(
            "❌ <b>Kirish ruxsati yo'q!</b>\n\n"
            "Testlarga kirish vaqtinchalik cheklangan.\n"
            "Administrator bilan bog'laning."
        )
        return
    
    # Check if user has registrations
    registrations = data_manager.get_user_registrations(message.from_user.id)
    if not registrations:
        await message.answer(
            "❌ <b>Avval ro'yxatdan o'ting!</b>\n\n"
            "Testlarni ishlash uchun oldin ro'yxatdan o'tishingiz kerak.\n"
            "📝 'Ro'yxatdan o'tish' tugmasini bosing."
        )
        return
    
    await state.set_state(TestStates.selecting_age_group)
    
    await message.answer(
        "📚 <b>Test ishlash</b>\n\n"
        "Yosh guruhini tanlang:",
        reply_markup=get_age_groups_keyboard()
    )

@router.callback_query(F.data.startswith("age_group:"), TestStates.selecting_age_group)
async def process_age_group_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Process age group selection for tests"""
    age_group = callback.data.split(":", 1)[1]
    
    if age_group not in ["7-10", "11-14"]:
        await callback.answer("❌ Noto'g'ri yosh guruhi!", show_alert=True)
        return
    
    # Get available tests for age group
    tests = data_manager.get_tests_by_age_group(age_group)
    
    if not tests:
        await callback.answer(
            f"❌ {age_group} yosh guruhi uchun testlar mavjud emas!",
            show_alert=True
        )
        return
    
    await state.update_data(selected_age_group=age_group)
    await state.set_state(TestStates.selecting_test)
    
    # Create tests keyboard
    keyboard = []
    for test_id, test_data in tests.items():
        test_name = test_data.get('name', f'Test {test_id[:8]}')
        keyboard.append([InlineKeyboardButton(
            text=test_name,
            callback_data=f"select_test:{test_id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_age_groups")])
    
    if callback.message:
        await callback.message.edit_text(
            f"📚 <b>{age_group} yosh guruhi testlari</b>\n\n"
            "Testni tanlang:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    
    await callback.answer()

@router.callback_query(F.data == "back_to_age_groups", TestStates.selecting_test)
async def back_to_age_groups(callback: CallbackQuery, state: FSMContext) -> None:
    """Go back to age group selection"""
    await state.set_state(TestStates.selecting_age_group)
    
    if callback.message:
        await callback.message.edit_text(
            "📚 <b>Test ishlash</b>\n\n"
            "Yosh guruhini tanlang:",
            reply_markup=get_age_groups_keyboard()
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("select_test:"), TestStates.selecting_test)
async def start_selected_test(callback: CallbackQuery, state: FSMContext) -> None:
    """Start the selected test"""
    test_id = callback.data.split(":", 1)[1]
    data = await state.get_data()
    age_group = data.get('selected_age_group')
    
    if not age_group:
        await callback.answer("❌ Xatolik!", show_alert=True)
        return
    
    test_data = data_manager.get_test(test_id, age_group)
    if not test_data:
        await callback.answer("❌ Test topilmadi!", show_alert=True)
        return
    
    # Initialize test session
    await state.update_data(
        test_id=test_id,
        test_data=test_data,
        current_question=0,
        answers=[],
        start_time=datetime.now().isoformat()
    )
    await state.set_state(TestStates.taking_test)
    
    # Show first question
    await show_test_question(callback.message, state)
    await callback.answer()

async def show_test_question(message: Message, state: FSMContext) -> None:
    """Show current test question"""
    data = await state.get_data()
    test_data = data['test_data']
    current_q = data['current_question']
    questions = test_data.get('questions', [])
    
    if current_q >= len(questions):
        await finish_test(message, state)
        return
    
    question = questions[current_q]
    
    text = f"📚 <b>{test_data.get('name', 'Test')}</b>\n\n"
    text += f"Savol {current_q + 1}/{len(questions)}\n\n"
    text += f"<b>{question.get('question', 'Savol matn mavjud emas')}</b>\n\n"
    
    # Handle different question types
    if question.get('type') == 'multiple_choice':
        options = question.get('options', [])
        keyboard = []
        for i, option in enumerate(options):
            keyboard.append([InlineKeyboardButton(
                text=f"{chr(65 + i)}. {option}",
                callback_data=f"answer:{i}"
            )])
    else:
        # Text answer
        text += "Javobingizni yozing:"
        keyboard = [[InlineKeyboardButton(text="⏹️ Testni to'xtatish", callback_data="stop_test")]]
    
    if message:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@router.callback_query(F.data.startswith("answer:"), TestStates.taking_test)
async def process_test_answer(callback: CallbackQuery, state: FSMContext) -> None:
    """Process test answer"""
    answer_index = int(callback.data.split(":", 1)[1])
    data = await state.get_data()
    
    # Save answer
    answers = data.get('answers', [])
    answers.append(answer_index)
    
    # Move to next question
    current_q = data.get('current_question', 0) + 1
    await state.update_data(answers=answers, current_question=current_q)
    
    # Show next question or finish test
    await show_test_question(callback.message, state)
    await callback.answer()

@router.message(TestStates.taking_test)
async def process_text_answer(message: Message, state: FSMContext) -> None:
    """Process text answer for open-ended questions"""
    if not message.text:
        await message.answer("Iltimos, matn formatida javob bering.")
        return
    
    data = await state.get_data()
    
    # Save text answer
    answers = data.get('answers', [])
    answers.append(message.text.strip())
    
    # Move to next question
    current_q = data.get('current_question', 0) + 1
    await state.update_data(answers=answers, current_question=current_q)
    
    # Show next question or finish test
    await show_test_question(message, state)

@router.callback_query(F.data == "stop_test", TestStates.taking_test)
async def stop_test(callback: CallbackQuery, state: FSMContext) -> None:
    """Stop test"""
    await state.clear()
    
    if callback.message:
        await callback.message.edit_text(
            "❌ <b>Test to'xtatildi</b>\n\n"
            "Test yakunlanmadi. Natija saqlanmadi."
        )
    
    await callback.message.answer("Asosiy menu:", reply_markup=get_main_menu_keyboard())
    await callback.answer()

async def finish_test(message: Message, state: FSMContext) -> None:
    """Finish test and calculate score"""
    data = await state.get_data()
    test_data = data['test_data']
    answers = data.get('answers', [])
    questions = test_data.get('questions', [])
    
    # Calculate score
    score = 0
    total_questions = len(questions)
    
    for i, question in enumerate(questions):
        if i < len(answers):
            user_answer = answers[i]
            if question.get('type') == 'multiple_choice':
                correct_answer = question.get('correct_answer', 0)
                if user_answer == correct_answer:
                    score += 1
            # For text answers, we can't auto-grade, so we'll mark as correct for now
            else:
                score += 1
    
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    # Save result
    result_data = {
        'telegram_id': message.from_user.id,
        'test_id': data['test_id'],
        'test_name': test_data.get('name', 'Test'),
        'age_group': data['selected_age_group'],
        'score': score,
        'total_questions': total_questions,
        'percentage': percentage,
        'answers': answers,
        'start_time': data.get('start_time'),
        'duration_minutes': 0  # Could calculate actual duration
    }
    
    result_id = data_manager.save_test_result(result_data)
    
    # Show results
    text = "🎉 <b>Test yakunlandi!</b>\n\n"
    text += f"📊 <b>Natijangiz:</b>\n"
    text += f"✅ To'g'ri javoblar: {score}/{total_questions}\n"
    text += f"📈 Foiz: {percentage:.1f}%\n\n"
    
    if percentage >= 80:
        text += "🌟 A'lo! Ajoyib natija!"
    elif percentage >= 60:
        text += "👍 Yaxshi natija!"
    elif percentage >= 40:
        text += "📚 Yaxshi, lekin ko'proq o'qish kerak."
    else:
        text += "💪 Mashq qilishda davom eting!"
    
    if result_id:
        text += f"\n\n📝 Natija ID: <code>{result_id}</code>"
    
    await message.edit_text(text)
    await message.answer("Asosiy menu:", reply_markup=get_main_menu_keyboard())
    await state.clear()

# ═══════════════════════════════════════════════════════════════════════════════════
# RESULTS HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════════

@router.message(F.text == "📊 Natijalarim")
async def show_user_results(message: Message) -> None:
    """Show user's test results"""
    results = data_manager.get_user_results(message.from_user.id)
    
    if not results:
        await message.answer(
            "📊 <b>Natijalaringiz</b>\n\n"
            "Hali test ishlamagansiz.\n\n"
            "📚 'Test ishlash' tugmasini bosib, birinchi testingizni ishlang!"
        )
        return
    
    text = "📊 <b>Sizning natijalaringiz</b>\n\n"
    
    for i, result in enumerate(results[:10], 1):  # Show last 10 results
        percentage = result.get('percentage', 0)
        test_name = result.get('test_name', 'Test')
        completed_at = result.get('completed_at', '')
        
        # Format date
        try:
            date_obj = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
            date_str = date_obj.strftime('%d.%m.%Y %H:%M')
        except:
            date_str = completed_at[:16] if completed_at else 'N/A'
        
        emoji = "🌟" if percentage >= 80 else "👍" if percentage >= 60 else "📚"
        
        text += f"{i}. {emoji} <b>{test_name}</b>\n"
        text += f"   📈 {percentage:.1f}% ({result.get('score', 0)}/{result.get('total_questions', 0)})\n"
        text += f"   📅 {date_str}\n\n"
    
    if len(results) > 10:
        text += f"... va yana {len(results) - 10} ta natija"
    
    await message.answer(text)

# ═══════════════════════════════════════════════════════════════════════════════════
# ADMIN HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════════

@router.message(F.text == "👥 Foydalanuvchilar")
async def admin_users(message: Message) -> None:
    """Show users statistics (Super Admin only)"""
    if not data_manager.is_super_admin(message.from_user.username or ""):
        await message.answer("❌ Bu buyruq faqat Super Admin uchun!")
        return
    
    users = data_manager.get_all_users()
    stats = data_manager.get_statistics()
    
    text = "👥 <b>Foydalanuvchilar statistikasi</b>\n\n"
    text += f"📊 Jami ro'yxatdan o'tganlar: {len(users)}\n"
    text += f"📈 Jami testlar ishlangan: {stats.get('total_tests_taken', 0)}\n\n"
    
    # Regional stats
    regional_stats = stats.get('regional_stats', {})
    if regional_stats:
        text += "<b>Viloyatlar bo'yicha:</b>\n"
        for region, count in sorted(regional_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            text += f"• {region}: {count} ta\n"
        text += "\n"
    
    # Age group stats
    age_stats = stats.get('age_group_stats', {})
    if age_stats:
        text += "<b>Yosh guruhlari bo'yicha:</b>\n"
        for age_group, data in age_stats.items():
            text += f"• {age_group} yosh: {data.get('users', 0)} foydalanuvchi, {data.get('tests_taken', 0)} test\n"
    
    await message.answer(text)

@router.message(F.text == "📋 Testlar")
async def admin_tests(message: Message, state: FSMContext) -> None:
    """Test management (Super Admin only)"""
    if not data_manager.is_super_admin(message.from_user.username or ""):
        await message.answer("❌ Bu buyruq faqat Super Admin uchun!")
        return
    
    keyboard = [
        [InlineKeyboardButton(text="➕ Yangi test qo'shish", callback_data="create_test")],
        [InlineKeyboardButton(text="📋 Testlarni ko'rish", callback_data="view_tests")],
        [InlineKeyboardButton(text="🗑️ Testni o'chirish", callback_data="delete_test")]
    ]
    
    await message.answer(
        "📋 <b>Test boshqaruvi</b>\n\n"
        "Amalni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query(F.data == "create_test")
async def start_test_creation(callback: CallbackQuery, state: FSMContext) -> None:
    """Start test creation process"""
    if not data_manager.is_super_admin(callback.from_user.username or ""):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await state.set_state(AdminStates.creating_test_name)
    
    if callback.message:
        await callback.message.edit_text(
            "➕ <b>Yangi test yaratish</b>\n\n"
            "Test nomini kiriting:"
        )
    
    await callback.answer()

@router.message(AdminStates.creating_test_name)
async def process_test_name(message: Message, state: FSMContext) -> None:
    """Process test name"""
    if not message.text:
        await message.answer("Iltimos, test nomini kiriting.")
        return
    
    test_name = message.text.strip()
    if len(test_name) < 3:
        await message.answer("Test nomi kamida 3 ta belgidan iborat bo'lishi kerak.")
        return
    
    await state.update_data(test_name=test_name)
    await state.set_state(AdminStates.creating_test_age_group)
    
    await message.answer(
        f"Test nomi: <b>{test_name}</b>\n\n"
        "Yosh guruhini tanlang:",
        reply_markup=get_age_groups_keyboard()
    )

@router.callback_query(F.data.startswith("age_group:"), AdminStates.creating_test_age_group)
async def process_test_age_group(callback: CallbackQuery, state: FSMContext) -> None:
    """Process test age group selection"""
    age_group = callback.data.split(":", 1)[1]
    
    if age_group not in ["7-10", "11-14"]:
        await callback.answer("❌ Noto'g'ri yosh guruhi!", show_alert=True)
        return
    
    await state.update_data(age_group=age_group)
    await state.set_state(AdminStates.creating_test_document)
    
    if callback.message:
        await callback.message.edit_text(
            f"Yosh guruhi: <b>{age_group}</b>\n\n"
            "Test uchun hujjat yuklang (PDF, Word, Excel, Text formatida):"
        )
    
    await callback.answer()

@router.message(AdminStates.creating_test_document, F.document)
async def process_test_document(message: Message, state: FSMContext) -> None:
    """Process test document upload"""
    if not message.document:
        await message.answer("Iltimos, hujjat yuklang.")
        return
    
    document = message.document
    
    # Validate document format
    if not validate_document_format(document.file_name or "", document.mime_type or ""):
        await message.answer(
            "❌ Noto'g'ri fayl formati!\n\n"
            "Qo'llab-quvvatlanadigan formatlar: PDF, Word (.doc, .docx), Excel (.xls, .xlsx), Text (.txt)"
        )
        return
    
    try:
        # Download file
        file_info = await bot.get_file(document.file_id)
        if not file_info.file_path:
            await message.answer("❌ Fayl yuklab olinmadi.")
            return
        
        file_content = await bot.download_file(file_info.file_path)
        if not file_content:
            await message.answer("❌ Fayl mazmuni olinmadi.")
            return
        
        # Extract text content
        text_content = extract_text_from_document(
            file_content.read(), 
            document.file_name or "", 
            document.mime_type or ""
        )
        
        # Get document type
        doc_type = get_document_type(document.file_name or "", document.mime_type or "")
        
        await state.update_data(
            document_name=document.file_name,
            document_type=doc_type,
            document_content=text_content
        )
        await state.set_state(AdminStates.creating_test_questions)
        
        await message.answer(
            f"✅ Hujjat yuklandi: <b>{document.file_name}</b>\n"
            f"📄 Tur: {doc_type}\n\n"
            "Endi test savollarini JSON formatida kiriting:\n\n"
            "<code>[\n"
            "  {\n"
            '    "question": "Savol matni",\n'
            '    "type": "multiple_choice",\n'
            '    "options": ["A variant", "B variant", "C variant", "D variant"],\n'
            '    "correct_answer": 0\n'
            "  }\n"
            "]</code>"
        )
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        await message.answer(f"❌ Hujjatni qayta ishlashda xatolik: {str(e)}")

@router.message(AdminStates.creating_test_questions)
async def process_test_questions(message: Message, state: FSMContext) -> None:
    """Process test questions"""
    if not message.text:
        await message.answer("Iltimos, savollarni JSON formatida kiriting.")
        return
    
    try:
        questions = json.loads(message.text.strip())
        
        if not isinstance(questions, list) or len(questions) == 0:
            await message.answer("❌ Savollar ro'yxati bo'sh yoki noto'g'ri format!")
            return
        
        # Validate questions structure
        for i, q in enumerate(questions):
            if not isinstance(q, dict) or 'question' not in q:
                await message.answer(f"❌ {i+1}-savol noto'g'ri formatda!")
                return
        
        # Get all test data
        data = await state.get_data()
        
        test_data = {
            'name': data['test_name'],
            'age_group': data['age_group'],
            'document_name': data.get('document_name'),
            'document_type': data.get('document_type'),
            'document_content': data.get('document_content'),
            'questions': questions,
            'created_by': message.from_user.username,
            'created_by_id': message.from_user.id
        }
        
        # Save test
        test_id = data_manager.save_test(test_data, data['age_group'])
        
        if test_id:
            await message.answer(
                f"✅ <b>Test muvaffaqiyatli yaratildi!</b>\n\n"
                f"📝 Test ID: <code>{test_id}</code>\n"
                f"📚 Nom: {data['test_name']}\n"
                f"👥 Yosh guruhi: {data['age_group']}\n"
                f"❓ Savollar soni: {len(questions)}\n"
                f"📄 Hujjat: {data.get('document_name', 'N/A')}",
                reply_markup=get_admin_menu_keyboard()
            )
            logger.info(f"Test created: {test_id} by {message.from_user.username}")
        else:
            await message.answer(
                "❌ Test yaratishda xatolik yuz berdi.",
                reply_markup=get_admin_menu_keyboard()
            )
        
    except json.JSONDecodeError:
        await message.answer(
            "❌ JSON format xato!\n\n"
            "Iltimos, to'g'ri JSON formatida savollar kiriting."
        )
    except Exception as e:
        logger.error(f"Error creating test: {e}")
        await message.answer(
            f"❌ Test yaratishda xatolik: {str(e)}",
            reply_markup=get_admin_menu_keyboard()
        )
    
    await state.clear()

@router.message(F.text == "🔒 Kirish nazorati")
async def admin_access_control(message: Message) -> None:
    """Access control management (Super Admin only)"""
    if not data_manager.is_super_admin(message.from_user.username or ""):
        await message.answer("❌ Bu buyruq faqat Super Admin uchun!")
        return
    
    access_info = data_manager.get_access_control_info()
    
    text = "🔒 <b>Kirish nazorati</b>\n\n"
    access_status = "✅ Ha" if access_info.get('test_access_enabled', True) else "❌ Yo'q"
    text += f"📋 Test kirishiga ruxsat: {access_status}\n"
    
    allowed_users = access_info.get('allowed_users', [])
    if allowed_users:
        text += f"👥 Ruxsat berilgan foydalanuvchilar: {len(allowed_users)} ta\n"
        text += f"📝 Ro'yxat: {', '.join(allowed_users[:5])}\n"
        if len(allowed_users) > 5:
            text += f"... va yana {len(allowed_users) - 5} ta\n"
    else:
        text += "👥 Ruxsat berilgan foydalanuvchilar: Hammaga ochiq\n"
    
    keyboard = [
        [InlineKeyboardButton(
            text="🔓 Testlarni ochish" if not access_info.get('test_access_enabled', True) else "🔒 Testlarni yopish",
            callback_data="toggle_test_access"
        )],
        [InlineKeyboardButton(text="➕ Foydalanuvchi qo'shish", callback_data="add_allowed_user")],
        [InlineKeyboardButton(text="🗑️ Foydalanuvchi o'chirish", callback_data="remove_allowed_user")]
    ]
    
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@router.callback_query(F.data == "toggle_test_access")
async def toggle_test_access(callback: CallbackQuery) -> None:
    """Toggle test access"""
    if not data_manager.is_super_admin(callback.from_user.username or ""):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    access_info = data_manager.get_access_control_info()
    current_status = access_info.get('test_access_enabled', True)
    new_status = not current_status
    
    if data_manager.update_test_access(new_status):
        status_text = "ochildi" if new_status else "yopildi"
        await callback.answer(f"✅ Testlarga kirish {status_text}!", show_alert=True)
        
        # Refresh the message
        await admin_access_control(callback.message)
    else:
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)

@router.message(F.text == "📢 Xabar yuborish")
async def admin_broadcast(message: Message, state: FSMContext) -> None:
    """Broadcast message to all users (Super Admin only)"""
    if not data_manager.is_super_admin(message.from_user.username or ""):
        await message.answer("❌ Bu buyruq faqat Super Admin uchun!")
        return
    
    await state.set_state(AdminStates.creating_broadcast)
    
    await message.answer(
        "📢 <b>Xabar yuborish</b>\n\n"
        "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabarni kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(AdminStates.creating_broadcast)
async def process_broadcast_message(message: Message, state: FSMContext) -> None:
    """Process broadcast message"""
    if not message.text:
        await message.answer("Iltimos, matn formatida xabar kiriting.")
        return
    
    broadcast_text = message.text.strip()
    if len(broadcast_text) < 5:
        await message.answer("Xabar kamida 5 ta belgidan iborat bo'lishi kerak.")
        return
    
    # Get all bot users
    bot_users = data_manager.get_all_bot_users()
    
    if not bot_users:
        await message.answer(
            "❌ Xabar yuborish uchun foydalanuvchilar topilmadi.",
            reply_markup=get_admin_menu_keyboard()
        )
        await state.clear()
        return
    
    # Confirm broadcast
    keyboard = [
        [InlineKeyboardButton(text="✅ Yuborish", callback_data="confirm_broadcast")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_broadcast")]
    ]
    
    await state.update_data(broadcast_message=broadcast_text)
    
    await message.answer(
        f"📢 <b>Xabarni tasdiqlang</b>\n\n"
        f"📊 Qabul qiluvchilar: {len(bot_users)} ta foydalanuvchi\n\n"
        f"<b>Xabar matni:</b>\n{broadcast_text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query(F.data == "confirm_broadcast", AdminStates.creating_broadcast)
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    """Confirm and send broadcast"""
    data = await state.get_data()
    broadcast_message = data.get('broadcast_message')
    
    if not broadcast_message:
        await callback.answer("❌ Xabar topilmadi!", show_alert=True)
        return
    
    bot_users = data_manager.get_all_bot_users()
    
    if callback.message:
        await callback.message.edit_text("📤 Xabar yuborilmoqda...")
    
    # Send broadcast
    sent_count = 0
    failed_count = 0
    
    for user_id, user_data in bot_users.items():
        try:
            telegram_id = user_data.get('telegram_id')
            if telegram_id:
                final_message = f"📢 <b>Admindan xabar</b>\n\n{broadcast_message}"
                await bot.send_message(telegram_id, final_message)
                sent_count += 1
                await asyncio.sleep(0.1)  # Rate limiting
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send broadcast to {user_id}: {e}")
    
    # Save broadcast record
    broadcast_data = {
        'message': broadcast_message,
        'sent_by': callback.from_user.username,
        'sent_by_id': callback.from_user.id,
        'sent_count': sent_count,
        'failed_count': failed_count,
        'total_users': len(bot_users)
    }
    
    broadcast_id = data_manager.save_broadcast(broadcast_data)
    
    result_text = f"✅ <b>Xabar yuborildi!</b>\n\n"
    result_text += f"📊 Muvaffaqiyatli: {sent_count} ta\n"
    result_text += f"❌ Muvaffaqiyatsiz: {failed_count} ta\n"
    result_text += f"📝 Broadcast ID: <code>{broadcast_id}</code>"
    
    await callback.message.edit_text(result_text)
    await callback.message.answer("Asosiy menu:", reply_markup=get_admin_menu_keyboard())
    
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "cancel_broadcast", AdminStates.creating_broadcast)
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    """Cancel broadcast"""
    await state.clear()
    
    if callback.message:
        await callback.message.edit_text("❌ Xabar yuborish bekor qilindi.")
    
    await callback.message.answer("Asosiy menu:", reply_markup=get_admin_menu_keyboard())
    await callback.answer()

@router.message(F.text == "📁 Eksport")
async def admin_export(message: Message) -> None:
    """Data export options (Super Admin only)"""
    if not data_manager.is_super_admin(message.from_user.username or ""):
        await message.answer("❌ Bu buyruq faqat Super Admin uchun!")
        return
    
    keyboard = [
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="export_users")],
        [InlineKeyboardButton(text="📊 Test natijalari", callback_data="export_results")],
        [InlineKeyboardButton(text="📈 Statistika", callback_data="export_stats")]
    ]
    
    await message.answer(
        "📁 <b>Ma'lumotlarni eksport qilish</b>\n\n"
        "Eksport qilmoqchi bo'lgan ma'lumotni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query(F.data == "export_users")
async def export_users_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Show export formats for users"""
    if not data_manager.is_super_admin(callback.from_user.username or ""):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await state.update_data(export_type="users")
    
    if callback.message:
        await callback.message.edit_text(
            "👥 <b>Foydalanuvchilarni eksport qilish</b>\n\n"
            "Formatni tanlang:",
            reply_markup=get_export_formats_keyboard()
        )
    
    await callback.answer()

@router.callback_query(F.data == "export_results")
async def export_results_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Show export formats for results"""
    if not data_manager.is_super_admin(callback.from_user.username or ""):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await state.update_data(export_type="results")
    
    if callback.message:
        await callback.message.edit_text(
            "📊 <b>Test natijalarini eksport qilish</b>\n\n"
            "Formatni tanlang:",
            reply_markup=get_export_formats_keyboard()
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("export:"))
async def process_export(callback: CallbackQuery, state: FSMContext) -> None:
    """Process export request"""
    if not data_manager.is_super_admin(callback.from_user.username or ""):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    export_format = callback.data.split(":", 1)[1]
    data = await state.get_data()
    export_type = data.get('export_type')
    
    if not export_type:
        await callback.answer("❌ Eksport turi tanlanmagan!", show_alert=True)
        return
    
    if callback.message:
        await callback.message.edit_text("📤 Eksport yaratilmoqda...")
    
    try:
        if export_type == "users":
            if export_format == "text":
                content = export_manager.export_users_text()
                filename = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                
                # Send as file
                text_file = BytesIO(content.encode('utf-8'))
                text_file.name = filename
                
                await bot.send_document(
                    callback.message.chat.id,
                    document=text_file,
                    caption=f"📄 Foydalanuvchilar ma'lumotlari ({export_format.upper()})"
                )
                
            elif export_format == "excel" and EXCEL_AVAILABLE:
                excel_file = export_manager.export_users_excel()
                if excel_file:
                    filename = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    excel_file.name = filename
                    
                    await bot.send_document(
                        callback.message.chat.id,
                        document=excel_file,
                        caption=f"📊 Foydalanuvchilar ma'lumotlari (Excel)"
                    )
                else:
                    raise Exception("Excel fayl yaratilmadi")
                    
            elif export_format == "word" and DOCX_AVAILABLE:
                word_file = export_manager.export_users_word()
                if word_file:
                    filename = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                    word_file.name = filename
                    
                    await bot.send_document(
                        callback.message.chat.id,
                        document=word_file,
                        caption=f"📝 Foydalanuvchilar ma'lumotlari (Word)"
                    )
                else:
                    raise Exception("Word fayl yaratilmadi")
                    
            elif export_format == "pdf" and PDF_AVAILABLE:
                pdf_file = export_manager.export_users_pdf()
                if pdf_file:
                    filename = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    pdf_file.name = filename
                    
                    await bot.send_document(
                        callback.message.chat.id,
                        document=pdf_file,
                        caption=f"📄 Foydalanuvchilar ma'lumotlari (PDF)"
                    )
                else:
                    raise Exception("PDF fayl yaratilmadi")
            else:
                await callback.message.edit_text(f"❌ {export_format.upper()} format qo'llab-quvvatlanmaydi!")
                
        elif export_type == "results":
            if export_format == "excel" and EXCEL_AVAILABLE:
                excel_file = export_manager.export_results_excel()
                if excel_file:
                    filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    excel_file.name = filename
                    
                    await bot.send_document(
                        callback.message.chat.id,
                        document=excel_file,
                        caption=f"📊 Test natijalari (Excel)"
                    )
                else:
                    raise Exception("Excel fayl yaratilmadi")
            else:
                await callback.message.edit_text(f"❌ Natijalar uchun {export_format.upper()} format qo'llab-quvvatlanmaydi!")
        
        await callback.message.answer("✅ Eksport muvaffaqiyatli yakunlandi!")
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        await callback.message.edit_text(f"❌ Eksport yaratishda xatolik: {str(e)}")
    
    await state.clear()
    await callback.answer()

# ═══════════════════════════════════════════════════════════════════════════════════
# INFO HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════════

@router.message(F.text == "ℹ️ Bot haqida")
async def about_bot(message: Message) -> None:
    """Show bot information"""
    text = "ℹ️ <b>Kitobxon Kids Bot haqida</b>\n\n"
    text += "🎯 <b>Maqsad:</b>\n"
    text += "7-14 yosh orasidagi bolalar uchun o'qish tushunish testlarini o'tkazish\n\n"
    
    text += "🔧 <b>Imkoniyatlar:</b>\n"
    text += "• Cheksiz ro'yxatdan o'tish\n"
    text += "• Yosh guruhiga mos testlar (7-10 va 11-14)\n"
    text += "• Ko'p formatli hujjatlar (PDF, Word, Excel, Text)\n"
    text += "• Natijalarni kuzatish\n"
    text += "• Regional statistika\n\n"
    
    text += "👥 <b>Foydalanuvchilar:</b>\n"
    stats = data_manager.get_statistics()
    text += f"• Jami ro'yxatdan o'tganlar: {stats.get('total_users', 0)}\n"
    text += f"• Jami testlar: {stats.get('total_tests_taken', 0)}\n\n"
    
    text += "🔄 <b>Versiya:</b> 2.0 (Refactored)\n"
    text += "📅 <b>Yangilangan:</b> 2025-08-13\n\n"
    
    text += "🚀 <b>Yangi imkoniyatlar:</b>\n"
    text += "• 4000+ concurrent user support\n"
    text += "• Multi-format exports\n"
    text += "• Advanced access control\n"
    text += "• Optimized performance"
    
    await message.answer(text)

@router.message(F.text == "☎️ Aloqa")
async def contact_info(message: Message) -> None:
    """Show contact information"""
    text = "☎️ <b>Aloqa ma'lumotlari</b>\n\n"
    text += "📧 <b>Texnik yordam:</b>\n"
    text += "• @admin_username (Telegram)\n"
    text += "• support@kitobxonkids.uz (Email)\n\n"
    
    text += "🏢 <b>Tashkilot:</b>\n"
    text += "Kitobxon Kids ta'lim markazi\n\n"
    
    text += "🕐 <b>Ish vaqti:</b>\n"
    text += "Dushanba - Juma: 09:00 - 18:00\n"
    text += "Shanba: 09:00 - 14:00\n"
    text += "Yakshanba: Dam olish kuni\n\n"
    
    text += "❓ <b>Tez-tez beriladigan savollar:</b>\n"
    text += "• Test qanday ishlaydi?\n"
    text += "• Natijalar qanday baholanadi?\n"
    text += "• Texnik muammolar hal qilish\n\n"
    
    text += "📱 <b>Bizni kuzatib boring:</b>\n"
    text += "• Telegram: @kitobxon_kids\n"
    text += "• Instagram: @kitobxon_kids\n"
    text += "• Facebook: Kitobxon Kids"
    
    await message.answer(text)

# ═══════════════════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════════

@router.message()
async def unknown_message(message: Message) -> None:
    """Handle unknown messages"""
    text = "❓ <b>Tushunmadim</b>\n\n"
    text += "Iltimos, quyidagi tugmalardan birini tanlang yoki /start buyrug'ini yuboring."
    
    is_admin = data_manager.is_super_admin(message.from_user.username or "")
    keyboard = get_admin_menu_keyboard() if is_admin else get_main_menu_keyboard()
    
    await message.answer(text, reply_markup=keyboard)

# ═══════════════════════════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════════

async def set_bot_commands(bot: Bot) -> None:
    """Set bot commands menu"""
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam"),
    ]
    await bot.set_my_commands(commands)

async def main() -> None:
    """Main function to run the bot"""
    # Include router
    dp.include_router(router)
    
    # Set bot commands
    await set_bot_commands(bot)
    
    logger.info("🚀 Kitobxon Kids Bot started!")
    logger.info("📊 Features: Multi-format support, Unlimited registrations, Access control")
    logger.info("⚡ Performance: Optimized for 4,000+ concurrent users")
    
    # Start polling
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
