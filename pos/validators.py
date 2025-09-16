"""
Custom validators for POS application to enhance security
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os


def validate_image_file(file):
    """Validate uploaded image files for security and size"""
    if not file:
        return
    
    # Check file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if file.size > max_size:
        raise ValidationError(_('Image file too large. Maximum size is 5MB.'))
    
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(_('Invalid file type. Allowed types: JPG, PNG, GIF, WebP'))
    
    # Check if it's actually an image
    try:
        # Open and check the image without verify() to avoid corruption
        img = Image.open(file)
        
        # Check image dimensions (max 4000x4000 - will be auto-resized to 300x300)
        if img.width > 4000 or img.height > 4000:
            raise ValidationError(_('Image dimensions too large. Maximum: 4000x4000 pixels (will be auto-resized to 300x300)'))
            
        # Check for minimum dimensions
        if img.width < 50 or img.height < 50:
            raise ValidationError(_('Image too small. Minimum: 50x50 pixels'))
            
        # Just check if we can read the format - this is safer than verify()
        if not img.format:
            raise ValidationError(_('Invalid image format'))
            
    except Exception as e:
        raise ValidationError(_('Invalid image file or corrupted image'))
    
    # Reset file pointer after validation
    file.seek(0)


def validate_no_script_tags(value):
    """Prevent script injection in text fields"""
    if '<script' in value.lower() or '</script>' in value.lower():
        raise ValidationError(_('Script tags are not allowed'))
    
    if 'javascript:' in value.lower():
        raise ValidationError(_('JavaScript protocols are not allowed'))


def validate_safe_text(value):
    """Validate text fields to prevent various injection attacks"""
    # Check for common SQL injection patterns
    sql_patterns = [
        r'(\s|^)(union|select|insert|update|delete|drop|create|alter)\s',
        r'(\s|^)(or|and)\s+\d+\s*=\s*\d+',
        r'(\s|^)(or|and)\s+[\'"`]\w+[\'"`]\s*=\s*[\'"`]\w+[\'"`]',
        r'(\s|^)(exec|execute)\s*\(',
        r'(\s|^)(sp_|xp_)\w+',
        r'--',
        r'/\*.*\*/',
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, value.lower()):
            raise ValidationError(_('Invalid characters detected'))
    
    # Check for XSS patterns
    xss_patterns = [
        r'<\s*script\s*>',
        r'javascript\s*:',
        r'on\w+\s*=',
        r'<\s*iframe\s*>',
        r'<\s*object\s*>',
        r'<\s*embed\s*>',
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, value.lower()):
            raise ValidationError(_('Potentially unsafe content detected'))


def validate_positive_number(value):
    """Ensure numeric values are positive"""
    if value < 0:
        raise ValidationError(_('Value must be positive'))


def validate_reasonable_price(value):
    """Validate that prices are reasonable (not too high)"""
    if value > 1000000:  # 1 million limit
        raise ValidationError(_('Price seems unreasonably high'))
    
    if value < 0:
        raise ValidationError(_('Price cannot be negative'))


def validate_reasonable_quantity(value):
    """Validate that quantities are reasonable"""
    if value > 100000:  # 100k limit
        raise ValidationError(_('Quantity seems unreasonably high'))
    
    if value < 0:
        raise ValidationError(_('Quantity cannot be negative'))


def validate_product_name(value):
    """Validate product names"""
    if len(value.strip()) < 2:
        raise ValidationError(_('Product name must be at least 2 characters'))
    
    # Apply general text validation
    validate_safe_text(value)
    validate_no_script_tags(value)
    
    # Check for excessive special characters
    special_chars = len(re.findall(r'[^a-zA-Z0-9\s\-_\.]', value))
    if special_chars > len(value) * 0.3:  # More than 30% special chars
        raise ValidationError(_('Product name contains too many special characters'))


def validate_category_name(value):
    """Validate category names"""
    if len(value.strip()) < 2:
        raise ValidationError(_('Category name must be at least 2 characters'))
    
    # Apply general text validation
    validate_safe_text(value)
    validate_no_script_tags(value)