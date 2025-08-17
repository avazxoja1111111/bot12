# Overview

Kitobxon Kids is a high-performance educational Telegram bot designed for conducting reading comprehension tests for children aged 7-14 in the Republic of Uzbekistan. The bot is built to handle 10,000+ concurrent users while providing comprehensive test management, user registration with complete regional data, administrative controls, and multi-format document processing capabilities. It serves as an educational initiative supporting literacy assessment across all regions of Uzbekistan.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Bot Framework
- **Framework**: aiogram v3 with async/await architecture for high-performance concurrent operations
- **Design Pattern**: Event-driven architecture using Finite State Machine (FSM) for complex conversation flows
- **Performance Optimization**: Built-in connection pooling, request timeout management, and memory optimization for 10,000+ concurrent users
- **Error Handling**: Comprehensive error recovery system with statistics tracking and automatic retry mechanisms

## Data Storage and Management
- **Storage System**: JSON file-based persistence with structured data organization in `bot_data/` directory
- **Data Structure**:
  - User profiles with complete regional validation against Uzbekistan administrative divisions
  - Role-based admin system with audit tracking
  - Age-categorized test banks (7-10 and 11-14 years)
  - Comprehensive test results and performance analytics
  - Broadcasting system with delivery tracking
  - Access control and system statistics
- **Regional Data**: Complete integration of Uzbekistan's administrative structure (regions, districts, mahallas)

## User Management System
- **Registration Process**: Multi-step registration collecting child and parent information with regional validation
- **Authentication**: Role-based access control with Super Admin and Regular Admin tiers
- **User Tracking**: Dual tracking system for registered users and general bot interactions
- **Regional Validation**: Real-time validation against comprehensive Uzbekistan administrative database

## Test Management and Execution
- **Age-Based Categorization**: Automatic test assignment based on child's age groups
- **Multi-Format Import**: Support for Word (.doc/.docx), Excel (.xls/.xlsx), PDF, and plain text test imports
- **Scoring System**: Comprehensive performance tracking with detailed analytics
- **Security**: Anti-AI interference measures to ensure test authenticity

## Performance and Monitoring
- **Scalability**: Optimized for 10,000+ concurrent users with connection pooling and memory management
- **Monitoring**: Real-time performance tracking with CPU, memory, and response time metrics
- **Health Checks**: Automated system health monitoring with alert thresholds
- **Error Recovery**: Comprehensive error handling with automatic retry and graceful degradation

## Document Processing
- **Multi-Format Support**: Word, Excel, PDF, and text document processing with graceful fallbacks
- **Export Capabilities**: Excel and PDF generation for user data and test results
- **Large Dataset Handling**: Optimized export functionality for handling extensive data without truncation

# External Dependencies

## Core Framework
- **aiogram**: Modern async Telegram Bot API framework for Python with built-in performance optimizations
- **aiohttp**: HTTP client for Telegram API communication with connection pooling

## Document Processing (Optional)
- **openpyxl**: Excel file processing and generation with styling capabilities
- **python-docx**: Word document processing for test imports
- **reportlab**: PDF generation with custom styling and layouts
- **PyPDF2/pdfplumber**: PDF text extraction for test content parsing

## System Monitoring
- **psutil**: System resource monitoring for performance tracking
- **weakref**: Memory optimization for handling large user bases

## Environment Configuration
- **BOT_TOKEN**: Telegram Bot API token (required)
- **SUPER_ADMIN_ID**: Initial super administrator user ID
- **System Limits**: Configurable performance thresholds and connection limits

## Regional Data Integration
- **Uzbekistan Administrative Data**: Complete regional hierarchy validation system
- **Multi-language Support**: Uzbek language text processing and validation