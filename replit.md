# Overview

This is an optimized Telegram bot built for the "Kitobxon_Kids" educational project, designed to provide testing and assessment services for children aged 7-14. The bot implements a comprehensive educational platform with user registration, age-appropriate testing, certificate generation, and administrative management features. It serves as a digital testing platform for the Uzbek-speaking community with full regional support for all Uzbekistan provinces and districts.

**Latest Update (August 11, 2025):** The bot has been fully optimized for 10,000+ concurrent users with enhanced performance, complete geographic data coverage, fixed admin features, and restricted super-admin management to two specific Telegram IDs (6578706277, 7853664401).

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework and Core Architecture
- **Framework**: aiogram (Python Telegram Bot API wrapper) with async/await pattern for high-performance message handling
- **Architecture Pattern**: Event-driven monolithic design with FSM (Finite State Machine) for complex conversation flows
- **Deployment Strategy**: Single-file architecture (`main.py`) for simplified deployment and maintenance
- **Rationale**: Chosen for rapid development, easy deployment, and reduced infrastructure complexity while maintaining robust async capabilities

## Data Storage and Persistence Layer
- **Storage Solution**: JSON file-based persistence system organized in structured data files with performance optimizations
- **Data Architecture**:
  - `users.json` - User profiles with regional demographics and contact information including phone numbers
  - `admins.json` - Role-based access control and admin hierarchy management
  - `tests.json` - Age-segmented test questions (7-10 and 11-14 age groups)
  - `results.json` - Test completion records with detailed answer tracking
  - `statistics.json` - Real-time analytics and regional usage metrics
  - `broadcasts.json` - Message broadcasting history and delivery tracking
- **Design Decision**: File-based storage chosen over database for lightweight deployment, zero-configuration setup, and simplified backup/migration processes
- **Performance Optimizations**:
  - Async file operations with aiofiles for non-blocking I/O
  - In-memory caching with TTL (Time-To-Live) for frequently accessed data
  - Semaphore-controlled concurrent file operations (max 100 simultaneous)
  - LRU cache for regional data to reduce memory footprint
- **Trade-offs**: Optimized for 10,000+ concurrent users while maintaining data consistency

## State Management System
- **Implementation**: FSM using aiogram's native state management with StatesGroup classes
- **State Categories**: User registration flows, multi-step test sessions, admin operations, and certificate generation workflows
- **Context Preservation**: Maintains user conversation context across multiple message exchanges for complex interactions

## User Interface and Interaction Design
- **Navigation Architecture**: Hierarchical menu system using ReplyKeyboardMarkup for primary navigation
- **Interactive Components**: InlineKeyboardMarkup for test answers, admin controls, and contextual actions
- **Localization**: Complete Uzbek language interface with comprehensive regional data covering ALL Uzbekistan administrative divisions
- **Geographic Coverage**: Complete implementation of all 14 regions (Toshkent shahri, Toshkent viloyati, Andijon, Farg'ona, Namangan, Samarqand, Buxoro, Jizzax, Navoiy, Qashqadaryo, Surxondaryo, Sirdaryo, Xorazm, Qoraqalpog'iston) with all districts and mahallas
- **Manual Entry Option**: "Qo'lda kiritish" (Manual Entry) field below mahalla selection for unlisted locations
- **User Experience**: Progressive disclosure pattern with role-aware menu systems and context-sensitive interfaces

## Role-Based Access Control System
- **Permission Hierarchy**:
  - **Super Admins**: Complete system administration including user management, test creation, and system configuration
  - **Special Privilege Admins**: Hardcoded elevated permissions for specific user IDs (6578706277, 7853664401) - ONLY these IDs can manage super-admin assignments
  - **Regular Admins**: Limited administrative access for basic management tasks
  - **Regular Users**: Test participation, profile management, and certificate access
- **Security Model**: Role validation on all sensitive operations with comprehensive audit logging and permission checks
- **Super-Admin Restrictions**: Only users with IDs 6578706277 and 7853664401 can promote/demote super-admins, ensuring system security

## Testing and Assessment Engine
- **Age-Based Segmentation**: Separate test categories optimized for 7-10 and 11-14 year age groups
- **Question Format**: Multiple-choice assessment system (A, B, C, D options) with automated scoring
- **Test Management**: UUID-based test identification system with book association and progress tracking
- **Assessment Logic**: Automatic scoring with configurable passing thresholds and detailed result analytics

## Reporting and Analytics System
- **Admin Reporting**: Excel and PDF export capabilities for comprehensive data analysis
- **Statistics Engine**: Real-time regional usage tracking with demographic breakdowns
- **Certificate Generation**: Automated certificate creation and delivery system
- **Performance Monitoring**: System usage analytics and user engagement metrics

# External Dependencies

## Telegram Bot API Integration
- **Primary API**: Telegram Bot API through aiogram framework for all bot interactions
- **Channel Integration**: @Kitobxon_Kids channel for community engagement and announcements
- **Authentication**: Bot token-based authentication with environment variable configuration

## Document Generation Libraries
- **Excel Exports**: openpyxl library for administrative data exports and reporting
- **PDF Generation**: reportlab library for certificate creation and formatted reports
- **File Handling**: aiofiles for asynchronous file operations and temporary file management

## Runtime Environment
- **Python Runtime**: Async Python environment with support for concurrent operations
- **File System**: Local file system for JSON data persistence and temporary file storage
- **Timezone Handling**: Uzbekistan timezone (UTC+5) support for localized timestamps and scheduling

## Optional Integrations
- **Environment Configuration**: Support for environment variables for secure token and admin ID management
- **Logging Infrastructure**: Python logging framework for system monitoring and debugging
- **Concurrency Control**: Semaphore-based rate limiting for broadcast operations and resource management
