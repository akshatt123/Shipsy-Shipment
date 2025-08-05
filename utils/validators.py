def validate_shipment_data(form_data):
    """Validate shipment form data"""
    errors = []
    
    sender_name = form_data.get('sender_name', '').strip()
    sender_address = form_data.get('sender_address', '').strip()
    recipient_name = form_data.get('recipient_name', '').strip()
    recipient_address = form_data.get('recipient_address', '').strip()
    weight = form_data.get('weight', '')
    status = form_data.get('status', '')
    priority = form_data.get('priority', '')
    
    # Sender validation
    if not sender_name:
        errors.append('Sender name is required!')
    elif len(sender_name) > 100:
        errors.append('Sender name must be less than 100 characters!')
    
    if not sender_address:
        errors.append('Sender address is required!')
    elif len(sender_address) > 500:
        errors.append('Sender address must be less than 500 characters!')
    
    # Recipient validation
    if not recipient_name:
        errors.append('Recipient name is required!')
    elif len(recipient_name) > 100:
        errors.append('Recipient name must be less than 100 characters!')
    
    if not recipient_address:
        errors.append('Recipient address is required!')
    elif len(recipient_address) > 500:
        errors.append('Recipient address must be less than 500 characters!')
    
    # Weight validation
    if weight:
        try:
            weight_float = float(weight)
            if weight_float < 0:
                errors.append('Weight cannot be negative!')
            elif weight_float > 1000:
                errors.append('Weight cannot exceed 1000 kg!')
        except ValueError:
            errors.append('Weight must be a valid number!')
    
    # Status validation
    valid_statuses = ['pending', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'returned']
    if status not in valid_statuses:
        errors.append('Invalid status selected!')
    
    # Priority validation
    valid_priorities = ['standard', 'priority', 'urgent']
    if priority not in valid_priorities:
        errors.append('Invalid priority selected!')
    
    # Package description validation
    package_description = form_data.get('package_description', '').strip()
    if len(package_description) > 1000:
        errors.append('Package description must be less than 1000 characters!')
    
    return errors

def validate_task_data(form_data):
    """Validate task form data"""
    errors = []
    
    title = form_data.get('title', '').strip()
    description = form_data.get('description', '').strip()
    status = form_data.get('status', '')
    priority = form_data.get('priority', '')
    
    # Title validation
    if not title:
        errors.append('Task title is required!')
    elif len(title) > 200:
        errors.append('Task title must be less than 200 characters!')
    
    # Description validation
    if len(description) > 1000:
        errors.append('Task description must be less than 1000 characters!')
    
    # Status validation
    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
    if status not in valid_statuses:
        errors.append('Invalid status selected!')
    
    # Priority validation
    valid_priorities = ['low', 'medium', 'high', 'urgent']
    if priority not in valid_priorities:
        errors.append('Invalid priority selected!')
    
    return errors

def validate_user_data(form_data):
    """Validate user registration data"""
    errors = []
    
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    # Username validation
    if not username:
        errors.append('Username is required!')
    elif len(username) < 3:
        errors.append('Username must be at least 3 characters long!')
    elif len(username) > 50:
        errors.append('Username must be less than 50 characters!')
    elif not username.isalnum():
        errors.append('Username must contain only letters and numbers!')
    
    # Password validation
    if not password:
        errors.append('Password is required!')
    elif len(password) < 6:
        errors.append('Password must be at least 6 characters long!')
    elif len(password) > 100:
        errors.append('Password must be less than 100 characters!')
    
    return errors
