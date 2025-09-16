from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile

# Import custom validators for security
try:
    from pos.validators import (
        validate_product_name, 
        validate_category_name, 
        validate_reasonable_price, 
        validate_reasonable_quantity,
        validate_safe_text,
        validate_image_file
    )
except ImportError:
    # Fallback if validators not available
    def validate_product_name(value):
        pass
    def validate_category_name(value):
        pass
    def validate_reasonable_price(value):
        pass
    def validate_reasonable_quantity(value):
        pass
    def validate_safe_text(value):
        pass
    def validate_image_file(value):
        pass


class Category(models.Model):
    name = models.CharField(
        max_length=100, 
        unique=True,
        validators=[validate_category_name]
    )
    description = models.TextField(
        blank=True,
        validators=[validate_safe_text]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductManager(models.Manager):
    """Custom manager for Product model to handle soft deletes"""
    
    def get_queryset(self):
        """Return only non-deleted products by default"""
        return super().get_queryset().filter(is_deleted=False)
    
    def all_with_deleted(self):
        """Return all products including soft-deleted ones"""
        return super().get_queryset()
    
    def deleted_only(self):
        """Return only soft-deleted products"""
        return super().get_queryset().filter(is_deleted=True)


class Product(models.Model):
    name = models.CharField(
        max_length=200,
        validators=[validate_product_name]
    )
    description = models.TextField(
        blank=True,
        validators=[validate_safe_text]
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    sku = models.CharField(max_length=50, unique=True, blank=True, help_text="Stock Keeping Unit - Auto-generated if not provided")
    barcode = models.CharField(max_length=100, blank=True, unique=True, null=True)
    
    # Pricing
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0), validate_reasonable_price]
    )
    selling_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0), validate_reasonable_price]
    )
    
    # Stock management
    stock_quantity = models.PositiveIntegerField(
        default=0,
        validators=[validate_reasonable_quantity]
    )
    minimum_stock = models.PositiveIntegerField(
        default=5, 
        help_text="Alert when stock falls below this level",
        validators=[validate_reasonable_quantity]
    )
    
    # Product details
    image = models.ImageField(
        upload_to='products/', 
        blank=True, 
        null=True,
        validators=[validate_image_file],
        help_text="Product image (Max: 5MB, will be automatically resized to 300x300px)"
    )
    is_active = models.BooleanField(default=True)
    
    # Soft delete functionality
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='deleted_products'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Custom manager
    objects = ProductManager()
    all_objects = models.Manager()  # Access to all objects including deleted

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0

    @property
    def is_low_stock(self):
        """Check if product is running low on stock"""
        return self.stock_quantity <= self.minimum_stock

    def soft_delete(self, user=None):
        """Soft delete the product"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    def restore(self):
        """Restore a soft-deleted product"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save()

    def hard_delete(self):
        """Permanently delete the product"""
        super().delete()

    def save(self, *args, **kwargs):
        # Auto-generate SKU if not provided
        if not self.sku:
            # Generate SKU based on category and product count
            category_code = self.category.name[:3].upper()
            product_count = Product.objects.filter(category=self.category).count() + 1
            self.sku = f"{category_code}-{product_count:04d}"
            
            # Ensure uniqueness
            while Product.objects.filter(sku=self.sku).exists():
                product_count += 1
                self.sku = f"{category_code}-{product_count:04d}"
        
        # Resize image if provided and it's a new upload
        if self.image and hasattr(self.image, 'file'):
            try:
                self.image = self.resize_image(self.image)
            except Exception as e:
                print(f"Error during image processing: {e}")
                # Continue saving without image resizing if error occurs
        
        super().save(*args, **kwargs)

    def resize_image(self, image):
        """
        Resize uploaded image to 300x300 with better error handling
        """
        try:
            # Reset file pointer to beginning
            image.seek(0)
            
            # Open the image
            img = Image.open(image)
            
            # Load the image data to avoid lazy loading issues
            img.load()
            
            # Convert to RGB if necessary (handles RGBA, P mode images)
            if img.mode in ('RGBA', 'P', 'LA'):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to 300x300 with high quality (maintaining aspect ratio)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Create a new square image with white background
            new_img = Image.new('RGB', (300, 300), (255, 255, 255))
            
            # Calculate position to center the image
            x = (300 - img.width) // 2
            y = (300 - img.height) // 2
            
            # Paste the resized image onto the white background
            new_img.paste(img, (x, y))
            
            # Save to BytesIO
            output = BytesIO()
            new_img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            # Create new ContentFile
            resized_image = ContentFile(output.read())
            
            # Keep original filename but ensure .jpg extension
            original_name = image.name
            name_without_ext = os.path.splitext(original_name)[0]
            resized_image.name = f"{name_without_ext}_resized.jpg"
            
            print(f"Successfully resized image: {original_name} -> {resized_image.name}")
            return resized_image
            
        except Exception as e:
            # If resizing fails, return original image
            print(f"Image resizing failed for {image.name}: {e}")
            image.seek(0)  # Reset pointer
            return image
        
        # Resize image if it exists
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                img.thumbnail((300, 300))
                img.save(self.image.path)


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUSTMENT', 'Adjustment'),
        ('SALE', 'Sale'),
        ('RETURN', 'Return'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=200, blank=True)
    reference = models.CharField(max_length=100, blank=True, help_text="Reference number (invoice, PO, etc.)")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Only auto-update stock for non-SALE movements
        # SALE movements are handled manually in the POS checkout
        if self.movement_type != 'SALE':
            # Update product stock based on movement type
            if self.movement_type in ['IN', 'RETURN']:
                self.product.stock_quantity += abs(self.quantity)
            elif self.movement_type == 'OUT':
                self.product.stock_quantity -= abs(self.quantity)
            elif self.movement_type == 'ADJUSTMENT':
                self.product.stock_quantity = abs(self.quantity)
            
            self.product.save()


# Removed Customer model as this is a walk-in POS system
