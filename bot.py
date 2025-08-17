import logging
import asyncio
import json
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import random

# Database imports
from database import (
    DatabaseService, init_database, User, Question, TestResult, 
    TestAnswer, Feedback, RegionData
)

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, KeyboardButton, ReplyKeyboardMarkup,
    ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup,
    CallbackQuery, BufferedInputFile
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Excel and PDF libraries
try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    openpyxl = None

try:
    from reportlab.lib.pagesizes import letter, A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
except ImportError:
    SimpleDocTemplate = None

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "7570796885:AAFkj7iY05fQUG21015viY7Gy8ifXXcnOpA")
ADMINS = [int(x) for x in os.getenv("ADMIN_IDS", "6578706277,7853664401").split(",")]

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot and Dispatcher
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# FSM States
class RegistrationStates(StatesGroup):
    waiting_for_child_name = State()
    waiting_for_parent_name = State()
    waiting_for_age_group = State()
    waiting_for_region = State()
    waiting_for_manual_region = State()
    waiting_for_district = State()
    waiting_for_manual_district = State()
    waiting_for_mahalla = State()

class TestStates(StatesGroup):
    taking_test = State()

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_new_question = State()
    waiting_for_new_options = State()
    waiting_for_correct_answer = State()
    waiting_for_age_group_selection = State()
    waiting_for_bulk_questions = State()

class FeedbackStates(StatesGroup):
    waiting_for_feedback = State()

# Data storage
active_tests = {}

# Regions data
def init_regions_data():
    regions_data = {
        "Toshkent": {
            "districts": ["Chilonzor", "Shayxontohur", "Yunusobod", "Mirzo Ulug'bek", "Yakkasaroy", "Mirobod"],
            "mahallas": {
                "Chilonzor": ["1-mahalla", "2-mahalla", "3-mahalla"],
                "Shayxontohur": ["Markaziy", "Sharqiy", "G'arbiy"],
                "Yunusobod": ["Yangi Yunusobod", "Eski Yunusobod"]
            }
        },
        "Samarqand": {
            "districts": ["Samarqand shahar", "Urgut", "Bulung'ur", "Ishtixon", "Kattaqo'rg'on"],
            "mahallas": {
                "Samarqand shahar": ["Registon", "Siob", "Darvozaboy"],
                "Urgut": ["Markaz", "Yangiobod"],
                "Bulung'ur": ["Markaz", "Qishloq"]
            }
        },
        "Farg'ona": {
            "districts": ["Farg'ona shahar", "Marg'ilon", "Qo'qon", "Beshariq", "Bog'dod"],
            "mahallas": {
                "Farg'ona shahar": ["Markaz", "Yangi shahar"],
                "Marg'ilon": ["Ipak yo'li", "Hunarmandchilik"],
                "Qo'qon": ["Eski shahar", "Yangi shahar"]
            }
        },
        "Andijon": {
            "districts": ["Andijon shahar", "Xo'jaobod", "Asaka", "Baliqchi", "Bo'z"],
            "mahallas": {
                "Andijon shahar": ["Markaz", "Sanoat"],
                "Xo'jaobod": ["Qishloq", "Shahar"],
                "Asaka": ["Markaz"]
            }
        },
        "Namangan": {
            "districts": ["Namangan shahar", "To'raqo'rg'on", "Uchqo'rg'on", "Chust", "Pop"],
            "mahallas": {
                "Namangan shahar": ["Markaz", "Sanoat zone"],
                "To'raqo'rg'on": ["Markaz", "Qishloq"],
                "Chust": ["Hunarmandchilik", "Dehqonchilik"]
            }
        },
        "Qashqadaryo": {
            "districts": ["Qarshi", "Shahrisabz", "Kitob", "Yakkabog'", "Chiroqchi"],
            "mahallas": {
                "Qarshi": ["Markaz", "Sanoat"],
                "Shahrisabz": ["Tarixiy markaz", "Yangi shahar"],
                "Kitob": ["Markaz"]
            }
        },
        "Surxondaryo": {
            "districts": ["Termiz", "Denov", "Qaraqo'l", "Sho'rchi", "Muzrabot"],
            "mahallas": {
                "Termiz": ["Markaz", "Port zone"],
                "Denov": ["Markaz", "Qishloq"],
                "Qaraqo'l": ["Markaz"]
            }
        },
        "Sirdaryo": {
            "districts": ["Guliston", "Yangiyer", "Sirdaryo", "Boyovut", "Mirzaobod"],
            "mahallas": {
                "Guliston": ["Markaz", "Sanoat"],
                "Yangiyer": ["Markaz", "Qishloq"],
                "Sirdaryo": ["Markaz"]
            }
        },
        "Jizzax": {
            "districts": ["Jizzax shahar", "G'allaorol", "Zomin", "Baxtiyor", "Mirzacho'l"],
            "mahallas": {
                "Jizzax shahar": ["Markaz", "Yangi shahar"],
                "G'allaorol": ["Markaz", "Qishloq"],
                "Zomin": ["Tog'li", "Tekislik"]
            }
        },
        "Navoiy": {
            "districts": ["Navoiy shahar", "Zarafshon", "Nurota", "Karmana", "Qiziltepa"],
            "mahallas": {
                "Navoiy shahar": ["Markaz", "Sanoat"],
                "Zarafshon": ["Oltin qazish", "Shahar"],
                "Nurota": ["Tarixiy", "Markaz"]
            }
        },
        "Buxoro": {
            "districts": ["Buxoro shahar", "G'ijduvon", "Kogon", "Olot", "Peshku"],
            "mahallas": {
                "Buxoro shahar": ["Eski shahar", "Yangi shahar"],
                "G'ijduvon": ["Markaz", "Qishloq"],
                "Kogon": ["Temir yo'l", "Markaz"]
            }
        },
        "Xorazm": {
            "districts": ["Urganch", "Xiva", "Bog'ot", "Gurlan", "Qo'shko'pir"],
            "mahallas": {
                "Urganch": ["Markaz", "Sanoat"],
                "Xiva": ["Ichan qal'a", "Tashqi shahar"],
                "Bog'ot": ["Markaz"]
            }
        }
    }
    return regions_data

# Initialize regions
regions_data = init_regions_data()

# Keyboard creation functions
def create_main_menu():
    """Main menu buttons - changed from phone request to register"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Ro'yxatdan o'tish")],  # Register instead of Send Phone
            [KeyboardButton(text="📚 Loyiha haqida")],
            [KeyboardButton(text="📋 Test topshirish")],
            [KeyboardButton(text="💬 Fikr bildirish")]
        ],
        resize_keyboard=True
    )
    return kb

def create_admin_menu():
    """Admin menu buttons"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Foydalanuvchilar ro'yxati")],
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="❓ Savollarni boshqarish")],
            [KeyboardButton(text="📢 Xabar yuborish")],
            [KeyboardButton(text="📤 Ma'lumotlarni eksport qilish")],
            [KeyboardButton(text="🔙 Oddiy foydalanuvchi rejimiga qaytish")]
        ],
        resize_keyboard=True
    )
    return kb

def create_export_menu():
    """Export menu buttons"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Excel formatida", callback_data="export_excel")],
            [InlineKeyboardButton(text="📄 PDF formatida", callback_data="export_pdf")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
        ]
    )
    return kb

def create_question_management_menu():
    """Question management menu"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Savol qo'shish", callback_data="add_question")],
            [InlineKeyboardButton(text="📝 Ko'p savol qo'shish", callback_data="add_bulk_questions")],
            [InlineKeyboardButton(text="👀 Savollarni ko'rish", callback_data="view_questions")],
            [InlineKeyboardButton(text="🗑 Savollarni tozalash", callback_data="clear_questions")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
        ]
    )
    return kb

# Enhanced Excel export function
async def export_to_excel() -> Optional[BufferedInputFile]:
    """Enhanced Excel export with better formatting"""
    if not openpyxl:
        return None
    
    try:
        # Load fresh data from database
        users = DatabaseService.get_all_users()
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Kitobxon Kids - Foydalanuvchilar"
        
        # Enhanced styling
        header_fill = PatternFill(start_color="1f4e79", end_color="1f4e79", fill_type="solid")
        header_font = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
        data_font = Font(name="Calibri", size=11)
        
        # Alternating row colors for better readability
        light_fill = PatternFill(start_color="f2f2f2", end_color="f2f2f2", fill_type="solid")
        dark_fill = PatternFill(start_color="e6e6e6", end_color="e6e6e6", fill_type="solid")
        
        # Border style
        thin_border = Border(
            left=Side(style='thin', color='CCCCCC'),
            right=Side(style='thin', color='CCCCCC'),
            top=Side(style='thin', color='CCCCCC'),
            bottom=Side(style='thin', color='CCCCCC')
        )
        
        # Create title
        ws.merge_cells('A1:J2')
        ws['A1'] = "📚 KITOBXON KIDS LOYIHASI - FOYDALANUVCHILAR MA'LUMOTLARI"
        ws['A1'].font = Font(name="Calibri", size=16, bold=True, color="1f4e79")
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws['A1'].fill = PatternFill(start_color="e1ecf4", end_color="e1ecf4", fill_type="solid")
        
        # Add generation date
        ws.merge_cells('A3:J3')
        ws['A3'] = f"Yaratilgan sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        ws['A3'].font = Font(name="Calibri", size=10, italic=True)
        ws['A3'].alignment = Alignment(horizontal='center')
        
        # Headers
        headers = [
            "№", "Bola ismi", "Ota-ona ismi", "Telefon", 
            "Yosh guruhi", "Viloyat", "Tuman", "Mahalla", 
            "Ro'yxat sanasi", "Testlar soni"
        ]
        
        # Apply headers
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=5, column=col)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = thin_border
        
        # Add user data with enhanced formatting
        for idx, user in enumerate(users, 1):
            row_num = idx + 5
            # Get test results count separately to avoid session issues
            test_count = DatabaseService.get_user_test_count(user.user_id)
            
            row_data = [
                idx,
                user.child_name,
                user.parent_name,
                user.phone or "Kiritilmagan",
                user.age_group,
                user.region,
                user.district,
                user.mahalla,
                user.registration_date.strftime('%d.%m.%Y') if user.registration_date else "",
                test_count
            ]
            
            for col, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_num, column=col)
                cell.value = value
                cell.font = data_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = thin_border
                
                # Alternating row colors
                if idx % 2 == 0:
                    cell.fill = light_fill
                else:
                    cell.fill = dark_fill
        
        # Auto-adjust column widths
        column_widths = [5, 20, 20, 15, 12, 15, 15, 15, 12, 10]
        for col, width in enumerate(column_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width
        
        # Add summary section
        summary_row = len(users) + 8
        ws.merge_cells(f'A{summary_row}:J{summary_row}')
        ws[f'A{summary_row}'] = f"📊 JAMI: {len(users)} ta foydalanuvchi ro'yxatdan o'tgan"
        ws[f'A{summary_row}'].font = Font(name="Calibri", size=14, bold=True, color="2e5266")
        ws[f'A{summary_row}'].alignment = Alignment(horizontal='center')
        
        # Regional statistics
        region_stats = {}
        for user in users:
            region = user.region
            region_stats[region] = region_stats.get(region, 0) + 1
        
        # Add regional breakdown
        stats_row = summary_row + 2
        ws.merge_cells(f'A{stats_row}:J{stats_row}')
        ws[f'A{stats_row}'] = "🗺️ VILOYATLAR BO'YICHA STATISTIKA:"
        ws[f'A{stats_row}'].font = Font(name="Calibri", size=12, bold=True, color="2e5266")
        ws[f'A{stats_row}'].alignment = Alignment(horizontal='center')
        
        stats_row += 1
        for region, count in sorted(region_stats.items()):
            ws[f'A{stats_row}'] = f"▪️ {region}: {count} ta foydalanuvchi"
            ws[f'A{stats_row}'].font = Font(name="Calibri", size=10)
            ws[f'A{stats_row}'].alignment = Alignment(horizontal='left')
            stats_row += 1
        
        # Save to BytesIO
        from io import BytesIO
        excel_data = BytesIO()
        wb.save(excel_data)
        excel_data.seek(0)
        
        filename = f"kitobxon_kids_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return BufferedInputFile(excel_data.read(), filename=filename)
        
    except Exception as e:
        logger.error(f"Excel export error: {e}")
        return None

# Fixed PDF export function
async def export_to_pdf() -> Optional[BufferedInputFile]:
    """Fixed PDF export with proper text spacing and no overlapping"""
    if not SimpleDocTemplate:
        return None
    
    try:
        from io import BytesIO
        
        # Load fresh data from database
        users = DatabaseService.get_all_users()
        
        # Create PDF buffer
        buffer = BytesIO()
        
        # Use landscape orientation for better table display
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=landscape(A4),
            topMargin=0.8*inch,
            bottomMargin=0.8*inch,
            leftMargin=0.6*inch,
            rightMargin=0.6*inch
        )
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=24,
            alignment=1,  # Center alignment
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=20,
            alignment=1,
            textColor=colors.grey,
            fontName='Helvetica'
        )
        
        # Add title with proper spacing
        title = Paragraph("KITOBXON KIDS LOYIHASI", title_style)
        subtitle = Paragraph(f"Foydalanuvchilar ma'lumotlari - {datetime.now().strftime('%d.%m.%Y %H:%M')}", subtitle_style)
        elements.append(title)
        elements.append(subtitle)
        elements.append(Spacer(1, 24))
        
        # Prepare table data with truncated text to prevent overlap
        headers = [
            "№", "Bola ismi", "Ota-ona", "Telefon", 
            "Yosh", "Viloyat", "Tuman", "Mahalla", "Sana", "Test"
        ]
        
        table_data = [headers]
        
        # Add user data with careful text truncation
        for idx, user in enumerate(users, 1):
            # Truncate long text to prevent overlap
            child_name = (user.child_name[:12] + "..." if len(user.child_name) > 12 else user.child_name)
            parent_name = (user.parent_name[:12] + "..." if len(user.parent_name) > 12 else user.parent_name)
            phone = user.phone[:11] if user.phone else "N/A"
            region = (user.region[:8] + "..." if len(user.region) > 8 else user.region)
            district = (user.district[:10] + "..." if len(user.district) > 10 else user.district)
            mahalla = (user.mahalla[:8] + "..." if len(user.mahalla) > 8 else user.mahalla)
            reg_date = user.registration_date.strftime('%d.%m.%Y') if user.registration_date else ""
            # Get test results count separately to avoid session issues
            test_count = str(DatabaseService.get_user_test_count(user.user_id))
            
            row = [
                str(idx), child_name, parent_name, phone, user.age_group,
                region, district, mahalla, reg_date, test_count
            ]
            table_data.append(row)
        
        # Create table with proper column widths to prevent overlap
        col_widths = [0.5*inch, 1.1*inch, 1.1*inch, 0.9*inch, 0.7*inch, 0.9*inch, 1.0*inch, 0.9*inch, 0.8*inch, 0.5*inch]
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Enhanced table style with proper spacing
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            
            # Data row styling with alternating colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Proper padding to prevent text overlap
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 24))
        
        # Add summary statistics with proper formatting
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=1,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        )
        
        summary_text = f"JAMI: {len(users)} ta foydalanuvchi ro'yxatdan o'tgan"
        summary = Paragraph(summary_text, summary_style)
        elements.append(summary)
        
        # Regional statistics
        region_stats = {}
        for user in users:
            region = user.region
            region_stats[region] = region_stats.get(region, 0) + 1
        
        if region_stats:
            elements.append(Spacer(1, 16))
            stats_title = Paragraph("VILOYATLAR BO'YICHA STATISTIKA:", summary_style)
            elements.append(stats_title)
            elements.append(Spacer(1, 8))
            
            # Create statistics table
            stats_data = [["Viloyat", "Foydalanuvchilar soni"]]
            for region, count in sorted(region_stats.items()):
                stats_data.append([region, str(count)])
            
            stats_table = Table(stats_data, colWidths=[2.5*inch, 1.5*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightcyan),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            elements.append(stats_table)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        filename = f"kitobxon_kids_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return BufferedInputFile(pdf_data, filename=filename)
        
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        return None

# Start command and main functions
@dp.message(CommandStart())
async def start_command(message: Message):
    """Bot start command"""
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name or "Foydalanuvchi"
    
    # Check if user is admin
    if message.from_user.id in ADMINS:
        welcome_text = f"🤖 **Admin rejimida xush kelibsiz, {first_name}!**\n\nSiz admin huquqlariga egasiz.\n\n🔧 Admin panel uchun: /admin\n👤 Oddiy foydalanuvchi rejimi uchun: pastdagi tugmalardan foydalaning"
    else:
        # Check if user is already registered
        user = DatabaseService.get_user(user_id)
        
        if user:
            welcome_text = f"🎉 **Qaytib kelganingizdan xursandmiz, {first_name}!**\n\nSiz allaqachon ro'yxatdan o'tgansiz. Testlarni topshirishni boshlashingiz yoki loyiha haqida ko'proq ma'lumot olishingiz mumkin."
        else:
            welcome_text = f"🌟 **Kitobxon Kids loyihasiga xush kelibsiz, {first_name}!**\n\n📚 Bu loyiha orqali siz:\n• Bilimlaringizni sinab ko'rishingiz\n• Kitobxonlik darajangizni baholashingiz\n• Qiziqarli savollar bilan tanishishingiz mumkin\n\n🎯 **Boshlash uchun ro'yxatdan o'ting!**"
    
    await message.answer(
        welcome_text,
        reply_markup=create_main_menu(),
        parse_mode="Markdown"
    )

@dp.message(Command("admin"))
async def admin_command(message: Message):
    """Admin command"""
    if message.from_user.id not in ADMINS:
        await message.answer("❌ Sizda admin huquqlari yo'q!")
        return
    
    await message.answer(
        "🔧 **Admin Panel**\n\nBoshqaruv paneliga xush kelibsiz!",
        reply_markup=create_admin_menu(),
        parse_mode="Markdown"
    )

# User registration handlers
@dp.message(F.text == "📝 Ro'yxatdan o'tish")
async def start_registration(message: Message, state: FSMContext):
    """Start registration process"""
    user_id = str(message.from_user.id)
    
    # Check if user is already registered
    existing_user = DatabaseService.get_user(user_id)
    if existing_user:
        await message.answer(
            f"✅ Siz allaqachon ro'yxatdan o'tgansiz!\n\n"
            f"👶 Bola ismi: {existing_user.child_name}\n"
            f"👨‍👩‍👧‍👦 Ota-ona: {existing_user.parent_name}\n"
            f"📚 Yosh guruhi: {existing_user.age_group}\n"
            f"🏢 Viloyat: {existing_user.region}\n"
            f"🏙 Tuman: {existing_user.district}",
            parse_mode="Markdown"
        )
        return
    
    await message.answer(
        "📝 **Ro'yxatdan o'tish boshlandi!**\n\n👶 Bolangizning to'liq ismini kiriting:",
        parse_mode="Markdown"
    )
    await state.set_state(RegistrationStates.waiting_for_child_name)

@dp.message(RegistrationStates.waiting_for_child_name)
async def get_child_name(message: Message, state: FSMContext):
    """Get child name"""
    await state.update_data(child_name=message.text.strip())
    
    await message.answer(
        "👨‍👩‍👧‍👦 **Ota-ona ismini kiriting:**\n\nTo'liq ism-sharifingizni yozing:",
        parse_mode="Markdown"
    )
    await state.set_state(RegistrationStates.waiting_for_parent_name)

@dp.message(RegistrationStates.waiting_for_parent_name)
async def get_parent_name(message: Message, state: FSMContext):
    """Get parent name"""
    await state.update_data(parent_name=message.text.strip())
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="7-10 yosh")],
            [KeyboardButton(text="11-14 yosh")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "📚 **Yosh guruhini tanlang:**",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await state.set_state(RegistrationStates.waiting_for_age_group)

@dp.message(RegistrationStates.waiting_for_age_group)
async def get_age_group(message: Message, state: FSMContext):
    """Get age group"""
    age_group = message.text.strip()
    
    if age_group not in ["7-10 yosh", "11-14 yosh"]:
        await message.answer("❌ Iltimos, tugmalardan birini tanlang!")
        return
    
    await state.update_data(age_group=age_group)
    
    # Region selection
    region_buttons = [[KeyboardButton(text=region)] for region in regions_data.keys()]
    region_buttons.append([KeyboardButton(text="🖊 Qo'lda kiriting")])
    
    kb = ReplyKeyboardMarkup(
        keyboard=region_buttons,
        resize_keyboard=True
    )
    
    await message.answer(
        "🏢 **Viloyatni tanlang:**",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await state.set_state(RegistrationStates.waiting_for_region)

@dp.message(RegistrationStates.waiting_for_region)
async def get_region(message: Message, state: FSMContext):
    """Get region"""
    region = message.text.strip()
    
    if region == "🖊 Qo'lda kiriting":
        await message.answer(
            "🖊 **Viloyat nomini yozing:**",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        await state.set_state(RegistrationStates.waiting_for_manual_region)
        return
    
    await state.update_data(region=region)
    
    # Get districts for this region
    districts = regions_data.get(region, {}).get("districts", [])
    
    if districts:
        district_buttons = [[KeyboardButton(text=district)] for district in districts]
        district_buttons.append([KeyboardButton(text="🖊 Qo'lda kiriting")])
        
        kb = ReplyKeyboardMarkup(
            keyboard=district_buttons,
            resize_keyboard=True
        )
        
        await message.answer(
            "🏙 **Tuman/Shaharni tanlang:**",
            reply_markup=kb,
            parse_mode="Markdown"
        )
        await state.set_state(RegistrationStates.waiting_for_district)
    else:
        await message.answer(
            "🏙 **Tuman/Shahar nomini yozing:**",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        await state.set_state(RegistrationStates.waiting_for_manual_district)

@dp.message(RegistrationStates.waiting_for_manual_region)
async def get_manual_region(message: Message, state: FSMContext):
    """Get manually entered region"""
    await state.update_data(region=message.text.strip())
    
    await message.answer(
        "🏙 **Tuman/Shahar nomini yozing:**",
        parse_mode="Markdown"
    )
    await state.set_state(RegistrationStates.waiting_for_manual_district)

@dp.message(RegistrationStates.waiting_for_district)
async def get_district(message: Message, state: FSMContext):
    """Get district"""
    district = message.text.strip()
    
    if district == "🖊 Qo'lda kiriting":
        await message.answer(
            "🖊 **Tuman/Shahar nomini yozing:**",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        await state.set_state(RegistrationStates.waiting_for_manual_district)
        return
    
    await state.update_data(district=district)
    
    await message.answer(
        "🏡 **Mahalla nomini yozing:**",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await state.set_state(RegistrationStates.waiting_for_mahalla)

@dp.message(RegistrationStates.waiting_for_manual_district)
async def get_manual_district(message: Message, state: FSMContext):
    """Get manually entered district"""
    await state.update_data(district=message.text.strip())
    
    await message.answer(
        "🏡 **Mahalla nomini yozing:**",
        parse_mode="Markdown"
    )
    await state.set_state(RegistrationStates.waiting_for_mahalla)

@dp.message(RegistrationStates.waiting_for_mahalla)
async def get_mahalla(message: Message, state: FSMContext):
    """Get mahalla and complete registration"""
    data = await state.get_data()
    data['mahalla'] = message.text.strip()
    
    # Save to database
    user_data = {
        "user_id": str(message.from_user.id),
        "child_name": data['child_name'],
        "parent_name": data['parent_name'],
        "phone": "",  # Will be updated when phone is shared
        "age_group": data['age_group'].replace(" yosh", ""),  # Convert to database format
        "region": data['region'],
        "district": data['district'],
        "mahalla": data['mahalla'],
        "telegram_username": message.from_user.username or "",
        "telegram_name": f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
    }
    
    try:
        DatabaseService.create_user(user_data)
        
        success_text = f"""
✅ **Ro'yxatdan o'tish yakunlandi!**

👶 **Bola:** {data['child_name']}
👨‍👩‍👧‍👦 **Ota-ona:** {data['parent_name']}
📚 **Yosh guruhi:** {data['age_group']}
🏢 **Viloyat:** {data['region']}
🏙 **Tuman:** {data['district']}
🏡 **Mahalla:** {data['mahalla']}

🎉 Tabriklaymiz! Endi testlarni topshirishingiz mumkin.
"""
        
        await message.answer(
            success_text,
            reply_markup=create_main_menu(),
            parse_mode="Markdown"
        )
        
        # Notify admins
        username = message.from_user.username or "noma'lum"
        admin_text = f"""
📥 **Yangi foydalanuvchi ro'yxatdan o'tdi!**

👤 **Telegram:** @{username} ({message.from_user.id})
{success_text}
"""
        
        for admin_id in ADMINS:
            try:
                await bot.send_message(admin_id, admin_text, parse_mode="Markdown")
            except:
                pass
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error saving user: {e}")
        await message.answer(
            "❌ Ro'yxatdan o'tishda xatolik yuz berdi. Qaytadan urinib ko'ring.",
            reply_markup=create_main_menu()
        )
        await state.clear()

# Project info handler
@dp.message(F.text == "📚 Loyiha haqida")
async def project_info(message: Message):
    """Project information"""
    info_text = """
📚 **Kitobxon Kids Loyihasi**

🎯 **Maqsad:** O'zbekiston bolalarining kitobxonlik va umumiy bilim darajasini oshirish

👶 **Yosh guruhlari:**
• 7-10 yosh
• 11-14 yosh

📋 **Imkoniyatlar:**
• Ro'yxatdan o'tish
• Bilim darajasini sinash
• Natijalarni ko'rish
• Fikr bildirish

🏆 **Maqsadlar:**
• Bolalarda o'qish sevgisini rivojlantirish
• Bilimlarni baholash va mustahkamlash
• Ta'limiy jarayonni qiziqarli qilish

📞 **Qo'llab-quvvatlash:**
Savollaringiz bo'lsa, admin bilan bog'laning.
"""
    
    await message.answer(info_text, parse_mode="Markdown")

# Test handler
@dp.message(F.text == "📋 Test topshirish")
async def start_test(message: Message):
    """Start test"""
    user_id = str(message.from_user.id)
    
    # Check if user is registered
    user = DatabaseService.get_user(user_id)
    if not user:
        await message.answer(
            "❌ Avval ro'yxatdan o'ting!\n\n📝 Ro'yxatdan o'tish tugmasini bosing.",
            reply_markup=create_main_menu()
        )
        return
    
    # Check if there are questions for user's age group
    questions = DatabaseService.get_questions_by_age_group(user.age_group)
    if not questions:
        await message.answer(
            "❌ Sizning yosh guruhingiz uchun hozircha savollar mavjud emas.\n\nIltimos, keyinroq qaytadan urinib ko'ring.",
            reply_markup=create_main_menu()
        )
        return
    
    await message.answer(
        f"📋 **Test boshlash**\n\n"
        f"📚 Yosh guruhi: {user.age_group} yosh\n"
        f"❓ Savollar soni: {len(questions)}\n"
        f"⏱ Har bir savol uchun 20 soniya vaqt\n\n"
        f"Tayyormisiz?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="▶️ Testni boshlash", callback_data="start_test")],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")]
            ]
        ),
        parse_mode="Markdown"
    )

# Feedback handler
@dp.message(F.text == "💬 Fikr bildirish")
async def feedback_start(message: Message, state: FSMContext):
    """Start feedback process"""
    user_id = str(message.from_user.id)
    
    # Check if user is registered
    user = DatabaseService.get_user(user_id)
    if not user:
        await message.answer(
            "❌ Avval ro'yxatdan o'ting!\n\n📝 Ro'yxatdan o'tish tugmasini bosing.",
            reply_markup=create_main_menu()
        )
        return
    
    await message.answer(
        "💬 **Fikr bildirish**\n\n"
        "Loyiha haqida fikr va takliflaringizni yozing.\n"
        "Barcha xabarlar adminlarga yuboriladi:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await state.set_state(FeedbackStates.waiting_for_feedback)

@dp.message(FeedbackStates.waiting_for_feedback)
async def process_feedback(message: Message, state: FSMContext):
    """Process feedback"""
    user_id = str(message.from_user.id)
    feedback_text = message.text.strip()
    
    # Get user data
    user = DatabaseService.get_user(user_id)
    
    # Save feedback to database
    feedback_data = {
        "user_id": user_id,
        "feedback_text": feedback_text,
        "phone": user.phone if user else "",
        "telegram_username": message.from_user.username or ""
    }
    
    try:
        DatabaseService.save_feedback(feedback_data)
        
        await message.answer(
            "✅ **Fikr-mulohaza yuborildi!**\n\n"
            "Rahmat! Sizning fikringiz adminlarga yetkazildi.",
            reply_markup=create_main_menu(),
            parse_mode="Markdown"
        )
        
        # Send to admins
        child_name = user.child_name if user else "Noma'lum"
        username = message.from_user.username or "noma'lum"
        phone = user.phone if user else "noma'lum"
        
        admin_text = f"""
💬 **Yangi fikr-mulohaza:**

👤 **Foydalanuvchi:** {child_name} ({message.from_user.id})
📱 **Username:** @{username}
📞 **Telefon:** {phone}

💭 **Xabar:**
{feedback_text}

📅 **Sana:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
        
        for admin_id in ADMINS:
            try:
                await bot.send_message(admin_id, admin_text, parse_mode="Markdown")
            except:
                pass
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
        await message.answer(
            "❌ Fikr yuborishda xatolik yuz berdi. Qaytadan urinib ko'ring.",
            reply_markup=create_main_menu()
        )
        await state.clear()

# Admin handlers
@dp.message(F.text == "📤 Ma'lumotlarni eksport qilish")
async def export_data(message: Message):
    """Export data menu"""
    if message.from_user.id not in ADMINS:
        return
    
    await message.answer(
        "📤 **Ma'lumotlarni eksport qilish**\n\n"
        "Formatni tanlang:",
        reply_markup=create_export_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "export_excel")
async def export_excel_callback(callback: CallbackQuery):
    """Export to Excel"""
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.answer("📊 Excel fayl tayyorlanmoqda...")
    await callback.message.edit_text("⏳ **Excel fayl yaratilmoqda...**", parse_mode="Markdown")
    
    excel_file = await export_to_excel()
    
    if excel_file:
        await callback.message.answer_document(
            excel_file,
            caption="📊 **Foydalanuvchilar ma'lumotlari Excel formatida**",
            parse_mode="Markdown"
        )
        await callback.message.edit_text("✅ **Excel fayl muvaffaqiyatli yaratildi!**", parse_mode="Markdown")
    else:
        await callback.message.edit_text("❌ **Excel fayl yaratishda xatolik yuz berdi!**", parse_mode="Markdown")

@dp.callback_query(F.data == "export_pdf")
async def export_pdf_callback(callback: CallbackQuery):
    """Export to PDF"""
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.answer("📄 PDF fayl tayyorlanmoqda...")
    await callback.message.edit_text("⏳ **PDF fayl yaratilmoqda...**", parse_mode="Markdown")
    
    pdf_file = await export_to_pdf()
    
    if pdf_file:
        await callback.message.answer_document(
            pdf_file,
            caption="📄 **Foydalanuvchilar ma'lumotlari PDF formatida**",
            parse_mode="Markdown"
        )
        await callback.message.edit_text("✅ **PDF fayl muvaffaqiyatli yaratildi!**", parse_mode="Markdown")
    else:
        await callback.message.edit_text("❌ **PDF fayl yaratishda xatolik yuz berdi!**", parse_mode="Markdown")

@dp.message(F.text == "❓ Savollarni boshqarish")
async def questions_management(message: Message):
    """Questions management"""
    if message.from_user.id not in ADMINS:
        return
    
    await message.answer(
        "❓ **Savollarni boshqarish**\n\n"
        "Kerakli amalni tanlang:",
        reply_markup=create_question_management_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "add_question")
async def add_single_question(callback: CallbackQuery, state: FSMContext):
    """Add single question"""
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "➕ **Yangi savol qo'shish**\n\n"
        "Avval yosh guruhini tanlang:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="7-10 yosh", callback_data="single_age_7-10")],
                [InlineKeyboardButton(text="11-14 yosh", callback_data="single_age_11-14")],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_questions")]
            ]
        ),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("single_age_"))
async def single_age_selection(callback: CallbackQuery, state: FSMContext):
    """Select age group for single question"""
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    age_group = callback.data.split("_", 2)[2]
    await state.update_data(question_age_group=age_group)
    
    await callback.message.edit_text(
        f"📝 **{age_group} yosh guruhi uchun savol**\n\n"
        "Savol matnini kiriting:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="back_to_questions")]]
        ),
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.waiting_for_new_question)
    await callback.answer()

@dp.message(AdminStates.waiting_for_new_question)
async def get_question_text(message: Message, state: FSMContext):
    """Get question text"""
    if message.from_user.id not in ADMINS:
        return
    
    await state.update_data(question_text=message.text.strip())
    
    await message.answer(
        "📝 **Javob variantlarini kiriting**\n\n"
        "To'rtta variant kiriting (har birini alohida xabarda):\n"
        "Birinchi variantni yuboring:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AdminStates.waiting_for_new_options)
    await state.update_data(options=[], option_count=0)

@dp.message(AdminStates.waiting_for_new_options)
async def get_question_options(message: Message, state: FSMContext):
    """Get question options"""
    if message.from_user.id not in ADMINS:
        return
    
    data = await state.get_data()
    options = data.get('options', [])
    option_count = data.get('option_count', 0)
    
    options.append(message.text.strip())
    option_count += 1
    
    await state.update_data(options=options, option_count=option_count)
    
    if option_count < 4:
        await message.answer(f"✅ Variant {option_count} saqlandi.\n\n{option_count + 1}-variantni kiriting:")
    else:
        # Show options and ask for correct answer
        options_text = "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)])
        
        await message.answer(
            f"✅ **Barcha variantlar saqlandi!**\n\n"
            f"**Savol:** {data['question_text']}\n\n"
            f"**Variantlar:**\n{options_text}\n\n"
            f"To'g'ri javob harfini kiriting (A, B, C, D):",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="A"), KeyboardButton(text="B")],
                    [KeyboardButton(text="C"), KeyboardButton(text="D")]
                ],
                resize_keyboard=True
            )
        )
        await state.set_state(AdminStates.waiting_for_correct_answer)

@dp.message(AdminStates.waiting_for_correct_answer)
async def get_correct_answer(message: Message, state: FSMContext):
    """Get correct answer and save question"""
    if message.from_user.id not in ADMINS:
        return
    
    answer = message.text.strip().upper()
    
    if answer not in ['A', 'B', 'C', 'D']:
        await message.answer("❌ Faqat A, B, C yoki D harflaridan birini kiriting!")
        return
    
    data = await state.get_data()
    correct_answer = ord(answer) - ord('A')
    
    # Save question to database
    question_data = {
        "question_text": data['question_text'],
        "options": data['options'],
        "correct_answer": correct_answer,
        "age_group": data['question_age_group']
    }
    
    try:
        success = DatabaseService.add_question(
            question_data['question_text'],
            question_data['options'],
            question_data['correct_answer'],
            question_data['age_group']
        )
        
        if success:
            await message.answer(
                "✅ **Savol muvaffaqiyatli qo'shildi!**\n\n"
                f"📚 Yosh guruhi: {data['question_age_group']}\n"
                f"❓ Savol: {data['question_text']}\n"
                f"✅ To'g'ri javob: {answer}",
                reply_markup=create_admin_menu(),
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                "❌ **Savolni saqlashda xatolik yuz berdi!**",
                reply_markup=create_admin_menu()
            )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error saving question: {e}")
        await message.answer(
            "❌ **Savolni saqlashda xatolik yuz berdi!**",
            reply_markup=create_admin_menu()
        )
        await state.clear()

@dp.callback_query(F.data == "view_questions")
async def view_questions(callback: CallbackQuery):
    """View questions"""
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    try:
        questions_7_10 = DatabaseService.get_questions_by_age_group("7-10")
        questions_11_14 = DatabaseService.get_questions_by_age_group("11-14")
        
        stats_text = f"📊 **Savollar statistikasi:**\n\n"
        stats_text += f"👶 7-10 yosh: {len(questions_7_10)} ta savol\n"
        stats_text += f"🧒 11-14 yosh: {len(questions_11_14)} ta savol\n"
        stats_text += f"📝 Jami: {len(questions_7_10) + len(questions_11_14)} ta savol"
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="👶 7-10 yosh savollar", callback_data="show_7-10")],
                    [InlineKeyboardButton(text="🧒 11-14 yosh savollar", callback_data="show_11-14")],
                    [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_questions")]
                ]
            ),
            parse_mode="Markdown"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error viewing questions: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)

@dp.callback_query(F.data.startswith("show_"))
async def show_age_group_questions(callback: CallbackQuery):
    """Show questions for specific age group"""
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    age_group = callback.data.split("_")[1]
    
    try:
        questions = DatabaseService.get_questions_by_age_group(age_group)
        
        if not questions:
            await callback.message.edit_text(
                f"📝 **{age_group} yosh guruhi:**\n\n❌ Hozircha savollar yo'q",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="🔙 Orqaga", callback_data="view_questions")]]
                ),
                parse_mode="Markdown"
            )
        else:
            # Show first few questions
            text = f"📝 **{age_group} yosh guruhi ({len(questions)} ta savol):**\n\n"
            
            for i, q in enumerate(questions[:3], 1):  # Show only first 3
                text += f"{i}. {q.question_text}\n"
                for j, option in enumerate(q.options):
                    marker = "✅" if j == q.correct_answer else "◦"
                    text += f"   {marker} {chr(65+j)}) {option}\n"
                text += "\n"
            
            if len(questions) > 3:
                text += f"... va yana {len(questions) - 3} ta savol"
            
            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="🗑 Hammasi o'chirish", callback_data=f"clear_all_{age_group}")],
                        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="view_questions")]
                    ]
                ),
                parse_mode="Markdown"
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error showing questions: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)

@dp.callback_query(F.data.startswith("clear_all_"))
async def clear_all_questions(callback: CallbackQuery):
    """Clear all questions for age group"""
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    age_group = callback.data.split("_", 2)[2]
    
    await callback.message.edit_text(
        f"⚠️ **Diqqat!**\n\n"
        f"Haqiqatan ham {age_group} yosh guruhi uchun barcha savollarni o'chirmoqchimisiz?\n\n"
        f"Bu amalni bekor qilib bo'lmaydi!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Ha, o'chir", callback_data=f"confirm_clear_{age_group}")],
                [InlineKeyboardButton(text="❌ Yo'q, bekor qil", callback_data=f"show_{age_group}")]
            ]
        ),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("confirm_clear_"))
async def confirm_clear_questions(callback: CallbackQuery):
    """Confirm clearing questions"""
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    age_group = callback.data.split("_", 2)[2]
    
    try:
        deleted_count = DatabaseService.clear_questions_by_age_group(age_group)
        
        await callback.message.edit_text(
            f"✅ **Muvaffaqiyatli o'chirildi!**\n\n"
            f"📚 Yosh guruhi: {age_group}\n"
            f"🗑 O'chirilgan savollar: {deleted_count} ta",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="🔙 Savollar menu", callback_data="back_to_questions")]]
            ),
            parse_mode="Markdown"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error clearing questions: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)

# Navigation callbacks
@dp.callback_query(F.data == "back_to_questions")
async def back_to_questions(callback: CallbackQuery):
    """Back to questions menu"""
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "❓ **Savollarni boshqarish**\n\nKerakli amalni tanlang:",
        reply_markup=create_question_management_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    """Back to admin panel"""
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.message.delete()
    await callback.message.answer(
        "🔧 **Admin Panel**\n\nBoshqaruv paneliga xush kelibsiz!",
        reply_markup=create_admin_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(F.text == "📢 Xabar yuborish")
async def broadcast_message(message: Message, state: FSMContext):
    """Broadcast message"""
    if message.from_user.id not in ADMINS:
        return
    
    await message.answer(
        "📢 **Barcha foydalanuvchilarga xabar yuborish**\n\n"
        "Yubormoqchi bo'lgan xabaringizni kiriting:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.waiting_for_broadcast)

@dp.message(AdminStates.waiting_for_broadcast)
async def send_broadcast(message: Message, state: FSMContext):
    """Send broadcast message"""
    if message.from_user.id not in ADMINS:
        return
    
    broadcast_text = message.text.strip()
    
    try:
        users = DatabaseService.get_all_users()
        sent_count = 0
        failed_count = 0
        
        await message.answer("⏳ **Xabar yuborilmoqda...**", parse_mode="Markdown")
        
        for user in users:
            try:
                await bot.send_message(user.user_id, broadcast_text)
                sent_count += 1
            except:
                failed_count += 1
        
        result_text = f"""
✅ **Xabar yuborish yakunlandi!**

📤 Yuborildi: {sent_count} ta
❌ Xatolik: {failed_count} ta
📊 Jami: {len(users)} ta foydalanuvchi
"""
        
        await message.answer(
            result_text,
            reply_markup=create_admin_menu(),
            parse_mode="Markdown"
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        await message.answer(
            "❌ Xabar yuborishda xatolik yuz berdi!",
            reply_markup=create_admin_menu()
        )
        await state.clear()

@dp.message(F.text == "🔙 Oddiy foydalanuvchi rejimiga qaytish")
async def back_to_user_mode(message: Message):
    """Back to user mode"""
    if message.from_user.id not in ADMINS:
        return
    
    await message.answer(
        "👤 **Oddiy foydalanuvchi rejimiga qaytdingiz**\n\n"
        "Admin panelga qaytish uchun: /admin",
        reply_markup=create_main_menu(),
        parse_mode="Markdown"
    )

@dp.message(F.text == "👥 Foydalanuvchilar ro'yxati")
async def users_list(message: Message):
    """Show users list"""
    if message.from_user.id not in ADMINS:
        return
    
    try:
        users = DatabaseService.get_all_users()
        
        if not users:
            await message.answer("📋 Hech qanday foydalanuvchi ro'yxatdan o'tmagan.")
            return
        
        # Show summary
        text = f"👥 **Foydalanuvchilar ro'yxati**\n\n📊 **Jami:** {len(users)} ta\n\n"
        
        # Regional breakdown
        region_stats = {}
        for user in users:
            region = user.region
            region_stats[region] = region_stats.get(region, 0) + 1
        
        text += "🗺️ **Viloyatlar bo'yicha:**\n"
        for region, count in sorted(region_stats.items()):
            text += f"▪️ {region}: {count} ta\n"
        
        text += f"\n📤 **To'liq ma'lumotlar uchun eksport funksiyasidan foydalaning.**"
        
        await message.answer(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error getting users list: {e}")
        await message.answer("❌ Foydalanuvchilar ro'yxatini olishda xatolik yuz berdi!")

@dp.message(F.text == "📊 Statistika")
async def statistics(message: Message):
    """Show statistics"""
    if message.from_user.id not in ADMINS:
        return
    
    try:
        users = DatabaseService.get_all_users()
        
        # Basic stats
        total_users = len(users)
        users_7_10 = len([u for u in users if u.age_group == "7-10"])
        users_11_14 = len([u for u in users if u.age_group == "11-14"])
        
        # Questions stats
        questions_7_10 = DatabaseService.get_questions_by_age_group("7-10")
        questions_11_14 = DatabaseService.get_questions_by_age_group("11-14")
        
        stats_text = f"""
📊 **KITOBXON KIDS STATISTIKASI**

👥 **Foydalanuvchilar:**
▪️ Jami: {total_users} ta
▪️ 7-10 yosh: {users_7_10} ta
▪️ 11-14 yosh: {users_11_14} ta

❓ **Savollar:**
▪️ 7-10 yosh: {len(questions_7_10)} ta
▪️ 11-14 yosh: {len(questions_11_14)} ta
▪️ Jami: {len(questions_7_10) + len(questions_11_14)} ta

📅 **Sana:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
        
        await message.answer(stats_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        await message.answer("❌ Statistikani olishda xatolik yuz berdi!")

# Main function
async def main():
    """Start bot"""
    logger.info("Bot starting...")
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return
    
    # Clear all existing questions as requested by user
    try:
        count_7_10 = DatabaseService.clear_questions_by_age_group("7-10")
        count_11_14 = DatabaseService.clear_questions_by_age_group("11-14")
        logger.info(f"Cleared {count_7_10} questions from age group 7-10")
        logger.info(f"Cleared {count_11_14} questions from age group 11-14")
        logger.info("All existing tests removed as requested")
    except Exception as e:
        logger.warning(f"Could not clear questions: {e}")
    
    logger.info("Bot started successfully!")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
