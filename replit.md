# Overview

This is a comprehensive Telegram bot application built using the aiogram framework for the "Kitobxon_Kids" project. The bot features a complete admin panel system with role-based access control (Super Admin and Regular Admin), an interactive test system with age-based categorization, user registration with regional data collection, and advanced document generation capabilities. The bot implements a finite state machine for handling complex user interactions and includes comprehensive administrative features for user and test management. All functionality is contained within a single Python file for ease of deployment and maintenance.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Framework**: aiogram (Python Telegram Bot API wrapper)
- **Architecture Pattern**: Event-driven with FSM (Finite State Machine) for state management
- **Rationale**: aiogram provides robust async support and clean state management for complex bot interactions

## Data Storage
- **Primary Storage**: JSON file-based storage in `bot_data/` directory
- **Structure**: Flat file system with `users.json` for user data persistence
- **Rationale**: Simple file-based storage chosen for lightweight deployment and minimal infrastructure requirements
- **Trade-offs**: Limited scalability but sufficient for small to medium user bases

## State Management
- **Pattern**: FSM using aiogram's built-in state management
- **Implementation**: StatesGroup classes for different conversation flows
- **Purpose**: Handles multi-step user interactions like registration processes

## User Interface
- **Keyboard Types**: 
  - ReplyKeyboardMarkup for main navigation
  - InlineKeyboardMarkup for interactive buttons
- **Menu Structure**: Hierarchical menu system with regional data organization
- **Localization**: Uzbek language interface with regional/district data for Uzbekistan

## Administrative Features
- **Role-Based Access Control**: 
  - Super Admin: Full access (add/remove/promote admins, add/delete tests, download separate reports for test results and user data, view detailed admin list with names and usernames)
  - Regular Admin: Limited access (add tests, view users, receive notifications)
- **Admin Management**: Super Admin can add, remove, and promote regular admins to Super Admin status with full name and username display in admin lists
- **User Management**: Complete user registration data viewing and management with Telegram ID and username tracking
- **Test Management**: Add tests in text or PDF format, organize by age groups (7-10, 11-14)
- **Reporting**: Enhanced PDF (landscape format) and Excel (auto-sized columns, text wrapping) report generation with no data truncation
- **Real-time Notifications**: All admins receive instant notifications for registrations, feedback, test completions, and admin role changes

## Document Generation
- **PDF Generation**: ReportLab library for creating formatted reports
- **Excel Export**: openpyxl for spreadsheet generation
- **File Handling**: Temporary file creation for document downloads

# External Dependencies

## Core Libraries
- **aiogram**: Telegram Bot API framework for Python
- **asyncio**: Asynchronous programming support

## Document Processing
- **reportlab**: PDF generation and formatting
- **openpyxl**: Excel file creation and manipulation
- **PyPDF2**: PDF file reading capabilities

## Telegram Integration
- **Bot Token**: Hardcoded token for Telegram Bot API access
- **Channel Integration**: Subscription verification for "@Kitobxon_Kids" channel
- **File Uploads**: Support for sending generated documents through Telegram

## Environment Configuration
- **Environment Variables**: Bot token and admin ID configuration
- **File System**: Local file storage for user data and temporary documents

## Test System Features
- **Age-Based Categories**: Tests divided into 7-10 and 11-14 age groups
- **Interactive Testing**: 25 random questions per test session with 4 points each (max 100 points)
- **Time Management**: 1-minute timer per question with automatic progression
- **Question Sources**: Tests sourced from 5 different books with comprehensive question pools
- **Real-time Results**: Immediate feedback with detailed scoring and time tracking
- **Admin Notifications**: Test completion results sent to all admins with user details

## Data Structure
- **Regional Data**: Comprehensive Uzbekistan administrative divisions (provinces and districts)
- **User Data**: JSON-based storage with full registration details, Telegram ID, and username
- **Test Data**: Organized by age groups with question pools, correct answers, and metadata
- **Results Data**: Complete test history with scores, timing, user identification, and answers
- **Admin Data**: Role-based admin management with hierarchy and permissions