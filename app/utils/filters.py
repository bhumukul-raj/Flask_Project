"""
Template filters for the application.
"""

from datetime import datetime

def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object or ISO string."""
    if not value:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return value
    return value.strftime(format) 