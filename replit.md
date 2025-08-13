# Overview

This is a comprehensive Telegram educational testing bot called "Kitobxon Kids" designed to conduct reading comprehension tests for children aged 7-14 in Uzbekistan. The bot has been completely refactored (v2.0) to support unlimited registrations, multi-format document processing, simplified admin system (Super Admin only), comprehensive access control, and optimization for 4,000+ concurrent users. It features advanced document export capabilities in PDF, Word, Excel, and Text formats.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework and Core Design
- **Framework**: aiogram (Python Telegram Bot API wrapper) with async/await architecture
- **Design Pattern**: Event-driven monolithic architecture using Finite State Machine (FSM) for conversation flows
- **File Structure**: Single main.py file approach for simplified deployment and maintenance
- **State Management**: aiogram's StatesGroup classes handle multi-step user interactions with context preservation

## Data Storage and Persistence
- **Storage System**: JSON file-based persistence in `bot_data/` directory structure
- **Data Organization**:
  - `users.json` - Complete user profiles including child/parent information and regional data
  - `admins.json` - Administrative roles and permissions with audit tracking
  - `tests.json` - Question banks categorized by age groups (7-10 and 11-14 years)
  - `results.json` - Test completion records with detailed scoring and performance metrics
  - `statistics.json` - System analytics including regional performance and usage statistics
  - `broadcasts.json` - Message broadcasting history and delivery tracking
  - `bot_users.json` - Comprehensive tracking of all bot interactions for broadcasting
  - `access_control.json` - System-wide access permissions and feature toggles

## User Management and Authentication
- **Registration System**: Multi-step registration process collecting child and parent information
- **Regional Validation**: Comprehensive validation against Uzbekistan's administrative divisions
- **Role-Based Access**: Two-tier admin system (Super Admin and Regular Admin) with permission inheritance
- **User Tracking**: Dual tracking system for registered users and general bot interactions

## Test Management System
- **Age Categorization**: Automatic test assignment based on child's age (7-10 and 11-14 groups)
- **Dynamic Question Banks**: JSON-based storage allowing flexible test content management
- **Scoring System**: Comprehensive performance tracking with percentage-based grading
- **Results Analytics**: Detailed performance metrics with regional and age-group breakdowns

## Administrative Features
- **Broadcasting System**: Targeted messaging to all bot users with delivery tracking
- **Document Generation**: Excel and PDF export capabilities for user data and test results
- **Statistics Dashboard**: Real-time analytics with regional performance insights
- **Access Control**: Granular control over test availability and user permissions

# External Dependencies

## Core Bot Infrastructure
- **aiogram**: Modern async Telegram Bot API framework for Python
- **Python Standard Library**: JSON handling, datetime operations, logging, and file I/O

## Optional Document Generation
- **openpyxl**: Excel file generation with professional formatting and conditional styling
- **reportlab**: PDF document generation for reports and certificates
- **Pillow (PIL)**: Image processing support for enhanced document generation

## Data Validation
- **Built-in Regional Database**: Comprehensive validation against Uzbekistan's administrative structure including regions, districts, and mahallas

## Deployment Environment
- **File System**: Local JSON storage requiring read/write permissions
- **Telegram Bot API**: External API dependency for bot functionality
- **Python Runtime**: Requires Python 3.8+ with async/await support
