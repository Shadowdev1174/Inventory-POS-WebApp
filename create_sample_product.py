"""
Test script to create a sample product with image for demonstration
"""
import os
import sys
import django
from PIL import Image
import io

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_pos.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from inventory.models import Product, Category


def create_sample_image():
    """Create a sample product image for testing"""
    # Create a simple colored image
    img = Image.new('RGB', (300, 300), color='lightblue')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Create uploaded file
    return SimpleUploadedFile(
        name='sample_product.png',
        content=img_bytes.read(),
        content_type='image/png'
    )


def create_sample_product():
    """Create a sample product with image"""
    try:
        # Get or create a category
        category, created = Category.objects.get_or_create(
            name='Electronics',
            defaults={'description': 'Electronic devices and accessories'}
        )
        
        # Create sample image
        sample_image = create_sample_image()
        
        # Create product
        product = Product.objects.create(
            name='Sample Smartphone',
            selling_price=299.99,
            cost_price=199.99,
            stock_quantity=25,
            category=category,
            image=sample_image,
            minimum_stock=5,
            is_active=True
        )
        
        print(f"✅ Successfully created sample product: {product.name}")
        print(f"   Product ID: {product.id}")
        print(f"   SKU: {product.sku}")
        print(f"   Image URL: {product.image.url if product.image else 'No image'}")
        print(f"   Category: {product.category.name}")
        
        return product
        
    except Exception as e:
        print(f"❌ Error creating sample product: {e}")
        return None


if __name__ == "__main__":
    print("🖼️  Creating sample product with image...")
    product = create_sample_product()
    
    if product:
        print(f"\n✅ Sample product created successfully!")
        print(f"📍 You can now view it at: /inventory/products/{product.id}/")
        print(f"🛒 Test it in POS at: /pos/")
    else:
        print(f"\n❌ Failed to create sample product")