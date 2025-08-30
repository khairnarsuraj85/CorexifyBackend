import re
from datetime import datetime

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number (basic validation)"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    # Check if we have between 10-15 digits
    return 10 <= len(digits) <= 15

def format_date(date_obj):
    """Format datetime object to string"""
    if isinstance(date_obj, datetime):
        return date_obj.isoformat()
    return date_obj