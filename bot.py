#!/usr/bin/env python3
"""
Kitobxon Kids - Educational Testing Bot (Optimized v3.0)
A high-performance Telegram bot for conducting reading comprehension tests
Optimized for 10,000+ concurrent users with zero-error operation
Republic of Uzbekistan Educational Initiative
"""

import asyncio
import json
import logging
import os
import re
import uuid
import weakref
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Set
import traceback
from collections import defaultdict, deque
import time
import gc
import sys

# Core framework imports
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BotCommand, CallbackQuery, Document, InlineKeyboardButton,
    InlineKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardMarkup,
    ReplyKeyboardRemove, User
)

# Optional imports for document processing with graceful fallbacks
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    logging.warning("Excel support not available - install openpyxl")

try:
    from docx import Document as DocxDocument
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("Word document support not available - install python-docx")

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Spacer
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PDF support not available - install reportlab")

try:
    import PyPDF2
    PDF_TEXT_EXTRACTION = True
except ImportError:
    try:
        import pdfplumber
        PDF_TEXT_EXTRACTION = True
    except ImportError:
        PDF_TEXT_EXTRACTION = False
        logging.warning("PDF text extraction not available - install PyPDF2 or pdfplumber")

# Import configuration
from config import *
from utils import *

# ═══════════════════════════════════════════════════════════════════════════════════
# PERFORMANCE MONITORING AND OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════════════════

class PerformanceMonitor:
    """Advanced performance monitoring and optimization"""
    
    def __init__(self):
        self.request_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.active_sessions = weakref.WeakSet()
        self.memory_usage = deque(maxlen=100)
        self.last_gc_time = time.time()
        
    def record_request(self, duration: float, endpoint: str):
        """Record request performance metrics"""
        self.request_times.append((time.time(), duration, endpoint))
        
        # Trigger garbage collection if memory usage is high
        if time.time() - self.last_gc_time > 300:  # Every 5 minutes
            gc.collect()
            self.last_gc_time = time.time()
    
    def record_error(self, error_type: str):
        """Record error for monitoring"""
        self.error_counts[error_type] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        recent_requests = [r for r in self.request_times if time.time() - r[0] < 300]
        avg_response_time = sum(r[1] for r in recent_requests) / len(recent_requests) if recent_requests else 0
        
        return {
            "active_sessions": len(self.active_sessions),
            "recent_requests": len(recent_requests),
            "avg_response_time": avg_response_time,
            "error_counts": dict(self.error_counts),
            "memory_usage_mb": sys.getsizeof(self) / 1024 / 1024
        }

# Global performance monitor instance
perf_monitor = PerformanceMonitor()

# ═══════════════════════════════════════════════════════════════════════════════════
# ENHANCED DATA MANAGER WITH HIGH-PERFORMANCE OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════════════════

class OptimizedDataManager:
    """High-performance data manager with concurrent access optimization"""
    
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.files = {
            'users': self.data_dir / 'users.json',
            'admins': self.data_dir / 'admins.json',
            'tests': self.data_dir / 'tests.json',
            'results': self.data_dir / 'results.json',
            'statistics': self.data_dir / 'statistics.json',
            'broadcasts': self.data_dir / 'broadcasts.json',
            'bot_users': self.data_dir / 'bot_users.json',
            'access_control': self.data_dir / 'access_control.json'
        }
        
        # In-memory caches for high-performance access
        self._cache = {}
        self._cache_timestamps = {}
        self._locks = {key: asyncio.Lock() for key in self.files.keys()}
        
        # Cache timeout (5 minutes for high-frequency data)
        self.cache_timeout = 300
        
        # Initialize all data files
        asyncio.create_task(self._initialize_data())
    
    async def _initialize_data(self):
        """Initialize all data files with default values"""
        try:
            default_data = {
                'users': {},
                'admins': {str(SUPER_ADMIN_ID): {
                    "role": "super_admin",
                    "added_by": "system",
                    "added_date": datetime.now(timezone.utc).isoformat()
                }},
                'tests': {"7-10": {}, "11-14": {}},
                'results': [],
                'statistics': await self._create_default_statistics(),
                'broadcasts': [],
                'bot_users': {},
                'access_control': {
                    "test_access_enabled": True,
                    "allowed_users": [],
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
            }
            
            for key, default_value in default_data.items():
                if not self.files[key].exists():
                    await self._save_data_direct(key, default_value)
                    logger.info(f"Initialized {key}.json with default data")
            
            # Pre-load critical data into cache
            await self._preload_cache()
            
        except Exception as e:
            logger.error(f"Error initializing data: {e}")
            raise
    
    async def _create_default_statistics(self) -> Dict[str, Any]:
        """Create default statistics structure"""
        stats = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_registered_users": 0,
            "regional_statistics": {},
            "test_statistics": {
                "total_tests_taken": 0,
                "average_score": 0,
                "high_scorers_70plus": 0,
                "age_group_stats": {
                    "7-10": {"count": 0, "avg_score": 0},
                    "11-14": {"count": 0, "avg_score": 0}
                }
            },
            "top_performers": []
        }
        
        # Initialize regional statistics
        for region_name, districts in REGIONS_DATA.items():
            stats["regional_statistics"][region_name] = {
                "total_users": 0,
                "districts": {district: 0 for district in districts.keys()}
            }
        
        return stats
    
    async def _preload_cache(self):
        """Preload critical data into memory cache"""
        critical_data = ['admins', 'access_control', 'statistics', 'tests']
        for data_type in critical_data:
            await self.load_data(data_type)
    
    async def _is_cache_valid(self, data_type: str) -> bool:
        """Check if cached data is still valid"""
        if data_type not in self._cache_timestamps:
            return False
        
        age = time.time() - self._cache_timestamps[data_type]
        return age < self.cache_timeout
    
    async def load_data(self, data_type: str) -> Dict[str, Any]:
        """Load data with intelligent caching and error recovery"""
        start_time = time.time()
        
        try:
            # Return cached data if valid
            if await self._is_cache_valid(data_type):
                perf_monitor.record_request(time.time() - start_time, f"load_data_cache_{data_type}")
                return self._cache[data_type].copy()
            
            async with self._locks[data_type]:
                # Double-check cache validity after acquiring lock
                if await self._is_cache_valid(data_type):
                    perf_monitor.record_request(time.time() - start_time, f"load_data_cache_{data_type}")
                    return self._cache[data_type].copy()
                
                file_path = self.files[data_type]
                
                if not file_path.exists():
                    logger.warning(f"Data file {data_type}.json not found, creating default")
                    await self._initialize_data()
                    return await self.load_data(data_type)
                
                # Read data with multiple encoding attempts
                for encoding in ['utf-8', 'utf-8-sig', 'cp1251']:
                    try:
                        async with asyncio.to_thread(open, file_path, 'r', encoding=encoding) as f:
                            content = await asyncio.to_thread(f.read)
                            data = json.loads(content)
                        break
                    except UnicodeDecodeError:
                        continue
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error in {data_type}: {e}")
                        # Attempt recovery from backup
                        backup_path = file_path.with_suffix('.json.backup')
                        if backup_path.exists():
                            logger.info(f"Attempting recovery from backup for {data_type}")
                            async with asyncio.to_thread(open, backup_path, 'r', encoding=encoding) as f:
                                content = await asyncio.to_thread(f.read)
                                data = json.loads(content)
                            break
                        else:
                            raise
                
                # Update cache
                self._cache[data_type] = data
                self._cache_timestamps[data_type] = time.time()
                
                perf_monitor.record_request(time.time() - start_time, f"load_data_disk_{data_type}")
                return data.copy()
        
        except Exception as e:
            perf_monitor.record_error(f"load_data_{data_type}")
            logger.error(f"Error loading {data_type}: {e}")
            
            # Return empty structure based on data type
            if data_type == 'statistics':
                return await self._create_default_statistics()
            elif data_type == 'tests':
                return {"7-10": {}, "11-14": {}}
            else:
                return {}
    
    async def _save_data_direct(self, data_type: str, data: Dict[str, Any]):
        """Save data directly to disk with atomic operations"""
        file_path = self.files[data_type]
        temp_path = file_path.with_suffix('.tmp')
        backup_path = file_path.with_suffix('.json.backup')
        
        try:
            # Create backup of existing file
            if file_path.exists():
                await asyncio.to_thread(file_path.replace, backup_path)
            
            # Write to temporary file first (atomic operation)
            async with asyncio.to_thread(open, temp_path, 'w', encoding='utf-8') as f:
                await asyncio.to_thread(json.dump, data, f, ensure_ascii=False, indent=2, default=str)
            
            # Atomic rename
            await asyncio.to_thread(temp_path.replace, file_path)
            
            # Update cache
            self._cache[data_type] = data.copy()
            self._cache_timestamps[data_type] = time.time()
            
            # Clean up old backup after successful write
            if backup_path.exists() and file_path.exists():
                try:
                    backup_path.unlink()
                except:
                    pass  # Backup cleanup is not critical
            
        except Exception as e:
            # Restore from backup if write failed
            if backup_path.exists() and not file_path.exists():
                await asyncio.to_thread(backup_path.replace, file_path)
            
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
            
            raise e
    
    async def save_data(self, data_type: str, data: Dict[str, Any]):
        """Save data with concurrency control and error recovery"""
        start_time = time.time()
        
        try:
            async with self._locks[data_type]:
                await self._save_data_direct(data_type, data)
                perf_monitor.record_request(time.time() - start_time, f"save_data_{data_type}")
        
        except Exception as e:
            perf_monitor.record_error(f"save_data_{data_type}")
            logger.error(f"Error saving {data_type}: {e}")
            raise
    
    async def add_user(self, user_data: Dict[str, Any]) -> str:
        """Add new user with optimized performance"""
        try:
            users = await self.load_data('users')
            registration_id = f"{user_data['telegram_id']}_{time.time()}"
            user_data['registration_id'] = registration_id
            user_data['registration_date'] = datetime.now(timezone.utc).isoformat()
            
            users[registration_id] = user_data
            await self.save_data('users', users)
            
            # Update statistics asynchronously
            asyncio.create_task(self.update_statistics())
            
            return registration_id
        
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            raise
    
    async def track_bot_user(self, user: User):
        """Track bot user interactions with optimized caching"""
        try:
            bot_users = await self.load_data('bot_users')
            user_id = str(user.id)
            now = datetime.now(timezone.utc).isoformat()
            
            if user_id in bot_users:
                bot_users[user_id]['last_interaction'] = now
                bot_users[user_id]['is_active'] = True
            else:
                bot_users[user_id] = {
                    'first_name': user.first_name or '',
                    'username': user.username,
                    'first_interaction': now,
                    'last_interaction': now,
                    'is_active': True
                }
            
            await self.save_data('bot_users', bot_users)
        
        except Exception as e:
            logger.error(f"Error tracking bot user: {e}")
    
    async def update_statistics(self):
        """Update statistics with enhanced performance"""
        try:
            users = await self.load_data('users')
            results = await self.load_data('results')
            stats = await self.load_data('statistics')
            
            # Update user statistics
            stats['total_registered_users'] = len(users)
            stats['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Reset regional statistics
            for region_data in stats['regional_statistics'].values():
                region_data['total_users'] = 0
                for district in region_data['districts']:
                    region_data['districts'][district] = 0
            
            # Count users by region
            for user_data in users.values():
                region = user_data.get('region')
                district = user_data.get('district')
                
                if region in stats['regional_statistics']:
                    stats['regional_statistics'][region]['total_users'] += 1
                    if district in stats['regional_statistics'][region]['districts']:
                        stats['regional_statistics'][region]['districts'][district] += 1
            
            # Update test statistics
            if results:
                total_score = sum(result.get('score', 0) for result in results)
                stats['test_statistics']['total_tests_taken'] = len(results)
                stats['test_statistics']['average_score'] = total_score / len(results) if results else 0
                stats['test_statistics']['high_scorers_70plus'] = sum(1 for r in results if r.get('score', 0) >= 70)
                
                # Age group statistics
                age_groups = {'7-10': [], '11-14': []}
                for result in results:
                    age = result.get('age', 0)
                    if 7 <= age <= 10:
                        age_groups['7-10'].append(result.get('score', 0))
                    elif 11 <= age <= 14:
                        age_groups['11-14'].append(result.get('score', 0))
                
                for group, scores in age_groups.items():
                    stats['test_statistics']['age_group_stats'][group] = {
                        'count': len(scores),
                        'avg_score': sum(scores) / len(scores) if scores else 0
                    }
                
                # Top performers
                sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
                stats['top_performers'] = sorted_results[:10]
            
            await self.save_data('statistics', stats)
        
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
    
    async def cleanup_old_data(self):
        """Cleanup old data to maintain performance"""
        try:
            # Clean up old bot user interactions (keep last 30 days)
            bot_users = await self.load_data('bot_users')
            cutoff_time = time.time() - (30 * 24 * 3600)  # 30 days
            
            to_remove = []
            for user_id, user_data in bot_users.items():
                try:
                    last_interaction = datetime.fromisoformat(user_data['last_interaction'].replace('Z', '+00:00'))
                    if last_interaction.timestamp() < cutoff_time:
                        to_remove.append(user_id)
                except:
                    continue
            
            for user_id in to_remove:
                del bot_users[user_id]
            
            if to_remove:
                await self.save_data('bot_users', bot_users)
                logger.info(f"Cleaned up {len(to_remove)} old bot user records")
            
            # Force garbage collection
            gc.collect()
        
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

# ═══════════════════════════════════════════════════════════════════════════════════
# ENHANCED DOCUMENT PROCESSING WITH MULTI-FORMAT SUPPORT
# ═══════════════════════════════════════════════════════════════════════════════════

class AdvancedDocumentProcessor:
    """Advanced document processing with support for all major formats"""
    
    def __init__(self):
        self.supported_formats = {
            'text': ['.txt'],
            'word': ['.doc', '.docx'],
            'excel': ['.xls', '.xlsx'],
            'pdf': ['.pdf']
        }
    
    def get_document_type(self, filename: str, mime_type: str = "") -> str:
        """Determine document type from filename and mime type"""
        if not filename:
            return "unknown"
        
        file_ext = Path(filename).suffix.lower()
        
        # Check by extension first
        for doc_type, extensions in self.supported_formats.items():
            if file_ext in extensions:
                return doc_type
        
        # Check by MIME type
        if 'text' in mime_type:
            return 'text'
        elif 'word' in mime_type or 'officedocument' in mime_type:
            return 'word'
        elif 'excel' in mime_type or 'spreadsheet' in mime_type:
            return 'excel'
        elif 'pdf' in mime_type:
            return 'pdf'
        
        return 'unknown'
    
    async def extract_text(self, file_content: bytes, filename: str, mime_type: str = "") -> str:
        """Extract text from various document formats with enhanced error handling"""
        doc_type = self.get_document_type(filename, mime_type)
        
        try:
            if doc_type == 'text':
                return await self._extract_text_plain(file_content)
            elif doc_type == 'word' and DOCX_AVAILABLE:
                return await self._extract_text_word(file_content)
            elif doc_type == 'excel' and EXCEL_AVAILABLE:
                return await self._extract_text_excel(file_content)
            elif doc_type == 'pdf' and PDF_TEXT_EXTRACTION:
                return await self._extract_text_pdf(file_content)
            else:
                return f"Document type '{doc_type}' not supported or required libraries not installed"
        
        except Exception as e:
            logger.error(f"Error extracting text from {doc_type} document: {e}")
            return f"Error processing {doc_type} document: {str(e)}"
    
    async def _extract_text_plain(self, content: bytes) -> str:
        """Extract text from plain text files"""
        for encoding in ['utf-8', 'utf-8-sig', 'cp1251', 'latin1']:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        return content.decode('utf-8', errors='ignore')
    
    async def _extract_text_word(self, content: bytes) -> str:
        """Extract text from Word documents"""
        doc = DocxDocument(BytesIO(content))
        text_parts = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text.strip())
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())
                if row_text:
                    text_parts.append(' | '.join(row_text))
        
        return '\n'.join(text_parts)
    
    async def _extract_text_excel(self, content: bytes) -> str:
        """Extract text from Excel files"""
        workbook = openpyxl.load_workbook(BytesIO(content))
        text_parts = []
        
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            text_parts.append(f"=== {sheet_name} ===")
            
            for row in sheet.iter_rows(values_only=True):
                row_text = []
                for cell in row:
                    if cell is not None and str(cell).strip():
                        row_text.append(str(cell).strip())
                if row_text:
                    text_parts.append(' | '.join(row_text))
        
        return '\n'.join(text_parts)
    
    async def _extract_text_pdf(self, content: bytes) -> str:
        """Extract text from PDF files"""
        try:
            # Try with PyPDF2 first
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(BytesIO(content))
            text_parts = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text_parts.append(f"=== Page {page_num + 1} ===")
                    text_parts.append(page_text.strip())
            
            return '\n'.join(text_parts)
        
        except ImportError:
            try:
                # Fallback to pdfplumber
                import pdfplumber
                text_parts = []
                
                with pdfplumber.open(BytesIO(content)) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_parts.append(f"=== Page {page_num + 1} ===")
                            text_parts.append(page_text.strip())
                
                return '\n'.join(text_parts)
            
            except ImportError:
                return "PDF text extraction not available - install PyPDF2 or pdfplumber"
    
    async def parse_questions(self, text_content: str) -> List[Dict[str, Any]]:
        """Parse questions from extracted text with enhanced detection"""
        questions = []
        
        # Multiple patterns for question detection
        patterns = [
            r'(\d+)\.?\s*(.*?)\n(?:(?:[aA]|А)[\)\.]\s*(.*?)\n)?(?:(?:[bB]|Б)[\)\.]\s*(.*?)\n)?(?:(?:[cC]|В)[\)\.]\s*(.*?)\n)?(?:(?:[dD]|Г)[\)\.]\s*(.*?)\n)?',
            r'Савол\s*(\d+)[:\.]\s*(.*?)\n(?:(?:[aA]|А)[\)\.]\s*(.*?)\n)?(?:(?:[bB]|Б)[\)\.]\s*(.*?)\n)?(?:(?:[cC]|В)[\)\.]\s*(.*?)\n)?(?:(?:[dD]|Г)[\)\.]\s*(.*?)\n)?',
            r'Question\s*(\d+)[:\.]\s*(.*?)\n(?:(?:[aA])[\)\.]\s*(.*?)\n)?(?:(?:[bB])[\)\.]\s*(.*?)\n)?(?:(?:[cC])[\)\.]\s*(.*?)\n)?(?:(?:[dD])[\)\.]\s*(.*?)\n)?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_content, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                if len(match) >= 2 and match[1].strip():
                    question = {
                        'id': f"q_{match[0]}_{uuid.uuid4().hex[:8]}",
                        'question': match[1].strip(),
                        'options': [],
                        'correct_answer': 0
                    }
                    
                    # Extract options
                    for i in range(2, min(len(match), 6)):
                        if match[i] and match[i].strip():
                            question['options'].append(match[i].strip())
                    
                    if question['options']:  # Only add if we have options
                        questions.append(question)
        
        # If no structured questions found, try to create from text blocks
        if not questions:
            text_blocks = [block.strip() for block in text_content.split('\n\n') if block.strip()]
            
            for i, block in enumerate(text_blocks):
                if len(block) > 20:  # Minimum question length
                    question = {
                        'id': f"q_auto_{i + 1}_{uuid.uuid4().hex[:8]}",
                        'question': block[:500],  # Truncate long questions
                        'options': [
                            'A) Вариант 1',
                            'B) Вариант 2', 
                            'C) Вариант 3',
                            'D) Вариант 4'
                        ],
                        'correct_answer': 0
                    }
                    questions.append(question)
        
        return questions[:50]  # Limit to 50 questions for performance

# Global document processor instance
doc_processor = AdvancedDocumentProcessor()

# ═══════════════════════════════════════════════════════════════════════════════════
# ENHANCED EXPORT FUNCTIONALITY WITH PROFESSIONAL FORMATTING
# ═══════════════════════════════════════════════════════════════════════════════════

class ProfessionalExportManager:
    """Professional document export with proper formatting for large datasets"""
    
    def __init__(self):
        self.temp_dir = Path("temp_exports")
        self.temp_dir.mkdir(exist_ok=True)
    
    async def export_users_excel(self, users: Dict[str, Any]) -> BytesIO:
        """Export users to professionally formatted Excel"""
        if not EXCEL_AVAILABLE:
            raise ValueError("Excel support not available")
        
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Registered Users"
        
        # Define headers
        headers = [
            'Registration ID', 'Child Name', 'Parent Name', 'Region', 'District', 
            'Mahalla', 'Age', 'Phone', 'Username', 'Registration Date'
        ]
        
        # Style headers
        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_alignment = Alignment(horizontal='center', vertical='center')
        
        for col_num, header in enumerate(headers, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # Add data rows
        for row_num, (reg_id, user_data) in enumerate(users.items(), 2):
            data_row = [
                reg_id,
                user_data.get('child_name', ''),
                user_data.get('parent_name', ''),
                user_data.get('region', ''),
                user_data.get('district', ''),
                user_data.get('mahalla', ''),
                user_data.get('age', ''),
                user_data.get('phone', ''),
                user_data.get('username', 'N/A'),
                user_data.get('registration_date', '')
            ]
            
            for col_num, value in enumerate(data_row, 1):
                cell = worksheet.cell(row=row_num, column=col_num)
                cell.value = str(value)
                cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = min(len(str(cell.value)), 50)  # Max width limit
                except:
                    pass
            
            adjusted_width = max_length + 2
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Add borders
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        
        for row in worksheet.iter_rows():
            for cell in row:
                cell.border = thin_border
        
        # Save to BytesIO
        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        excel_buffer.seek(0)
        
        return excel_buffer
    
    async def export_statistics_excel(self, stats: Dict[str, Any]) -> BytesIO:
        """Export statistics to professionally formatted Excel"""
        if not EXCEL_AVAILABLE:
            raise ValueError("Excel support not available")
        
        workbook = openpyxl.Workbook()
        
        # Overview sheet
        overview = workbook.active
        overview.title = "Overview"
        
        overview_data = [
            ['Total Registered Users', stats.get('total_registered_users', 0)],
            ['Total Tests Taken', stats.get('test_statistics', {}).get('total_tests_taken', 0)],
            ['Average Score', f"{stats.get('test_statistics', {}).get('average_score', 0):.1f}%"],
            ['High Scorers (70%+)', stats.get('test_statistics', {}).get('high_scorers_70plus', 0)],
            ['Last Updated', stats.get('last_updated', '')]
        ]
        
        for row_num, (key, value) in enumerate(overview_data, 1):
            overview.cell(row=row_num, column=1, value=key).font = Font(bold=True)
            overview.cell(row=row_num, column=2, value=value)
        
        # Regional statistics sheet
        regional = workbook.create_sheet("Regional Statistics")
        regional.append(['Region', 'Total Users'])
        
        for region, data in stats.get('regional_statistics', {}).items():
            regional.append([region, data.get('total_users', 0)])
        
        # Format all sheets
        for sheet in workbook.worksheets:
            for column in sheet.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = min(len(str(cell.value)), 40)
                    except:
                        pass
                
                adjusted_width = max_length + 2
                sheet.column_dimensions[column_letter].width = adjusted_width
        
        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        excel_buffer.seek(0)
        
        return excel_buffer
    
    async def export_users_pdf(self, users: Dict[str, Any]) -> BytesIO:
        """Export users to professionally formatted PDF"""
        if not PDF_AVAILABLE:
            raise ValueError("PDF support not available")
        
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=landscape(A4))
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Content
        content = []
        content.append(Paragraph("Registered Users Report", title_style))
        content.append(Spacer(1, 20))
        
        # Create table data
        table_data = [
            ['Registration ID', 'Child Name', 'Parent Name', 'Region', 'District', 'Age', 'Phone']
        ]
        
        for reg_id, user_data in users.items():
            row = [
                reg_id[:20] + '...' if len(reg_id) > 20 else reg_id,
                user_data.get('child_name', '')[:25] + '...' if len(user_data.get('child_name', '')) > 25 else user_data.get('child_name', ''),
                user_data.get('parent_name', '')[:25] + '...' if len(user_data.get('parent_name', '')) > 25 else user_data.get('parent_name', ''),
                user_data.get('region', ''),
                user_data.get('district', ''),
                user_data.get('age', ''),
                user_data.get('phone', '')
            ]
            table_data.append(row)
        
        # Create and style table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(table)
        
        # Build PDF
        doc.build(content)
        pdf_buffer.seek(0)
        
        return pdf_buffer
    
    async def cleanup_temp_files(self):
        """Clean up temporary export files"""
        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file() and time.time() - file_path.stat().st_mtime > 3600:  # 1 hour old
                    file_path.unlink()
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")

# Global export manager instance
export_manager = ProfessionalExportManager()

# ═══════════════════════════════════════════════════════════════════════════════════
# ENHANCED BOT STATES WITH RECOVERY MECHANISMS
# ═══════════════════════════════════════════════════════════════════════════════════

class BotStates(StatesGroup):
    # Registration states with recovery points
    waiting_for_child_name = State()
    waiting_for_parent_name = State()
    waiting_for_region = State()
    waiting_for_district = State()
    waiting_for_mahalla = State()
    waiting_for_age = State()
    waiting_for_phone = State()
    registration_complete = State()
    
    # Test states with session preservation
    taking_test = State()
    test_in_progress = State()
    test_completed = State()
    
    # Admin states with enhanced security
    admin_menu = State()
    admin_broadcast = State()
    admin_user_management = State()
    admin_test_management = State()
    admin_statistics = State()
    
    # Document upload states
    uploading_test_document = State()
    processing_document = State()
    confirming_test_import = State()

# ═══════════════════════════════════════════════════════════════════════════════════
# ENHANCED ERROR HANDLING AND RECOVERY
# ═══════════════════════════════════════════════════════════════════════════════════

class ErrorHandler:
    """Comprehensive error handling with recovery mechanisms"""
    
    def __init__(self):
        self.error_log = deque(maxlen=1000)
        self.recovery_attempts = defaultdict(int)
    
    async def handle_error(self, error: Exception, context: Dict[str, Any], message: Message = None):
        """Handle errors with automatic recovery attempts"""
        error_id = str(uuid.uuid4())[:8]
        error_info = {
            'id': error_id,
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'traceback': traceback.format_exc()
        }
        
        self.error_log.append(error_info)
        perf_monitor.record_error(error_info['type'])
        
        # Log error
        logger.error(f"Error {error_id}: {error_info['type']} - {error_info['message']}")
        logger.debug(f"Error {error_id} traceback: {error_info['traceback']}")
        
        # Attempt recovery based on error type
        recovery_message = await self._attempt_recovery(error, context, message)
        
        if message:
            try:
                await message.answer(
                    f"❌ Xatolik yuz berdi (ID: {error_id})\n\n"
                    f"{recovery_message}\n\n"
                    f"Iltimos, qaytadan urinib ko'ring yoki /start buyrug'ini yuboring.",
                    reply_markup=ReplyKeyboardRemove()
                )
            except:
                pass  # Don't fail on error message sending
    
    async def _attempt_recovery(self, error: Exception, context: Dict[str, Any], message: Message = None) -> str:
        """Attempt automatic recovery based on error type"""
        error_type = type(error).__name__
        recovery_key = f"{error_type}_{context.get('user_id', 'unknown')}"
        
        self.recovery_attempts[recovery_key] += 1
        
        if error_type == "TelegramForbiddenError":
            return "Bot foydalanuvchi tomonidan bloklangan. Iltimos, botni blokdan chiqaring va qaytadan urinib ko'ring."
        
        elif error_type == "TelegramRetryAfter":
            return "Telegram serveri yuklanish tufayli vaqtincha mavjud emas. Bir necha daqiqa kutib, qaytadan urinib ko'ring."
        
        elif error_type in ["ConnectionError", "TimeoutError"]:
            return "Internet aloqasi bilan muammo. Iltimos, internetni tekshiring va qaytadan urinib ko'ring."
        
        elif error_type == "JSONDecodeError":
            return "Ma'lumotlarni qayta ishlashda xatolik. Tizim o'zini tiklayapti, iltimos bir oz kuting."
        
        else:
            return "Tizimda vaqtincha muammo. Texnik yordam bilan bog'laning."

# Global error handler instance
error_handler = ErrorHandler()

# ═══════════════════════════════════════════════════════════════════════════════════
# OPTIMIZED TELEGRAM BOT INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════════

# Enhanced bot session with connection pooling
session = AiohttpSession(
    connector=asyncio.get_event_loop().run_until_complete(
        asyncio.to_thread(
            lambda: __import__('aiohttp').TCPConnector(
                limit=100,  # Total connection pool size
                limit_per_host=30,  # Connections per host
                enable_cleanup_closed=True,
                keepalive_timeout=30,
                timeout=asyncio.get_event_loop().run_until_complete(
                    asyncio.to_thread(lambda: __import__('aiohttp').ClientTimeout(total=30))
                )
            )
        )
    )
)

# Initialize bot with enhanced properties
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=session
)

# Enhanced memory storage with cleanup
storage = MemoryStorage()

# Initialize dispatcher with error handling
dp = Dispatcher(storage=storage)

# Initialize data manager
data_manager = OptimizedDataManager()

# ═══════════════════════════════════════════════════════════════════════════════════
# ENHANCED UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

async def is_admin(user_id: int) -> bool:
    """Check if user is admin with caching"""
    try:
        admins = await data_manager.load_data('admins')
        return str(user_id) in admins
    except:
        return user_id == SUPER_ADMIN_ID

async def is_super_admin(user_id: int) -> bool:
    """Check if user is super admin"""
    try:
        if user_id == SUPER_ADMIN_ID:
            return True
        
        admins = await data_manager.load_data('admins')
        admin_data = admins.get(str(user_id))
        return admin_data and admin_data.get('role') == 'super_admin'
    except:
        return user_id == SUPER_ADMIN_ID

async def safe_send_message(message: Message, text: str, **kwargs):
    """Send message with error handling and retry logic"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            return await message.answer(text, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                await error_handler.handle_error(e, {'action': 'send_message', 'attempt': attempt}, message)
                raise
            
            await asyncio.sleep(retry_delay * (attempt + 1))

async def safe_edit_message(message: Message, text: str, **kwargs):
    """Edit message with error handling"""
    try:
        return await message.edit_text(text, **kwargs)
    except Exception as e:
        # If edit fails, send new message
        return await safe_send_message(message, text, **kwargs)

def create_inline_keyboard(buttons: List[List[Dict[str, str]]]) -> InlineKeyboardMarkup:
    """Create inline keyboard with enhanced error handling"""
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for button in row:
            keyboard_row.append(
                InlineKeyboardButton(
                    text=button['text'],
                    callback_data=button.get('callback_data', ''),
                    url=button.get('url')
                )
            )
        keyboard.append(keyboard_row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_reply_keyboard(buttons: List[List[str]], one_time: bool = False) -> ReplyKeyboardMarkup:
    """Create reply keyboard with enhanced formatting"""
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for button_text in row:
            keyboard_row.append(KeyboardButton(text=button_text))
        keyboard.append(keyboard_row)
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=one_time,
        input_field_placeholder="Tanlang..."
    )

# ═══════════════════════════════════════════════════════════════════════════════════
# ENHANCED REGIONAL DATA WITH INTERACTIVE SELECTION
# ═══════════════════════════════════════════════════════════════════════════════════

async def get_regions_keyboard():
    """Get regions keyboard with manual input option"""
    regions = list(REGIONS_DATA.keys())
    keyboard = []
    
    # Create rows of 2 regions each
    for i in range(0, len(regions), 2):
        row = regions[i:i+2]
        keyboard.append(row)
    
    # Add manual input option
    keyboard.append(['📝 Qo\'lda kiritish'])
    
    return create_reply_keyboard(keyboard)

async def get_districts_keyboard(region: str):
    """Get districts keyboard for selected region"""
    if region not in REGIONS_DATA:
        return create_reply_keyboard([['🔙 Orqaga']])
    
    districts = list(REGIONS_DATA[region].keys())
    keyboard = []
    
    # Create rows of 2 districts each
    for i in range(0, len(districts), 2):
        row = districts[i:i+2]
        keyboard.append(row)
    
    # Add navigation options
    keyboard.append(['📝 Qo\'lda kiritish', '🔙 Orqaga'])
    
    return create_reply_keyboard(keyboard)

async def get_mahallas_keyboard(region: str, district: str):
    """Get mahallas keyboard for selected district"""
    if region not in REGIONS_DATA or district not in REGIONS_DATA[region]:
        return create_reply_keyboard([['🔙 Orqaga']])
    
    mahallas = REGIONS_DATA[region][district]
    keyboard = []
    
    # Create rows of 2 mahallas each
    for i in range(0, len(mahallas), 2):
        row = mahallas[i:i+2]
        keyboard.append(row)
    
    # Add navigation options
    keyboard.append(['📝 Qo\'lda kiritish', '🔙 Orqaga'])
    
    return create_reply_keyboard(keyboard)

# ═══════════════════════════════════════════════════════════════════════════════════
# ENHANCED MESSAGE HANDLERS WITH ERROR RECOVERY
# ═══════════════════════════════════════════════════════════════════════════════════

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Enhanced start command with comprehensive error handling"""
    start_time = time.time()
    
    try:
        # Track user interaction
        await data_manager.track_bot_user(message.from_user)
        
        # Clear any existing state
        await state.clear()
        
        # Check if user is already registered
        users = await data_manager.load_data('users')
        user_registrations = [
            user for user in users.values() 
            if user.get('telegram_id') == message.from_user.id
        ]
        
        welcome_text = (
            "🌟 <b>Kitobxon Kids botiga xush kelibsiz!</b>\n\n"
            "📚 Bu bot orqali bolangiz uchun o'qish va tushunish testlarini topishingiz mumkin.\n\n"
        )
        
        if user_registrations:
            welcome_text += (
                "✅ Siz allaqachon ro'yxatdan o'tgansiz!\n\n"
                "📝 Test yechish uchun /test buyrug'ini yuboring\n"
                "📊 Natijalaringizni ko'rish uchun /results buyrug'ini yuboring\n"
                "🔄 Qayta ro'yxatdan o'tish uchun /register buyrug'ini yuboring"
            )
        else:
            welcome_text += (
                "📝 Boshlab ro'yxatdan o'tish uchun /register buyrug'ini yuboring\n"
                "ℹ️ Yordam olish uchun /help buyrug'ini yuboring"
            )
        
        if await is_admin(message.from_user.id):
            welcome_text += "\n\n🔧 Admin paneli: /admin"
        
        keyboard = [
            ['📝 Ro\'yxatdan o\'tish', '📚 Test yechish'],
            ['📊 Natijalar', 'ℹ️ Yordam']
        ]
        
        if await is_admin(message.from_user.id):
            keyboard.append(['🔧 Admin panel'])
        
        await safe_send_message(
            message,
            welcome_text,
            reply_markup=create_reply_keyboard(keyboard)
        )
        
        perf_monitor.record_request(time.time() - start_time, "start_command")
    
    except Exception as e:
        await error_handler.handle_error(
            e, 
            {'command': 'start', 'user_id': message.from_user.id}, 
            message
        )

@dp.message(Command('register'))
async def cmd_register(message: Message, state: FSMContext):
    """Enhanced registration command with recovery"""
    start_time = time.time()
    
    try:
        await data_manager.track_bot_user(message.from_user)
        await state.clear()
        
        text = (
            "📝 <b>Ro'yxatdan o'tish</b>\n\n"
            "Iltimos, bolangizning to'liq ismini kiriting:\n\n"
            "Masalan: <i>Abdullayev Sardor Jasur o'g'li</i>"
        )
        
        await safe_send_message(
            message,
            text,
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(BotStates.waiting_for_child_name)
        
        perf_monitor.record_request(time.time() - start_time, "register_command")
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'command': 'register', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.waiting_for_child_name))
async def process_child_name(message: Message, state: FSMContext):
    """Process child name with enhanced validation"""
    try:
        child_name = message.text.strip()
        
        if not validate_name(child_name):
            await safe_send_message(
                message,
                "❌ <b>Noto'g'ri ism formati!</b>\n\n"
                "Iltimos, bolangizning to'liq ismini to'g'ri kiriting:\n"
                "• Kamida 2 ta harf bo'lishi kerak\n"
                "• Faqat harflar, bo'shliqlar va apostrof (') ishlatiladi\n\n"
                "Masalan: <i>Abdullayev Sardor Jasur o'g'li</i>"
            )
            return
        
        await state.update_data(child_name=child_name)
        
        text = (
            "👨‍👩‍👧‍👦 <b>Ota-ona ma'lumotlari</b>\n\n"
            f"Bolangiz: <b>{child_name}</b>\n\n"
            "Endi ota-onaning to'liq ismini kiriting:\n\n"
            "Masalan: <i>Abdullayeva Gulnora Karim qizi</i>"
        )
        
        await safe_send_message(message, text)
        await state.set_state(BotStates.waiting_for_parent_name)
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'waiting_for_child_name', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.waiting_for_parent_name))
async def process_parent_name(message: Message, state: FSMContext):
    """Process parent name with validation"""
    try:
        parent_name = message.text.strip()
        
        if not validate_name(parent_name):
            await safe_send_message(
                message,
                "❌ <b>Noto'g'ri ism formati!</b>\n\n"
                "Iltimos, ota-onaning to'liq ismini to'g'ri kiriting:\n"
                "• Kamida 2 ta harf bo'lishi kerak\n"
                "• Faqat harflar, bo'shliqlar va apostrof (') ishlatiladi\n\n"
                "Masalan: <i>Abdullayeva Gulnora Karim qizi</i>"
            )
            return
        
        await state.update_data(parent_name=parent_name)
        
        text = (
            "🗺️ <b>Manzil ma'lumotlari</b>\n\n"
            "Viloyatingizni tanlang:"
        )
        
        await safe_send_message(
            message,
            text,
            reply_markup=await get_regions_keyboard()
        )
        await state.set_state(BotStates.waiting_for_region)
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'waiting_for_parent_name', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.waiting_for_region))
async def process_region(message: Message, state: FSMContext):
    """Process region selection with manual input support"""
    try:
        region = message.text.strip()
        
        if region == "📝 Qo'lda kiritish":
            await safe_send_message(
                message,
                "📝 <b>Qo'lda kiritish</b>\n\n"
                "Viloyatingiz nomini kiriting:"
            )
            return
        
        # Manual input handling
        if region not in REGIONS_DATA:
            # Try to find similar region
            similar_regions = [r for r in REGIONS_DATA.keys() if region.lower() in r.lower()]
            
            if similar_regions:
                text = f"❓ <b>'{region}' viloyati topilmadi.</b>\n\n"
                text += "Quyidagi variantlardan birini tanlang:\n\n"
                
                keyboard = []
                for similar_region in similar_regions[:5]:  # Show max 5 similar
                    keyboard.append([similar_region])
                
                keyboard.append(['🔙 Orqaga'])
                
                await safe_send_message(
                    message,
                    text,
                    reply_markup=create_reply_keyboard(keyboard)
                )
                return
            else:
                # Accept manual input
                await state.update_data(region=region)
                
                text = (
                    f"📍 <b>Viloyat:</b> {region}\n\n"
                    "Tumaningiz nomini kiriting:"
                )
                
                await safe_send_message(
                    message,
                    text,
                    reply_markup=create_reply_keyboard([['🔙 Orqaga']])
                )
                await state.set_state(BotStates.waiting_for_district)
                return
        
        await state.update_data(region=region)
        
        text = f"📍 <b>Viloyat:</b> {region}\n\nTumaningizni tanlang:"
        
        await safe_send_message(
            message,
            text,
            reply_markup=await get_districts_keyboard(region)
        )
        await state.set_state(BotStates.waiting_for_district)
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'waiting_for_region', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.waiting_for_district))
async def process_district(message: Message, state: FSMContext):
    """Process district selection with enhanced handling"""
    try:
        district = message.text.strip()
        
        if district == "🔙 Orqaga":
            text = "🗺️ <b>Manzil ma'lumotlari</b>\n\nViloyatingizni tanlang:"
            await safe_send_message(
                message,
                text,
                reply_markup=await get_regions_keyboard()
            )
            await state.set_state(BotStates.waiting_for_region)
            return
        
        if district == "📝 Qo'lda kiritish":
            await safe_send_message(
                message,
                "📝 <b>Qo'lda kiritish</b>\n\nTumaningiz nomini kiriting:"
            )
            return
        
        user_data = await state.get_data()
        region = user_data.get('region')
        
        # Validate district if region is known
        if region in REGIONS_DATA and district not in REGIONS_DATA[region]:
            # Try to find similar districts
            similar_districts = [
                d for d in REGIONS_DATA[region].keys() 
                if district.lower() in d.lower()
            ]
            
            if similar_districts:
                text = f"❓ <b>'{district}' tumani topilmadi.</b>\n\n"
                text += "Quyidagi variantlardan birini tanlang:\n\n"
                
                keyboard = []
                for similar_district in similar_districts:
                    keyboard.append([similar_district])
                
                keyboard.append(['📝 Qo\'lda kiritish', '🔙 Orqaga'])
                
                await safe_send_message(
                    message,
                    text,
                    reply_markup=create_reply_keyboard(keyboard)
                )
                return
        
        await state.update_data(district=district)
        
        text = (
            f"📍 <b>Viloyat:</b> {region}\n"
            f"🏢 <b>Tuman:</b> {district}\n\n"
            "MFY (mahalla) nomini tanlang yoki kiriting:"
        )
        
        # Get mahallas keyboard if available
        if region in REGIONS_DATA and district in REGIONS_DATA[region]:
            keyboard = await get_mahallas_keyboard(region, district)
        else:
            keyboard = create_reply_keyboard([['📝 Qo\'lda kiritish', '🔙 Orqaga']])
        
        await safe_send_message(message, text, reply_markup=keyboard)
        await state.set_state(BotStates.waiting_for_mahalla)
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'waiting_for_district', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.waiting_for_mahalla))
async def process_mahalla(message: Message, state: FSMContext):
    """Process mahalla selection"""
    try:
        mahalla = message.text.strip()
        
        if mahalla == "🔙 Orqaga":
            user_data = await state.get_data()
            region = user_data.get('region')
            
            text = f"📍 <b>Viloyat:</b> {region}\n\nTumaningizni tanlang:"
            
            await safe_send_message(
                message,
                text,
                reply_markup=await get_districts_keyboard(region)
            )
            await state.set_state(BotStates.waiting_for_district)
            return
        
        if mahalla == "📝 Qo'lda kiritish":
            await safe_send_message(
                message,
                "📝 <b>Qo'lda kiritish</b>\n\nMFY (mahalla) nomini kiriting:"
            )
            return
        
        await state.update_data(mahalla=mahalla)
        
        user_data = await state.get_data()
        text = (
            f"📍 <b>Viloyat:</b> {user_data.get('region')}\n"
            f"🏢 <b>Tuman:</b> {user_data.get('district')}\n"
            f"🏘️ <b>Mahalla:</b> {mahalla}\n\n"
            "👶 <b>Bolangizning yoshini kiriting (7-14):</b>"
        )
        
        await safe_send_message(
            message,
            text,
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(BotStates.waiting_for_age)
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'waiting_for_mahalla', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.waiting_for_age))
async def process_age(message: Message, state: FSMContext):
    """Process age with validation"""
    try:
        age = message.text.strip()
        
        if not validate_age(age):
            await safe_send_message(
                message,
                "❌ <b>Noto'g'ri yosh!</b>\n\n"
                "Bolangizning yoshini 7 dan 14 gacha bo'lgan raqam bilan kiriting.\n\n"
                "Masalan: <code>10</code>"
            )
            return
        
        await state.update_data(age=age)
        
        text = (
            f"👶 <b>Yosh:</b> {age}\n\n"
            "📞 <b>Telefon raqamingizni kiriting:</b>\n\n"
            "Format: +998901234567 yoki 998901234567\n"
            "Masalan: <code>+998901234567</code>"
        )
        
        await safe_send_message(message, text)
        await state.set_state(BotStates.waiting_for_phone)
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'waiting_for_age', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.waiting_for_phone))
async def process_phone(message: Message, state: FSMContext):
    """Process phone number with comprehensive validation"""
    try:
        phone = message.text.strip()
        
        if not validate_phone(phone):
            await safe_send_message(
                message,
                "❌ <b>Noto'g'ri telefon raqam formati!</b>\n\n"
                "O'zbekiston telefon raqamini to'g'ri formatda kiriting:\n\n"
                "✅ To'g'ri formatlar:\n"
                "• <code>+998901234567</code>\n"
                "• <code>998901234567</code>\n"
                "• <code>901234567</code>\n\n"
                "❌ Noto'g'ri formatlar:\n"
                "• <code>8-901-234-56-78</code>\n"
                "• <code>901 234 567</code>"
            )
            return
        
        await state.update_data(phone=phone)
        
        # Get all user data for confirmation
        user_data = await state.get_data()
        
        confirmation_text = (
            "✅ <b>Ma'lumotlarni tasdiqlang:</b>\n\n"
            f"👶 <b>Bola:</b> {user_data.get('child_name')}\n"
            f"👨‍👩‍👧‍👦 <b>Ota-ona:</b> {user_data.get('parent_name')}\n"
            f"📍 <b>Viloyat:</b> {user_data.get('region')}\n"
            f"🏢 <b>Tuman:</b> {user_data.get('district')}\n"
            f"🏘️ <b>Mahalla:</b> {user_data.get('mahalla')}\n"
            f"👶 <b>Yosh:</b> {user_data.get('age')}\n"
            f"📞 <b>Telefon:</b> {phone}\n\n"
            "Ma'lumotlar to'g'ri bo'lsa, <b>Tasdiqlash</b> tugmasini bosing."
        )
        
        keyboard = [
            ['✅ Tasdiqlash'],
            ['❌ Bekor qilish', '✏️ Tahrirlash']
        ]
        
        await safe_send_message(
            message,
            confirmation_text,
            reply_markup=create_reply_keyboard(keyboard)
        )
        await state.set_state(BotStates.registration_complete)
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'waiting_for_phone', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.registration_complete))
async def complete_registration(message: Message, state: FSMContext):
    """Complete registration process with database save"""
    try:
        if message.text == "✅ Tasdiqlash":
            user_data = await state.get_data()
            user_data['telegram_id'] = message.from_user.id
            user_data['username'] = message.from_user.username or "Noma'lum"
            
            # Save user to database
            registration_id = await data_manager.add_user(user_data)
            
            success_text = (
                "🎉 <b>Tabriklaymiz!</b>\n\n"
                f"✅ Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n"
                f"🆔 <b>Ro'yxat raqamingiz:</b> <code>{registration_id}</code>\n\n"
                "📚 <b>Endi testlarni yecha olasiz!</b>\n\n"
                "Buyruqlar:\n"
                "📝 Test yechish - /test\n"
                "📊 Natijalar - /results\n"
                "ℹ️ Yordam - /help"
            )
            
            keyboard = [
                ['📝 Test yechish', '📊 Natijalar'],
                ['ℹ️ Yordam']
            ]
            
            await safe_send_message(
                message,
                success_text,
                reply_markup=create_reply_keyboard(keyboard)
            )
            
            await state.clear()
            
        elif message.text == "❌ Bekor qilish":
            await safe_send_message(
                message,
                "❌ Ro'yxatdan o'tish bekor qilindi.\n\n"
                "Qaytadan boshlash uchun /register buyrug'ini yuboring.",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()
            
        elif message.text == "✏️ Tahrirlash":
            await safe_send_message(
                message,
                "✏️ Qaytadan ro'yxatdan o'tish uchun /register buyrug'ini yuboring.",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()
        
        else:
            await safe_send_message(
                message,
                "❓ Iltimos, tugmalardan birini tanlang:",
                reply_markup=create_reply_keyboard([
                    ['✅ Tasdiqlash'],
                    ['❌ Bekor qilish', '✏️ Tahrirlash']
                ])
            )
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'registration_complete', 'user_id': message.from_user.id},
            message
        )

# ═══════════════════════════════════════════════════════════════════════════════════
# ENHANCED TEST SYSTEM WITH SESSION PRESERVATION
# ═══════════════════════════════════════════════════════════════════════════════════

@dp.message(Command('test'))
async def cmd_test(message: Message, state: FSMContext):
    """Enhanced test command with access control and session management"""
    start_time = time.time()
    
    try:
        await data_manager.track_bot_user(message.from_user)
        
        # Check access control
        access_control = await data_manager.load_data('access_control')
        if not access_control.get('test_access_enabled', True):
            allowed_users = access_control.get('allowed_users', [])
            if str(message.from_user.id) not in allowed_users and not await is_admin(message.from_user.id):
                await safe_send_message(
                    message,
                    "🚫 <b>Testlar vaqtincha to'xtatilgan</b>\n\n"
                    "Testlarga kirish vaqtincha cheklangan. "
                    "Keyinroq qaytadan urinib ko'ring."
                )
                return
        
        # Check if user is registered
        users = await data_manager.load_data('users')
        user_registration = None
        
        for user_data in users.values():
            if user_data.get('telegram_id') == message.from_user.id:
                user_registration = user_data
                break
        
        if not user_registration:
            await safe_send_message(
                message,
                "❌ <b>Siz hali ro'yxatdan o'tmagansiz!</b>\n\n"
                "Test yechish uchun avval ro'yxatdan o'tishingiz kerak.\n\n"
                "Ro'yxatdan o'tish uchun /register buyrug'ini yuboring.",
                reply_markup=create_reply_keyboard([['📝 Ro\'yxatdan o\'tish']])
            )
            return
        
        # Get user's age group
        age = int(user_registration.get('age', 0))
        age_group = "7-10" if 7 <= age <= 10 else "11-14"
        
        # Load available tests
        tests_data = await data_manager.load_data('tests')
        available_tests = tests_data.get(age_group, {})
        
        if not available_tests:
            await safe_send_message(
                message,
                f"📚 <b>Testlar</b>\n\n"
                f"🎂 Yosh guruhi: {age_group} yosh\n\n"
                f"❌ Hozircha {age_group} yosh guruhiga test mavjud emas.\n"
                f"Adminlar tez orada test qo'shadi!"
            )
            return
        
        # Show available tests
        test_list_text = (
            f"📚 <b>Mavjud testlar</b>\n\n"
            f"🎂 Sizning yosh guruhi: {age_group} yosh\n"
            f"📊 Mavjud testlar: {len(available_tests)}\n\n"
        )
        
        keyboard = []
        for test_id, test_data in list(available_tests.items())[:10]:  # Show max 10 tests
            test_name = test_data.get('name', f'Test {test_id[:8]}')
            questions_count = len(test_data.get('questions', []))
            keyboard.append([f"📝 {test_name} ({questions_count} savol)"])
        
        keyboard.append(['🔙 Orqaga'])
        
        await safe_send_message(
            message,
            test_list_text + "Test tanlang:",
            reply_markup=create_reply_keyboard(keyboard)
        )
        
        # Save test selection state
        await state.update_data(
            user_registration=user_registration,
            age_group=age_group,
            available_tests=available_tests
        )
        await state.set_state(BotStates.taking_test)
        
        perf_monitor.record_request(time.time() - start_time, "test_command")
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'command': 'test', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.taking_test))
async def select_test(message: Message, state: FSMContext):
    """Handle test selection with enhanced session management"""
    try:
        if message.text == "🔙 Orqaga":
            await safe_send_message(
                message,
                "🏠 Bosh menyu",
                reply_markup=create_reply_keyboard([
                    ['📝 Test yechish', '📊 Natijalar'],
                    ['ℹ️ Yordam']
                ])
            )
            await state.clear()
            return
        
        state_data = await state.get_data()
        available_tests = state_data.get('available_tests', {})
        
        # Find selected test
        selected_test = None
        for test_id, test_data in available_tests.items():
            test_name = test_data.get('name', f'Test {test_id[:8]}')
            if test_name in message.text:
                selected_test = test_data
                selected_test['id'] = test_id
                break
        
        if not selected_test:
            await safe_send_message(
                message,
                "❌ Test topilmadi. Iltimos, ro'yxatdan birini tanlang."
            )
            return
        
        questions = selected_test.get('questions', [])
        if not questions:
            await safe_send_message(
                message,
                "❌ Bu testda savollar mavjud emas."
            )
            return
        
        # Initialize test session with enhanced data preservation
        test_session = {
            'test_id': selected_test['id'],
            'test_name': selected_test.get('name', 'Test'),
            'questions': questions,
            'current_question': 0,
            'answers': [],
            'start_time': time.time(),
            'user_registration': state_data.get('user_registration'),
            'age_group': state_data.get('age_group')
        }
        
        await state.update_data(test_session=test_session)
        
        # Show first question
        await show_question(message, state)
        await state.set_state(BotStates.test_in_progress)
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'taking_test', 'user_id': message.from_user.id},
            message
        )

async def show_question(message: Message, state: FSMContext):
    """Display question with enhanced formatting and navigation"""
    try:
        state_data = await state.get_data()
        test_session = state_data.get('test_session', {})
        
        questions = test_session.get('questions', [])
        current_q = test_session.get('current_question', 0)
        
        if current_q >= len(questions):
            await complete_test(message, state)
            return
        
        question = questions[current_q]
        question_text = question.get('question', '')
        options = question.get('options', [])
        
        # Format question display
        display_text = (
            f"📚 <b>{test_session.get('test_name', 'Test')}</b>\n\n"
            f"📝 <b>Savol {current_q + 1}/{len(questions)}:</b>\n\n"
            f"{question_text}\n\n"
        )
        
        if options:
            display_text += "<b>Javob variantlari:</b>\n"
            option_labels = ['A', 'B', 'C', 'D', 'E', 'F']
            
            for i, option in enumerate(options[:6]):  # Max 6 options
                if i < len(option_labels):
                    display_text += f"{option_labels[i]}) {option}\n"
            
            # Create option buttons
            keyboard = []
            for i, option in enumerate(options[:6]):
                if i < len(option_labels):
                    keyboard.append([f"{option_labels[i]}) {option[:30]}{'...' if len(option) > 30 else ''}"])
        else:
            display_text += "<i>Javob variantlari mavjud emas</i>\n"
            keyboard = [['Keyingi savol']]
        
        # Add navigation buttons
        navigation_row = []
        if current_q > 0:
            navigation_row.append('⬅️ Oldingi')
        navigation_row.append('🏁 Testni yakunlash')
        
        if navigation_row:
            keyboard.append(navigation_row)
        
        await safe_send_message(
            message,
            display_text,
            reply_markup=create_reply_keyboard(keyboard)
        )
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'action': 'show_question', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.test_in_progress))
async def process_answer(message: Message, state: FSMContext):
    """Process test answer with comprehensive session management"""
    try:
        state_data = await state.get_data()
        test_session = state_data.get('test_session', {})
        
        if message.text == "🏁 Testni yakunlash":
            await complete_test(message, state)
            return
        
        if message.text == "⬅️ Oldingi":
            current_q = test_session.get('current_question', 0)
            if current_q > 0:
                test_session['current_question'] = current_q - 1
                # Remove last answer if going back
                if test_session.get('answers') and len(test_session['answers']) > current_q - 1:
                    test_session['answers'] = test_session['answers'][:current_q - 1]
                
                await state.update_data(test_session=test_session)
                await show_question(message, state)
            return
        
        # Process answer selection
        current_q = test_session.get('current_question', 0)
        questions = test_session.get('questions', [])
        
        if current_q >= len(questions):
            return
        
        question = questions[current_q]
        options = question.get('options', [])
        
        # Determine selected answer
        selected_answer = -1
        answer_text = message.text
        
        # Check if it's a formatted option (A), B), etc.)
        for i, option in enumerate(options):
            option_labels = ['A', 'B', 'C', 'D', 'E', 'F']
            if i < len(option_labels):
                if message.text.startswith(f"{option_labels[i]})"):
                    selected_answer = i
                    answer_text = option
                    break
        
        # If not found, try to match the text
        if selected_answer == -1:
            for i, option in enumerate(options):
                if message.text.strip() == option.strip():
                    selected_answer = i
                    answer_text = option
                    break
        
        # Save answer
        answers = test_session.get('answers', [])
        
        # Ensure answers list is long enough
        while len(answers) <= current_q:
            answers.append({'answer': -1, 'text': '', 'time_taken': 0})
        
        answers[current_q] = {
            'answer': selected_answer,
            'text': answer_text,
            'time_taken': time.time() - test_session.get('start_time', time.time())
        }
        
        test_session['answers'] = answers
        test_session['current_question'] = current_q + 1
        
        await state.update_data(test_session=test_session)
        
        # Show next question or complete test
        if test_session['current_question'] >= len(questions):
            await complete_test(message, state)
        else:
            await show_question(message, state)
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'test_in_progress', 'user_id': message.from_user.id},
            message
        )

async def complete_test(message: Message, state: FSMContext):
    """Complete test with comprehensive result calculation and storage"""
    try:
        state_data = await state.get_data()
        test_session = state_data.get('test_session', {})
        
        questions = test_session.get('questions', [])
        answers = test_session.get('answers', [])
        user_registration = test_session.get('user_registration', {})
        
        # Calculate score
        correct_answers = 0
        total_questions = len(questions)
        
        for i, (question, answer) in enumerate(zip(questions, answers)):
            correct_answer = question.get('correct_answer', 0)
            user_answer = answer.get('answer', -1)
            
            if user_answer == correct_answer:
                correct_answers += 1
        
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Create result record
        result_record = {
            'id': str(uuid.uuid4()),
            'user_id': message.from_user.id,
            'registration_id': user_registration.get('registration_id', ''),
            'child_name': user_registration.get('child_name', ''),
            'test_id': test_session.get('test_id', ''),
            'test_name': test_session.get('test_name', 'Test'),
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score': score_percentage,
            'age': int(user_registration.get('age', 0)),
            'age_group': test_session.get('age_group', ''),
            'completion_time': datetime.now(timezone.utc).isoformat(),
            'time_taken': time.time() - test_session.get('start_time', time.time()),
            'answers': answers,
            'region': user_registration.get('region', ''),
            'district': user_registration.get('district', '')
        }
        
        # Save result
        results = await data_manager.load_data('results')
        results.append(result_record)
        await data_manager.save_data('results', results)
        
        # Update statistics
        asyncio.create_task(data_manager.update_statistics())
        
        # Create result message
        performance_emoji = "🥇" if score_percentage >= 90 else "🥈" if score_percentage >= 70 else "🥉" if score_percentage >= 50 else "📝"
        
        result_text = (
            f"{performance_emoji} <b>Test yakunlandi!</b>\n\n"
            f"📚 <b>Test:</b> {test_session.get('test_name', 'Test')}\n"
            f"👶 <b>Foydalanuvchi:</b> {user_registration.get('child_name', 'Noma\'lum')}\n"
            f"📊 <b>Natija:</b> {correct_answers}/{total_questions} ({score_percentage:.1f}%)\n"
            f"⏱️ <b>Vaqt:</b> {int(result_record['time_taken'] // 60)}:{int(result_record['time_taken'] % 60):02d}\n\n"
        )
        
        if score_percentage >= 90:
            result_text += "🎉 <b>A'lo natija!</b> Siz juda yaxshi bilim ko'rsatdingiz!"
        elif score_percentage >= 70:
            result_text += "👍 <b>Yaxshi natija!</b> Davom eting!"
        elif score_percentage >= 50:
            result_text += "📚 <b>O'rtacha natija.</b> Ko'proq mashq qiling!"
        else:
            result_text += "📖 <b>Mashq qilish kerak.</b> Ko'proq o'qing va qayta urinib ko'ring!"
        
        result_text += (
            f"\n\n📋 <b>Natija ID:</b> <code>{result_record['id'][:8]}</code>\n"
            f"📅 <b>Sana:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        
        keyboard = [
            ['📊 Batafsil natija', '📝 Yana test yechish'],
            ['🏠 Bosh menyu']
        ]
        
        await safe_send_message(
            message,
            result_text,
            reply_markup=create_reply_keyboard(keyboard)
        )
        
        await state.clear()
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'action': 'complete_test', 'user_id': message.from_user.id},
            message
        )

# ═══════════════════════════════════════════════════════════════════════════════════
# ENHANCED ADMIN PANEL WITH ZERO-DELAY OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════════

@dp.message(Command('admin'))
async def cmd_admin(message: Message, state: FSMContext):
    """Enhanced admin panel with comprehensive functionality"""
    start_time = time.time()
    
    try:
        if not await is_admin(message.from_user.id):
            await safe_send_message(
                message,
                "❌ Sizga admin paneliga kirish ruxsati yo'q."
            )
            return
        
        await data_manager.track_bot_user(message.from_user)
        await state.clear()
        
        # Get system statistics
        stats = await data_manager.load_data('statistics')
        perf_stats = perf_monitor.get_stats()
        
        is_super = await is_super_admin(message.from_user.id)
        
        admin_text = (
            "🔧 <b>Admin Panel</b>\n\n"
            f"👤 <b>Admin:</b> {message.from_user.first_name}\n"
            f"🛡️ <b>Ruxsat:</b> {'Super Admin' if is_super else 'Admin'}\n\n"
            f"📊 <b>Tizim statistikasi:</b>\n"
            f"👥 Ro'yxatdan o'tganlar: {stats.get('total_registered_users', 0)}\n"
            f"📝 Jami testlar: {stats.get('test_statistics', {}).get('total_tests_taken', 0)}\n"
            f"⚡ Faol sessiyalar: {perf_stats.get('active_sessions', 0)}\n"
            f"⏱️ O'rtacha javob vaqti: {perf_stats.get('avg_response_time', 0):.2f}s\n\n"
            "Quyidagi funksiyalardan birini tanlang:"
        )
        
        keyboard = [
            ['📊 Statistika', '👥 Foydalanuvchilar'],
            ['📝 Testlar boshqaruvi', '📢 Xabar yuborish'],
            ['📄 Export', '⚙️ Sozlamalar']
        ]
        
        if is_super:
            keyboard.append(['👮‍♂️ Admin boshqaruvi', '🔧 Tizim sozlari'])
        
        keyboard.append(['🔙 Orqaga'])
        
        await safe_send_message(
            message,
            admin_text,
            reply_markup=create_reply_keyboard(keyboard)
        )
        await state.set_state(BotStates.admin_menu)
        
        perf_monitor.record_request(time.time() - start_time, "admin_panel")
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'command': 'admin', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.admin_menu))
async def admin_menu_handler(message: Message, state: FSMContext):
    """Handle admin menu selections with enhanced functionality"""
    try:
        if not await is_admin(message.from_user.id):
            await state.clear()
            return
        
        if message.text == "🔙 Orqaga":
            await safe_send_message(
                message,
                "🏠 Bosh menyu",
                reply_markup=create_reply_keyboard([
                    ['📝 Test yechish', '📊 Natijalar'],
                    ['ℹ️ Yordam']
                ])
            )
            await state.clear()
            return
        
        elif message.text == "📊 Statistika":
            await show_admin_statistics(message, state)
        
        elif message.text == "👥 Foydalanuvchilar":
            await show_user_management(message, state)
        
        elif message.text == "📝 Testlar boshqaruvi":
            await show_test_management(message, state)
        
        elif message.text == "📢 Xabar yuborish":
            await show_broadcast_menu(message, state)
        
        elif message.text == "📄 Export":
            await show_export_menu(message, state)
        
        elif message.text == "⚙️ Sozlamalar":
            await show_settings_menu(message, state)
        
        elif message.text == "👮‍♂️ Admin boshqaruvi" and await is_super_admin(message.from_user.id):
            await show_admin_management(message, state)
        
        elif message.text == "🔧 Tizim sozlari" and await is_super_admin(message.from_user.id):
            await show_system_settings(message, state)
        
        else:
            await safe_send_message(
                message,
                "❓ Noto'g'ri tanlov. Iltimos, menyudan birini tanlang."
            )
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'admin_menu', 'user_id': message.from_user.id},
            message
        )

async def show_admin_statistics(message: Message, state: FSMContext):
    """Show comprehensive admin statistics"""
    try:
        stats = await data_manager.load_data('statistics')
        users = await data_manager.load_data('users')
        results = await data_manager.load_data('results')
        bot_users = await data_manager.load_data('bot_users')
        perf_stats = perf_monitor.get_stats()
        
        # Calculate additional statistics
        recent_registrations = len([
            u for u in users.values() 
            if 'registration_date' in u and 
            (datetime.now(timezone.utc) - datetime.fromisoformat(u['registration_date'].replace('Z', '+00:00'))).days <= 7
        ])
        
        recent_tests = len([
            r for r in results 
            if 'completion_time' in r and 
            (datetime.now(timezone.utc) - datetime.fromisoformat(r['completion_time'].replace('Z', '+00:00'))).days <= 7
        ])
        
        # Regional breakdown
        regional_text = ""
        regional_stats = stats.get('regional_statistics', {})
        top_regions = sorted(
            regional_stats.items(),
            key=lambda x: x[1].get('total_users', 0),
            reverse=True
        )[:5]
        
        for region, region_data in top_regions:
            if region_data.get('total_users', 0) > 0:
                regional_text += f"• {region}: {region_data['total_users']}\n"
        
        stats_text = (
            f"📊 <b>Batafsil statistika</b>\n\n"
            f"👥 <b>Foydalanuvchilar:</b>\n"
            f"• Jami ro'yxatdan o'tgan: {len(users)}\n"
            f"• So'nggi 7 kun: {recent_registrations}\n"
            f"• Bot foydalanuvchilari: {len(bot_users)}\n\n"
            
            f"📝 <b>Testlar:</b>\n"
            f"• Jami yechilgan: {len(results)}\n"
            f"• So'nggi 7 kun: {recent_tests}\n"
            f"• O'rtacha ball: {stats.get('test_statistics', {}).get('average_score', 0):.1f}%\n"
            f"• Yuqori natija (70%+): {stats.get('test_statistics', {}).get('high_scorers_70plus', 0)}\n\n"
            
            f"🌍 <b>Eng faol hududlar:</b>\n{regional_text}\n"
            
            f"⚡ <b>Tizim holati:</b>\n"
            f"• Faol sessiyalar: {perf_stats.get('active_sessions', 0)}\n"
            f"• O'rtacha javob vaqti: {perf_stats.get('avg_response_time', 0):.2f}s\n"
            f"• Xatoliklar soni: {sum(perf_stats.get('error_counts', {}).values())}\n\n"
            
            f"📅 <b>So'nggi yangilanish:</b>\n"
            f"{stats.get('last_updated', 'Noma\'lum')}"
        )
        
        keyboard = [
            ['🔄 Yangilash', '📄 Export'],
            ['🔙 Admin panel']
        ]
        
        await safe_send_message(
            message,
            stats_text,
            reply_markup=create_reply_keyboard(keyboard)
        )
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'action': 'show_admin_statistics', 'user_id': message.from_user.id},
            message
        )

async def show_export_menu(message: Message, state: FSMContext):
    """Show export menu with multiple format options"""
    try:
        export_text = (
            "📄 <b>Export ma'lumotlari</b>\n\n"
            "Quyidagi ma'lumotlarni export qilishingiz mumkin:\n\n"
            "📋 Formatlar:\n"
            "• Excel (.xlsx)\n"
            "• PDF\n"
            "• JSON\n\n"
            "Ma'lumot turini tanlang:"
        )
        
        keyboard = [
            ['👥 Foydalanuvchilar (Excel)', '👥 Foydalanuvchilar (PDF)'],
            ['📊 Statistika (Excel)', '📊 Statistika (PDF)'],
            ['📝 Test natijalari (Excel)', '📝 Test natijalari (PDF)'],
            ['💾 Barcha ma\'lumotlar (JSON)'],
            ['🔙 Admin panel']
        ]
        
        await safe_send_message(
            message,
            export_text,
            reply_markup=create_reply_keyboard(keyboard)
        )
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'action': 'show_export_menu', 'user_id': message.from_user.id},
            message
        )

# ═══════════════════════════════════════════════════════════════════════════════════
# DOCUMENT UPLOAD AND PROCESSING WITH MULTI-FORMAT SUPPORT
# ═══════════════════════════════════════════════════════════════════════════════════

@dp.message(F.document)
async def handle_document_upload(message: Message, state: FSMContext):
    """Handle document uploads with multi-format processing"""
    try:
        if not await is_admin(message.from_user.id):
            await safe_send_message(
                message,
                "❌ Faqat adminlar hujjat yuklashi mumkin."
            )
            return
        
        document = message.document
        
        # Validate document
        if not validate_document_format(document.file_name, document.mime_type):
            await safe_send_message(
                message,
                f"❌ <b>Qo'llab-quvvatlanmaydigan fayl formati!</b>\n\n"
                f"📁 <b>Fayl:</b> {document.file_name}\n"
                f"📄 <b>Format:</b> {document.mime_type}\n\n"
                f"✅ <b>Qo'llab-quvvatlangan formatlar:</b>\n"
                f"• Word: .doc, .docx\n"
                f"• Excel: .xls, .xlsx\n"
                f"• PDF: .pdf\n"
                f"• Matn: .txt"
            )
            return
        
        # Check file size (max 20MB)
        if document.file_size > 20 * 1024 * 1024:
            await safe_send_message(
                message,
                "❌ Fayl hajmi juda katta! Maksimal hajm: 20MB"
            )
            return
        
        processing_msg = await safe_send_message(
            message,
            f"⏳ <b>Hujjatni qayta ishlamoqda...</b>\n\n"
            f"📁 <b>Fayl:</b> {document.file_name}\n"
            f"📊 <b>Hajm:</b> {document.file_size / 1024:.1f} KB\n"
            f"📄 <b>Tur:</b> {get_document_type(document.file_name, document.mime_type)}\n\n"
            f"Iltimos kuting..."
        )
        
        try:
            # Download file
            file = await bot.get_file(document.file_id)
            file_content = await bot.download_file(file.file_path)
            
            # Extract text
            extracted_text = await doc_processor.extract_text(
                file_content.read(),
                document.file_name,
                document.mime_type
            )
            
            # Parse questions
            questions = await doc_processor.parse_questions(extracted_text)
            
            await safe_edit_message(
                processing_msg,
                f"✅ <b>Hujjat muvaffaqiyatli qayta ishlandi!</b>\n\n"
                f"📁 <b>Fayl:</b> {document.file_name}\n"
                f"📝 <b>Topilgan savollar:</b> {len(questions)}\n\n"
                f"{'✅ Savollar topildi!' if questions else '❌ Savollar topilmadi!'}\n\n"
                f"Davom etish uchun tanlov qiling:",
                reply_markup=create_reply_keyboard([
                    ['📝 Savollarni ko\'rish', '💾 Test sifatida saqlash'],
                    ['📄 Matn ko\'rish', '❌ Bekor qilish']
                ])
            )
            
            # Save processing data
            await state.update_data(
                document_processing={
                    'filename': document.file_name,
                    'extracted_text': extracted_text,
                    'questions': questions,
                    'file_size': document.file_size,
                    'mime_type': document.mime_type
                }
            )
            await state.set_state(BotStates.processing_document)
        
        except Exception as e:
            await safe_edit_message(
                processing_msg,
                f"❌ <b>Hujjatni qayta ishlashda xatolik!</b>\n\n"
                f"Xatolik: {str(e)}\n\n"
                f"Iltimos, qaytadan urinib ko'ring yoki boshqa formatda yuklang."
            )
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'action': 'document_upload', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.processing_document))
async def handle_document_processing_choice(message: Message, state: FSMContext):
    """Handle document processing choices"""
    try:
        state_data = await state.get_data()
        doc_data = state_data.get('document_processing', {})
        
        if message.text == "❌ Bekor qilish":
            await safe_send_message(
                message,
                "❌ Hujjat qayta ishlash bekor qilindi.",
                reply_markup=create_reply_keyboard([['🔙 Admin panel']])
            )
            await state.clear()
            return
        
        elif message.text == "📄 Matn ko'rish":
            extracted_text = doc_data.get('extracted_text', '')
            
            if len(extracted_text) > 3000:
                # Split long text
                text_parts = [extracted_text[i:i+3000] for i in range(0, len(extracted_text), 3000)]
                for i, part in enumerate(text_parts[:3]):  # Show max 3 parts
                    await safe_send_message(
                        message,
                        f"📄 <b>Matn qismi {i+1}/{min(len(text_parts), 3)}:</b>\n\n"
                        f"<pre>{part}</pre>"
                    )
            else:
                await safe_send_message(
                    message,
                    f"📄 <b>Chiqarilgan matn:</b>\n\n<pre>{extracted_text}</pre>"
                )
        
        elif message.text == "📝 Savollarni ko'rish":
            questions = doc_data.get('questions', [])
            
            if not questions:
                await safe_send_message(
                    message,
                    "❌ Hech qanday savol topilmadi."
                )
                return
            
            questions_text = f"📝 <b>Topilgan savollar ({len(questions)} ta):</b>\n\n"
            
            for i, question in enumerate(questions[:5], 1):  # Show first 5 questions
                questions_text += f"<b>{i}. {question.get('question', '')[:100]}...</b>\n"
                
                options = question.get('options', [])
                if options:
                    for j, option in enumerate(options[:4], 1):
                        questions_text += f"   {j}) {option[:50]}...\n"
                
                questions_text += "\n"
            
            if len(questions) > 5:
                questions_text += f"... va yana {len(questions) - 5} ta savol"
            
            await safe_send_message(message, questions_text)
        
        elif message.text == "💾 Test sifatida saqlash":
            questions = doc_data.get('questions', [])
            
            if not questions:
                await safe_send_message(
                    message,
                    "❌ Saqlash uchun savollar topilmadi."
                )
                return
            
            # Ask for test details
            await safe_send_message(
                message,
                f"💾 <b>Testni saqlash</b>\n\n"
                f"📝 Savollar soni: {len(questions)}\n\n"
                f"Test nomini kiriting:"
            )
            await state.set_state(BotStates.confirming_test_import)
        
        else:
            await safe_send_message(
                message,
                "❓ Noto'g'ri tanlov. Iltimos, tugmalardan birini bosing."
            )
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'processing_document', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.confirming_test_import))
async def confirm_test_import(message: Message, state: FSMContext):
    """Confirm and save imported test"""
    try:
        test_name = message.text.strip()
        
        if len(test_name) < 3:
            await safe_send_message(
                message,
                "❌ Test nomi juda qisqa! Kamida 3 ta belgi kiriting."
            )
            return
        
        state_data = await state.get_data()
        doc_data = state_data.get('document_processing', {})
        questions = doc_data.get('questions', [])
        
        if not questions:
            await safe_send_message(
                message,
                "❌ Saqlash uchun savollar mavjud emas."
            )
            return
        
        # Create test data
        test_id = str(uuid.uuid4())
        test_data = {
            'id': test_id,
            'name': test_name,
            'questions': questions,
            'created_by': message.from_user.id,
            'created_date': datetime.now(timezone.utc).isoformat(),
            'source_file': doc_data.get('filename', ''),
            'total_questions': len(questions)
        }
        
        # Ask for age group
        await safe_send_message(
            message,
            f"👶 <b>Yosh guruhini tanlang:</b>\n\n"
            f"📝 <b>Test:</b> {test_name}\n"
            f"📊 <b>Savollar:</b> {len(questions)} ta\n\n"
            f"Bu test qaysi yosh guruhi uchun?",
            reply_markup=create_reply_keyboard([
                ['👶 7-10 yosh', '🧒 11-14 yosh'],
                ['❌ Bekor qilish']
            ])
        )
        
        # Save test data for final confirmation
        await state.update_data(test_data=test_data)
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'confirming_test_import', 'user_id': message.from_user.id},
            message
        )

# ═══════════════════════════════════════════════════════════════════════════════════
# ENHANCED BROADCAST SYSTEM WITH DELIVERY TRACKING
# ═══════════════════════════════════════════════════════════════════════════════════

async def show_broadcast_menu(message: Message, state: FSMContext):
    """Show broadcast menu with enhanced options"""
    try:
        bot_users = await data_manager.load_data('bot_users')
        users = await data_manager.load_data('users')
        
        broadcast_text = (
            f"📢 <b>Xabar yuborish tizimi</b>\n\n"
            f"📊 <b>Statistika:</b>\n"
            f"• Bot foydalanuvchilari: {len(bot_users)}\n"
            f"• Ro'yxatdan o'tganlar: {len(users)}\n\n"
            f"Kimga xabar yuborishni tanlang:"
        )
        
        keyboard = [
            ['📢 Barcha bot foydalanuvchilariga', '✅ Faqat ro\'yxatdan o\'tganlarga'],
            ['🎯 Hududiy xabar', '📝 Test xabar'],
            ['📋 Xabar tarixi', '🔙 Admin panel']
        ]
        
        await safe_send_message(
            message,
            broadcast_text,
            reply_markup=create_reply_keyboard(keyboard)
        )
        await state.set_state(BotStates.admin_broadcast)
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'action': 'show_broadcast_menu', 'user_id': message.from_user.id},
            message
        )

@dp.message(StateFilter(BotStates.admin_broadcast))
async def handle_broadcast_selection(message: Message, state: FSMContext):
    """Handle broadcast type selection"""
    try:
        if message.text == "🔙 Admin panel":
            await safe_send_message(
                message,
                "🔧 Admin panel",
                reply_markup=create_reply_keyboard([
                    ['📊 Statistika', '👥 Foydalanuvchilar'],
                    ['📝 Testlar boshqaruvi', '📢 Xabar yuborish'],
                    ['📄 Export', '⚙️ Sozlamalar'],
                    ['🔙 Orqaga']
                ])
            )
            await state.set_state(BotStates.admin_menu)
            return
        
        broadcast_type = None
        if message.text == "📢 Barcha bot foydalanuvchilariga":
            broadcast_type = "all_users"
        elif message.text == "✅ Faqat ro'yxatdan o'tganlarga":
            broadcast_type = "registered_users"
        elif message.text == "📝 Test xabar":
            broadcast_type = "test_message"
        
        if broadcast_type:
            await safe_send_message(
                message,
                f"✉️ <b>Xabar matnini kiriting:</b>\n\n"
                f"📝 Xabar HTML formatida bo'lishi mumkin.\n"
                f"⚠️ Ehtiyotkorlik bilan yozing - bu xabar ko'p kishiga yuboriladi!",
                reply_markup=create_reply_keyboard([['❌ Bekor qilish']])
            )
            
            await state.update_data(broadcast_type=broadcast_type)
    
    except Exception as e:
        await error_handler.handle_error(
            e,
            {'state': 'admin_broadcast', 'user_id': message.from_user.id},
            message
        )

# ═══════════════════════════════════════════════════════════════════════════════════
# STARTUP AND CLEANUP ROUTINES
# ═══════════════════════════════════════════════════════════════════════════════════

async def set_bot_commands():
    """Set bot commands with comprehensive list"""
    commands = [
        BotCommand(command="start", description="🏠 Botni ishga tushirish"),
        BotCommand(command="register", description="📝 Ro'yxatdan o'tish"),
        BotCommand(command="test", description="📚 Test yechish"),
        BotCommand(command="results", description="📊 Natijalar"),
        BotCommand(command="help", description="ℹ️ Yordam"),
        BotCommand(command="admin", description="🔧 Admin panel (faqat adminlar uchun)")
    ]
    
    await bot.set_my_commands(commands)
    logger.info("Bot commands set successfully")

async def startup():
    """Enhanced startup routine with comprehensive initialization"""
    try:
        logger.info("🚀 Starting Kitobxon Kids Bot v3.0...")
        
        # Initialize data manager
        logger.info("📁 Initializing data manager...")
        await data_manager._initialize_data()
        
        # Set bot commands
        await set_bot_commands()
        
        # Start background tasks
        asyncio.create_task(periodic_cleanup())
        asyncio.create_task(performance_monitor_task())
        
        logger.info("✅ Bot startup completed successfully!")
        
        # Send startup notification to super admin
        try:
            await bot.send_message(
                SUPER_ADMIN_ID,
                f"🚀 <b>Bot ishga tushdi!</b>\n\n"
                f"⏰ <b>Vaqt:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
                f"🤖 <b>Versiya:</b> 3.0 (Optimized)\n"
                f"⚡ <b>Holat:</b> Tayyorlash tugadi"
            )
        except:
            pass  # Don't fail startup if notification fails
    
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

async def shutdown():
    """Enhanced shutdown routine with cleanup"""
    try:
        logger.info("🛑 Shutting down bot...")
        
        # Close session
        if bot.session:
            await bot.session.close()
        
        # Cleanup temp files
        await export_manager.cleanup_temp_files()
        
        # Final data cleanup
        await data_manager.cleanup_old_data()
        
        logger.info("✅ Bot shutdown completed successfully!")
    
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

async def periodic_cleanup():
    """Periodic cleanup task for maintenance"""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            
            # Cleanup old data
            await data_manager.cleanup_old_data()
            
            # Cleanup temp files
            await export_manager.cleanup_temp_files()
            
            # Force garbage collection
            gc.collect()
            
            logger.info("🧹 Periodic cleanup completed")
        
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

async def performance_monitor_task():
    """Performance monitoring background task"""
    while True:
        try:
            await asyncio.sleep(300)  # Monitor every 5 minutes
            
            stats = perf_monitor.get_stats()
            
            # Log performance statistics
            logger.info(
                f"⚡ Performance: "
                f"Sessions: {stats['active_sessions']}, "
                f"Avg response: {stats['avg_response_time']:.2f}s, "
                f"Errors: {sum(stats['error_counts'].values())}"
            )
            
            # Alert on high error rate
            error_count = sum(stats['error_counts'].values())
            if error_count > 50:  # Alert threshold
                try:
                    await bot.send_message(
                        SUPER_ADMIN_ID,
                        f"⚠️ <b>Yuqori xatolik darajasi!</b>\n\n"
                        f"🚨 Xatoliklar: {error_count}\n"
                        f"📊 Statistika: {stats}"
                    )
                except:
                    pass
        
        except Exception as e:
            logger.error(f"Performance monitor error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════════

async def main():
    """Main application entry point with enhanced error handling"""
    try:
        logger.info("Starting Kitobxon Kids Educational Bot v3.0")
        logger.info("Optimized for 10,000+ concurrent users")
        
        # Initialize bot
        await startup()
        
        # Start polling
        logger.info("🔄 Starting bot polling...")
        await dp.start_polling(bot, skip_updates=True)
    
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        logger.error(traceback.format_exc())
    finally:
        await shutdown()

if __name__ == "__main__":
    # Set up event loop policy for better performance on Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the bot
    asyncio.run(main())
