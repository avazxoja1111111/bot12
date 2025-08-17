#!/usr/bin/env python3
"""
Utility functions for Kitobxon Kids Educational Bot
Contains validation functions, formatting helpers, and common utilities
"""

import re
import json
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from config import REGIONS_DATA, AGE_GROUPS, SUPPORTED_FORMATS, SUPPORTED_MIME_TYPES

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════════
# VALIDATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def validate_name(name: str) -> bool:
    """
    Validate name format for Uzbek names
    
    Args:
        name: Name string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not name or len(name.strip()) < 2:
        return False
    
    # Allow Uzbek letters, spaces, apostrophes, and hyphens
    pattern = r"^[A-Za-zÀ-ÿĀ-žА-яЁё\s'\-]+$"
    return bool(re.match(pattern, name.strip()))

def validate_age(age_str: str) -> bool:
    """
    Validate age input (must be 7-14 years)
    
    Args:
        age_str: Age as string
        
    Returns:
        bool: True if valid age, False otherwise
    """
    try:
        age = int(age_str)
        return 7 <= age <= 14
    except ValueError:
        return False

def validate_phone(phone: str) -> bool:
    """
    Validate Uzbekistan phone number format
    
    Args:
        phone: Phone number string
        
    Returns:
        bool: True if valid format, False otherwise
    """
    # Remove all non-digit characters
    clean_phone = re.sub(r'\D', '', phone)
    
    # Check for Uzbek mobile numbers patterns
    uzbek_patterns = [
        r'^998[0-9]{9}$',      # +998XXXXXXXXX (full international)
        r'^[0-9]{9}$',         # XXXXXXXXX (local mobile)
        r'^[0-9]{12}$'         # 998XXXXXXXXX (international without +)
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in uzbek_patterns)

def validate_region(region: str) -> bool:
    """
    Check if region exists in Uzbekistan regional data
    
    Args:
        region: Region name
        
    Returns:
        bool: True if valid region
    """
    return region in REGIONS_DATA

def validate_district(region: str, district: str) -> bool:
    """
    Check if district exists in the specified region
    
    Args:
        region: Region name
        district: District name
        
    Returns:
        bool: True if valid district in region
    """
    if region not in REGIONS_DATA:
        return False
    return district in REGIONS_DATA[region]

def validate_mahalla(region: str, district: str, mahalla: str) -> bool:
    """
    Check if mahalla exists in the specified district
    
    Args:
        region: Region name
        district: District name
        mahalla: Mahalla name
        
    Returns:
        bool: True if valid mahalla in district
    """
    if not validate_district(region, district):
        return False
    return mahalla in REGIONS_DATA[region][district]

def validate_document_format(filename: str, mime_type: str) -> bool:
    """
    Validate document format (PDF, Word, Excel, Text)
    
    Args:
        filename: Document filename
        mime_type: Document MIME type
        
    Returns:
        bool: True if supported format
    """
    if not filename:
        return False
        
    file_ext = Path(filename).suffix.lower()
    
    # Check by extension
    for format_exts in SUPPORTED_FORMATS.values():
        if file_ext in format_exts:
            return True
    
    # Check by MIME type
    return mime_type in SUPPORTED_MIME_TYPES

def get_document_type(filename: str, mime_type: str = "") -> str:
    """
    Get document type from filename and mime type
    
    Args:
        filename: Document filename
        mime_type: Document MIME type
        
    Returns:
        str: Document type (text, word, excel, pdf, unknown)
    """
    if not filename:
        return "unknown"
        
    file_ext = Path(filename).suffix.lower()
    
    # Check by extension first
    for doc_type, extensions in SUPPORTED_FORMATS.items():
        if file_ext in extensions:
            return doc_type
    
    # Check by MIME type
    if 'text' in mime_type:
        return 'text'
    elif 'word' in mime_type or 'officedocument.wordprocessing' in mime_type:
        return 'word'
    elif 'excel' in mime_type or 'spreadsheet' in mime_type:
        return 'excel'
    elif 'pdf' in mime_type:
        return 'pdf'
    
    return 'unknown'

def get_age_group(age: int) -> str:
    """
    Get age group for given age
    
    Args:
        age: Child's age
        
    Returns:
        str: Age group identifier (7-10 or 11-14)
    """
    for group_id, group_data in AGE_GROUPS.items():
        if group_data["min"] <= age <= group_data["max"]:
            return group_id
    
    return "unknown"

# ═══════════════════════════════════════════════════════════════════════════════════
# FORMATTING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def format_phone_number(phone: str) -> str:
    """
    Format phone number to standard Uzbek format
    
    Args:
        phone: Raw phone number
        
    Returns:
        str: Formatted phone number
    """
    # Remove all non-digit characters
    clean_phone = re.sub(r'\D', '', phone)
    
    # Format based on length
    if len(clean_phone) == 9:
        # Local format: add +998
        return f"+998{clean_phone}"
    elif len(clean_phone) == 12 and clean_phone.startswith('998'):
        # International without +: add +
        return f"+{clean_phone}"
    elif len(clean_phone) == 12 and clean_phone.startswith('998'):
        return f"+{clean_phone}"
    
    return phone  # Return original if can't format

def format_user_name(first_name: str, last_name: str = None, username: str = None) -> str:
    """
    Format user display name
    
    Args:
        first_name: User's first name
        last_name: User's last name (optional)
        username: User's username (optional)
        
    Returns:
        str: Formatted display name
    """
    name_parts = [first_name]
    if last_name:
        name_parts.append(last_name)
    
    full_name = " ".join(name_parts)
    
    if username:
        return f"{full_name} (@{username})"
    
    return full_name

def format_datetime(dt: Union[str, datetime], format_str: str = "%d.%m.%Y %H:%M") -> str:
    """
    Format datetime for display
    
    Args:
        dt: Datetime string or object
        format_str: Format string
        
    Returns:
        str: Formatted datetime string
    """
    try:
        if isinstance(dt, str):
            # Parse ISO format datetime
            parsed_dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        else:
            parsed_dt = dt
        
        return parsed_dt.strftime(format_str)
    except Exception:
        return str(dt)

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def format_duration(seconds: float) -> str:
    """
    Format duration in human readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}:{minutes:02d}:00"

def format_score(score: float, total: int = 100) -> str:
    """
    Format test score with emoji
    
    Args:
        score: Score value
        total: Total possible score
        
    Returns:
        str: Formatted score with emoji
    """
    percentage = (score / total * 100) if total > 0 else 0
    
    if percentage >= 90:
        emoji = "🥇"
    elif percentage >= 70:
        emoji = "🥈"
    elif percentage >= 50:
        emoji = "🥉"
    else:
        emoji = "📝"
    
    return f"{emoji} {percentage:.1f}%"

# ═══════════════════════════════════════════════════════════════════════════════════
# TEXT PROCESSING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def clean_text(text: str, max_length: int = None) -> str:
    """
    Clean and sanitize text input
    
    Args:
        text: Input text
        max_length: Maximum length (optional)
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Remove potentially dangerous HTML/script tags
    cleaned = re.sub(r'<script[^>]*>.*?</script>', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<[^>]+>', '', cleaned)  # Remove other HTML tags
    
    # Truncate if needed
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length - 3] + "..."
    
    return cleaned

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text
    
    Args:
        text: Input text
        min_length: Minimum keyword length
        
    Returns:
        List[str]: List of keywords
    """
    # Remove punctuation and convert to lowercase
    clean_text_content = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Split into words and filter
    words = [word.strip() for word in clean_text_content.split() 
             if len(word.strip()) >= min_length]
    
    # Remove duplicates while preserving order
    keywords = []
    seen = set()
    for word in words:
        if word not in seen:
            keywords.append(word)
            seen.add(word)
    
    return keywords[:10]  # Return top 10 keywords

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

# ═══════════════════════════════════════════════════════════════════════════════════
# DATA PROCESSING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string
    
    Args:
        json_str: JSON string
        default: Default value if parsing fails
        
    Returns:
        Any: Parsed data or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(data: Any, indent: int = None) -> str:
    """
    Safely serialize data to JSON
    
    Args:
        data: Data to serialize
        indent: JSON indentation
        
    Returns:
        str: JSON string
    """
    try:
        return json.dumps(data, ensure_ascii=False, indent=indent, default=str)
    except (TypeError, ValueError):
        return "{}"

def merge_dictionaries(dict1: dict, dict2: dict) -> dict:
    """
    Deep merge two dictionaries
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        dict: Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dictionaries(result[key], value)
        else:
            result[key] = value
    
    return result

def flatten_dict(d: dict, parent_key: str = '', sep: str = '.') -> dict:
    """
    Flatten nested dictionary
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for keys
        
    Returns:
        dict: Flattened dictionary
    """
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)

# ═══════════════════════════════════════════════════════════════════════════════════
# ASYNC UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

async def retry_async(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Retry async function with exponential backoff
    
    Args:
        func: Async function to retry
        max_retries: Maximum retry attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier
        
    Returns:
        Any: Function result
        
    Raises:
        Exception: Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                await asyncio.sleep(delay * (backoff ** attempt))
            else:
                logger.error(f"Function failed after {max_retries} retries: {e}")
    
    raise last_exception

async def safe_execute(coro, default_value=None, log_errors: bool = True):
    """
    Safely execute coroutine with error handling
    
    Args:
        coro: Coroutine to execute
        default_value: Value to return on error
        log_errors: Whether to log errors
        
    Returns:
        Any: Coroutine result or default value
    """
    try:
        return await coro
    except Exception as e:
        if log_errors:
            logger.error(f"Safe execute error: {e}")
        return default_value

def batch_list(items: List[Any], batch_size: int) -> List[List[Any]]:
    """
    Split list into batches
    
    Args:
        items: List to split
        batch_size: Size of each batch
        
    Returns:
        List[List[Any]]: List of batches
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

# ═══════════════════════════════════════════════════════════════════════════════════
# REGIONAL DATA HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def get_all_regions() -> List[str]:
    """Get list of all regions"""
    return list(REGIONS_DATA.keys())

def get_districts_by_region(region: str) -> List[str]:
    """Get districts for a region"""
    return list(REGIONS_DATA.get(region, {}).keys())

def get_mahallas_by_district(region: str, district: str) -> List[str]:
    """Get mahallas for a district"""
    return REGIONS_DATA.get(region, {}).get(district, [])

def find_similar_regions(query: str, limit: int = 5) -> List[str]:
    """
    Find regions similar to query
    
    Args:
        query: Search query
        limit: Maximum results
        
    Returns:
        List[str]: Similar region names
    """
    query_lower = query.lower()
    matches = []
    
    for region in REGIONS_DATA.keys():
        if query_lower in region.lower():
            matches.append(region)
    
    return matches[:limit]

def find_similar_districts(region: str, query: str, limit: int = 5) -> List[str]:
    """
    Find districts similar to query in a region
    
    Args:
        region: Region name
        query: Search query
        limit: Maximum results
        
    Returns:
        List[str]: Similar district names
    """
    if region not in REGIONS_DATA:
        return []
    
    query_lower = query.lower()
    matches = []
    
    for district in REGIONS_DATA[region].keys():
        if query_lower in district.lower():
            matches.append(district)
    
    return matches[:limit]

def get_regional_statistics_template() -> Dict[str, Any]:
    """
    Get template for regional statistics
    
    Returns:
        Dict[str, Any]: Regional statistics template
    """
    template = {}
    
    for region, districts in REGIONS_DATA.items():
        template[region] = {
            "total_users": 0,
            "districts": {district: 0 for district in districts.keys()}
        }
    
    return template

# ═══════════════════════════════════════════════════════════════════════════════════
# LOGGING AND DEBUG HELPERS
# ═══════════════════════════════════════════════════════════════════════════════════

def log_user_action(user_id: int, action: str, details: Dict[str, Any] = None):
    """
    Log user action for debugging
    
    Args:
        user_id: User ID
        action: Action name
        details: Additional details
    """
    log_entry = {
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details or {}
    }
    
    logger.info(f"User action: {safe_json_dumps(log_entry)}")

def debug_memory_usage():
    """Log current memory usage"""
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        logger.info(f"Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB")
    except ImportError:
        logger.warning("psutil not available for memory monitoring")

# ═══════════════════════════════════════════════════════════════════════════════════
# ERROR HANDLING UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════════

class ValidationError(Exception):
    """Custom validation error"""
    pass

class ProcessingError(Exception):
    """Custom processing error"""
    pass

def create_error_response(error_type: str, message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create standardized error response
    
    Args:
        error_type: Type of error
        message: Error message
        details: Additional error details
        
    Returns:
        Dict[str, Any]: Error response
    """
    return {
        "error": True,
        "error_type": error_type,
        "message": message,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def create_success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """
    Create standardized success response
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        Dict[str, Any]: Success response
    """
    return {
        "error": False,
        "message": message,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
