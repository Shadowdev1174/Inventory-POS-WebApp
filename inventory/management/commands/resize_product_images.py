from django.core.management.base import BaseCommand
from inventory.models import Product
from django.core.files.base import ContentFile
from PIL import Image
import os
from io import BytesIO


class Command(BaseCommand):
    help = 'Resize existing product images to 300x300 pixels'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be resized without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write('DRY RUN - No files will be modified')
        
        products_with_images = Product.objects.filter(image__isnull=False).exclude(image='')
        total_products = products_with_images.count()
        
        if total_products == 0:
            self.stdout.write('No products with images found.')
            return
        
        self.stdout.write(f'Found {total_products} products with images.')
        
        processed = 0
        errors = 0
        
        for product in products_with_images:
            try:
                if dry_run:
                    self.stdout.write(f'Would resize: {product.name} - {product.image.name}')
                else:
                    # Get current image
                    current_image = product.image
                    
                    # Resize using the same method as in the model
                    resized_image = self.resize_image(current_image)
                    
                    if resized_image != current_image:
                        # Save the resized image
                        product.image.save(
                            resized_image.name,
                            resized_image,
                            save=False  # Don't trigger save() again
                        )
                        product.save(update_fields=['image'])
                        
                        self.stdout.write(f'✓ Resized: {product.name}')
                    else:
                        self.stdout.write(f'- Skipped: {product.name} (resize failed)')
                
                processed += 1
                
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing {product.name}: {e}')
                )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Completed! Processed: {processed}, Errors: {errors}'
                )
            )
        else:
            self.stdout.write(f'DRY RUN completed. Would process {processed} images.')

    def resize_image(self, image):
        """
        Resize image to 300x300 with white background
        """
        try:
            # Open the image
            img = Image.open(image)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to 300x300 with high quality
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
            name_without_ext = os.path.splitext(os.path.basename(original_name))[0]
            resized_image.name = f"{name_without_ext}_resized.jpg"
            
            return resized_image
            
        except Exception as e:
            print(f"Image resizing failed: {e}")
            return image