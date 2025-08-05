from datetime import datetime
import re

def format_datetime(dt_string):
    """Format datetime string for display"""
    if not dt_string:
        return ''
    
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return dt_string

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return ''
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>"\']', '', text)
    return text.strip()

def get_status_badge_class(status):
    """Get Bootstrap badge class for task status"""
    status_classes = {
        'pending': 'bg-secondary',
        'in_progress': 'bg-warning',
        'completed': 'bg-success'
    }
    return status_classes.get(status, 'bg-secondary')

def get_priority_badge_class(priority):
    """Get Bootstrap badge class for task priority"""
    priority_classes = {
        'low': 'bg-info',
        'medium': 'bg-primary',
        'high': 'bg-danger'
    }
    return priority_classes.get(priority, 'bg-primary')

def paginate_query_string(page, **filters):
    """Generate query string for pagination with filters"""
    params = {'page': page}
    for key, value in filters.items():
        if value:
            params[key] = value
    
    query_parts = [f"{key}={value}" for key, value in params.items()]
    return '&'.join(query_parts)
