# Overview

The Kitobxon Kids Telegram Bot is an educational platform designed for Uzbek children aged 7-14 years. The bot facilitates comprehensive user registration with detailed geographic location data (region, district, mahalla) and provides an interactive testing system with question management capabilities. The system supports administrative functions including user data export in multiple formats (Excel, PDF), bulk question management, and real-time user statistics monitoring.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework Architecture
The application is built using the aiogram framework for Telegram bot development, implementing a state machine pattern with FSM (Finite State Machine) for managing complex user registration flows and test interactions. The bot uses memory storage for session management and supports concurrent user handling.

## Database Architecture
The system uses PostgreSQL as the primary database with SQLAlchemy ORM for data persistence. The database schema includes:
- **User Management**: Stores complete user profiles with registration data, contact information, and geographic location
- **Question System**: Manages test questions with support for multiple age groups (7-10 and 11-14 years)
- **Test Results**: Tracks user performance and test completion data
- **Regional Data**: Maintains hierarchical location data (regions → districts → mahallas)

The architecture implements a DatabaseService layer that provides CRUD operations and session management, ensuring data consistency and proper transaction handling.

## File Processing System
The application supports multiple document formats for question import:
- **Text files (.txt)**: UTF-8 encoded plain text parsing
- **Word documents (.docx)**: Document parsing using python-docx library
- **Excel spreadsheets (.xlsx)**: Data extraction using openpyxl library

Question parsing uses regex pattern matching to extract structured data in the format: "Question? A) Option B) Option C) Option D) Option Answer: X"

## Export and Reporting System
The system provides comprehensive data export capabilities:
- **Excel Export**: Professional formatting with styled worksheets using openpyxl
- **PDF Generation**: Structured reports using ReportLab with custom fonts and professional layout
- **Real-time Statistics**: Dynamic user analytics and regional demographic breakdowns

## Admin Panel Architecture
Administrative functions are implemented with role-based access control, supporting:
- Question management (single and bulk operations)
- User data monitoring and export
- Broadcast messaging system
- File upload and processing capabilities

## State Management
The bot implements a comprehensive state machine for managing user interactions:
- Registration flow states for collecting user information
- Test administration states for question delivery
- Admin panel states for administrative operations
- Error handling and recovery mechanisms

# External Dependencies

## Core Framework Dependencies
- **aiogram**: Telegram Bot API framework for Python providing async message handling and webhook support
- **SQLAlchemy**: ORM framework for database operations with PostgreSQL dialect support
- **PostgreSQL**: Primary database system for data persistence and relational data management

## Document Processing Libraries
- **openpyxl**: Excel file creation and manipulation for data export functionality
- **python-docx**: Word document parsing for question import from .docx files
- **ReportLab**: PDF generation library for creating formatted reports and data exports

## Data Processing Dependencies
- **json**: Built-in library for JSON data handling and configuration management
- **re**: Regular expressions for pattern matching in question parsing
- **datetime**: Time and date handling for registration timestamps and scheduling

## Optional Enhancement Libraries
- **uuid**: Unique identifier generation for database records
- **logging**: Application logging and error tracking
- **asyncio**: Asynchronous programming support for concurrent user handling

## Environment Configuration
The application relies on environment variables for:
- **BOT_TOKEN**: Telegram Bot API authentication token
- **DATABASE_URL**: PostgreSQL connection string
- **ADMIN_IDS**: Comma-separated list of administrator user IDs