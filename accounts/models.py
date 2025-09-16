from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('MANAGER', 'Manager'),
        ('CASHIER', 'Cashier'),
        ('INVENTORY_MANAGER', 'Inventory Manager'),
        ('STAFF', 'Staff'),
    ]
    
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STAFF')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Additional profile fields
    bio = models.TextField(max_length=500, blank=True, help_text="Brief description about yourself")
    date_of_birth = models.DateField(null=True, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # App preferences
    theme_preference = models.CharField(
        max_length=10, 
        choices=THEME_CHOICES, 
        default='light',
        help_text="Choose your preferred theme"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
        
    @property
    def display_name(self):
        """Return full name or username"""
        return self.user.get_full_name() or self.user.username

    @property
    def avatar_url(self):
        """Return avatar URL or default"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/images/default-avatar.png'

    def can_access_admin(self):
        return self.role in ['ADMIN', 'MANAGER']

    def can_manage_inventory(self):
        return self.role in ['ADMIN', 'MANAGER', 'INVENTORY_MANAGER']

    def can_process_sales(self):
        return self.role in ['ADMIN', 'MANAGER', 'CASHIER']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class CompanySettings(models.Model):
    """Singleton model for company-wide settings"""
    company_name = models.CharField(max_length=200, default='Inventory POS')
    logo = models.ImageField(upload_to='company/', blank=True, null=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Business settings
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Tax rate in percentage")
    currency_symbol = models.CharField(max_length=5, default='₱')
    receipt_footer = models.TextField(blank=True, help_text="Text to appear at bottom of receipts")
    
    # Theme settings
    primary_color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code")
    secondary_color = models.CharField(max_length=7, default='#6B7280', help_text="Hex color code")
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Settings"
        verbose_name_plural = "Company Settings"

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and CompanySettings.objects.exists():
            raise ValueError('Company settings already exist. Edit the existing record.')
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get or create company settings"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'company_name': 'Inventory POS',
                'tax_rate': 0.00,
                'currency_symbol': '₱',
                'primary_color': '#3B82F6',
                'secondary_color': '#6B7280',
            }
        )
        return settings
