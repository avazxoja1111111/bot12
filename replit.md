# Overview

This is an optimized single-file Telegram educational testing bot for the "Kitobxon_Kids" project. The bot implements a clean, streamlined testing system designed for children aged 7-14, featuring user registration, test administration, and basic admin functionality. The code has been optimized and shortened from the original implementation while maintaining all core functionality. All additional export features and certificate generation have been removed as requested.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework and Architecture
- **Framework**: aiogram (Python Telegram Bot API wrapper) with async/await pattern
- **Architecture Pattern**: Event-driven with FSM (Finite State Machine) for complex conversation flows
- **Deployment**: Single-file monolithic architecture contained in main.py for simplified deployment
- **Rationale**: aiogram provides robust async support and clean state management, while the monolithic approach reduces complexity and deployment overhead

## Data Storage and Persistence
- **Primary Storage**: JSON file-based storage system in `bot_data/` directory
- **Data Structure**: 
  - `users.json` - User registration and profile data
  - `admins.json` - Admin roles and permissions
  - `tests.json` - Test questions organized by age groups (7-10, 11-14)
  - `results.json` - Test completion records with detailed answers
  - `certificates.json` - Certificate generation tracking
  - `broadcasts.json` - Message broadcasting history
  - `statistics.json` - System analytics and performance metrics
- **Rationale**: File-based storage chosen for lightweight deployment, minimal infrastructure requirements, and easy backup/migration
- **Trade-offs**: Limited concurrent access but sufficient for educational bot usage patterns

## State Management System
- **Implementation**: FSM using aiogram's built-in state management with StatesGroup classes
- **State Groups**: Registration flows, test-taking sessions, admin operations, and certificate generation
- **Purpose**: Handles multi-step user interactions requiring context preservation across messages

## User Interface Design
- **Navigation**: Hierarchical menu system with ReplyKeyboardMarkup for main navigation
- **Interactive Elements**: InlineKeyboardMarkup for test answers, admin controls, and quick actions
- **Localization**: Full Uzbek language interface with comprehensive regional data for all Uzbekistan provinces and districts
- **User Experience**: Progressive disclosure with context-aware menus based on user roles and registration status

## Role-Based Access Control
- **Super Admin**: Complete system control including admin management, test creation/deletion, broadcasting, and enhanced reporting
- **Special Admin Privileges**: Hardcoded IDs (6578706277, 7853664401) with elevated permissions
- **Regular Users**: Test-taking and profile management
- **Security**: Role validation on all sensitive operations with audit logging

## Testing and Assessment Engine
- **Age Groups**: Separate test categories for 7-10 and 11-14 year olds
- **Question Format**: Multiple choice (A, B, C, D) with automatic scoring
- **Test Management**: UUID-based test identification with book name association
- **Result Tracking**: Detailed answer logging, time tracking, and percentage calculation
- **Clean Assessment**: Pure educational evaluation focused on learning outcomes

## Geographic Data Integration
- **Coverage**: Complete Uzbekistan administrative divisions (regions, districts, mahallas)
- **Structure**: Hierarchical selection system for accurate user location tracking
- **Analytics**: Regional statistics and demographic analysis capabilities
- **Compliance**: Local administrative structure alignment for official reporting

## Broadcasting and Communication
- **Mass Messaging**: Broadcast system for announcements to all registered users
- **Message Tracking**: Success/failure counting with detailed delivery reports
- **Admin Notifications**: Real-time updates on system activities and user registrations
- **Channel Integration**: Connection to @Kitobxon_Kids Telegram channel for extended reach

## Timezone and Localization
- **Timezone**: Uzbekistan time (UTC+5) for all timestamps and date operations
- **Date Formatting**: Localized date/time display consistent with regional preferences
- **Language**: Full Uzbek language support throughout the interface
- **Cultural Adaptation**: Menu structures and workflows adapted for local educational practices
