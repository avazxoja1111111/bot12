#!/usr/bin/env python3
"""
Enhanced error handling and recovery module for Kitobxon Kids Bot
Comprehensive error management for high-availability operations
"""

import asyncio
import logging
import traceback
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Union
from functools import wraps

from aiogram import Bot
from aiogram.exceptions import (
    TelegramAPIError, TelegramBadRequest, TelegramForbiddenError,
    TelegramNetworkError, TelegramRetryAfter, TelegramServerError,
    TelegramUnauthorizedError
)
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)

class ErrorStats:
    """Error statistics tracking"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.last_errors: Dict[str, datetime] = {}
        self.total_errors = 0
        self.reset_time = datetime.now(timezone.utc)
        
    def record_error(self, error_type: str):
        """Record an error occurrence"""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.last_errors[error_type] = datetime.now(timezone.utc)
        self.total_errors += 1
        
    def get_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            'total_errors': self.total_errors,
            'error_counts': self.error_counts.copy(),
            'last_errors': {k: v.isoformat() for k, v in self.last_errors.items()},
            'reset_time': self.reset_time.isoformat()
        }
        
    def reset_stats(self):
        """Reset error statistics"""
        self.error_counts.clear()
        self.last_errors.clear()
        self.total_errors = 0
        self.reset_time = datetime.now(timezone.utc)

# Global error statistics
error_stats = ErrorStats()

class EnhancedErrorHandler:
    """Enhanced error handler with recovery mechanisms"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.max_retries = 3
        self.retry_delays = [1, 2, 4]  # Exponential backoff
        
    async def handle_telegram_error(self, error: TelegramAPIError, context: str = "") -> bool:
        """Handle Telegram API errors with appropriate recovery"""
        error_type = type(error).__name__
        error_stats.record_error(error_type)
        
        logger.error(f"Telegram API error in {context}: {error_type} - {str(error)}")
        
        if isinstance(error, TelegramForbiddenError):
            # User blocked the bot - not recoverable
            logger.info(f"User blocked the bot: {str(error)}")
            return False
            
        elif isinstance(error, TelegramRetryAfter):
            # Rate limit - wait and retry
            retry_after = error.retry_after
            logger.warning(f"Rate limited, waiting {retry_after} seconds")
            await asyncio.sleep(retry_after)
            return True
            
        elif isinstance(error, TelegramNetworkError):
            # Network error - retry with backoff
            logger.warning(f"Network error: {str(error)}")
            return True
            
        elif isinstance(error, TelegramServerError):
            # Server error - retry with backoff
            logger.warning(f"Telegram server error: {str(error)}")
            return True
            
        elif isinstance(error, TelegramBadRequest):
            # Bad request - log and don't retry
            logger.error(f"Bad request: {str(error)}")
            return False
            
        elif isinstance(error, TelegramUnauthorizedError):
            # Unauthorized - critical error
            logger.critical(f"Unauthorized error: {str(error)}")
            return False
            
        else:
            # Unknown error - log and don't retry
            logger.error(f"Unknown Telegram error: {str(error)}")
            return False
    
    async def safe_send_message(self, chat_id: int, text: str, **kwargs) -> Optional[Message]:
        """Safely send message with error handling and retry"""
        for attempt in range(self.max_retries):
            try:
                return await self.bot.send_message(chat_id, text, **kwargs)
                
            except TelegramAPIError as e:
                should_retry = await self.handle_telegram_error(e, f"send_message to {chat_id}")
                
                if not should_retry:
                    return None
                    
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Unexpected error sending message to {chat_id}: {str(e)}")
                error_stats.record_error("UnexpectedError")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delays[min(attempt, len(self.retry_delays) - 1)])
                    
        logger.error(f"Failed to send message to {chat_id} after {self.max_retries} attempts")
        return None
    
    async def safe_edit_message(self, chat_id: int, message_id: int, text: str, **kwargs) -> bool:
        """Safely edit message with error handling and retry"""
        for attempt in range(self.max_retries):
            try:
                await self.bot.edit_message_text(text, chat_id, message_id, **kwargs)
                return True
                
            except TelegramAPIError as e:
                should_retry = await self.handle_telegram_error(e, f"edit_message {message_id} in {chat_id}")
                
                if not should_retry:
                    return False
                    
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Unexpected error editing message {message_id} in {chat_id}: {str(e)}")
                error_stats.record_error("UnexpectedError")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delays[min(attempt, len(self.retry_delays) - 1)])
                    
        logger.error(f"Failed to edit message {message_id} in {chat_id} after {self.max_retries} attempts")
        return False
    
    async def safe_answer_callback(self, callback_query: CallbackQuery, text: str = "", **kwargs) -> bool:
        """Safely answer callback query with error handling"""
        for attempt in range(self.max_retries):
            try:
                await callback_query.answer(text, **kwargs)
                return True
                
            except TelegramAPIError as e:
                should_retry = await self.handle_telegram_error(e, f"answer_callback {callback_query.id}")
                
                if not should_retry:
                    return False
                    
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Unexpected error answering callback {callback_query.id}: {str(e)}")
                error_stats.record_error("UnexpectedError")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delays[min(attempt, len(self.retry_delays) - 1)])
                    
        logger.error(f"Failed to answer callback {callback_query.id} after {self.max_retries} attempts")
        return False

def error_handler(context: str = ""):
    """Decorator for enhanced error handling in handlers"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except TelegramAPIError as e:
                error_type = type(e).__name__
                error_stats.record_error(error_type)
                logger.error(f"Telegram API error in {context or func.__name__}: {error_type} - {str(e)}")
                
                # Try to send error message to user if possible
                try:
                    if args and hasattr(args[0], 'from_user'):
                        user_id = args[0].from_user.id
                        if hasattr(args[0], 'bot'):
                            await args[0].bot.send_message(
                                user_id,
                                "⚠️ Vaqtincha texnik xatolik yuz berdi. Iltimos, bir oz kuting va qayta urinib ko'ring."
                            )
                except:
                    pass  # Ignore errors in error handling
                    
            except Exception as e:
                error_stats.record_error("UnexpectedError")
                logger.error(f"Unexpected error in {context or func.__name__}: {str(e)}")
                logger.debug(f"Traceback: {traceback.format_exc()}")
                
                # Try to send generic error message
                try:
                    if args and hasattr(args[0], 'from_user'):
                        user_id = args[0].from_user.id
                        if hasattr(args[0], 'bot'):
                            await args[0].bot.send_message(
                                user_id,
                                "❌ Kutilmagan xatolik yuz berdi. Administrator bilan bog'laning."
                            )
                except:
                    pass  # Ignore errors in error handling
                    
        return wrapper
    return decorator

def safe_operation(max_retries: int = 3, delay: float = 1.0):
    """Decorator for safe operations with retry logic"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    error_stats.record_error(type(e).__name__)
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
            
            logger.error(f"All {max_retries} attempts failed for {func.__name__}: {str(last_error)}")
            raise last_error
            
        return wrapper
    return decorator

async def log_error_context(error: Exception, context: Dict[str, Any]):
    """Log error with detailed context"""
    logger.error(f"Error occurred: {type(error).__name__} - {str(error)}")
    logger.error(f"Context: {context}")
    logger.debug(f"Traceback: {traceback.format_exc()}")

def get_user_friendly_error(error: Exception) -> str:
    """Convert technical errors to user-friendly messages"""
    if isinstance(error, TelegramForbiddenError):
        return "⚠️ Bot sizga xabar yuborolmaydi. Iltimos, botni qayta ishga tushiring."
    elif isinstance(error, TelegramNetworkError):
        return "🌐 Internet bilan bog'lanishda muammo. Iltimos, qayta urinib ko'ring."
    elif isinstance(error, TelegramServerError):
        return "🔧 Telegram serverida vaqtincha muammo. Bir oz kuting va qayta urinib ko'ring."
    elif isinstance(error, TelegramRetryAfter):
        return "⏱️ Juda ko'p so'rov yuborildi. Bir oz kuting va qayta urinib ko'ring."
    else:
        return "❌ Kutilmagan xatolik yuz berdi. Administrator bilan bog'laning."
