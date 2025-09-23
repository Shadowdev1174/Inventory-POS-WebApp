from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser if one does not exist'

    def handle(self, *args, **options):
        # Default admin credentials for Render deployment
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        password = os.environ.get('ADMIN_PASSWORD', 'admin123456')
        
        try:
            # Check if any superuser exists
            if User.objects.filter(is_superuser=True).exists():
                self.stdout.write(
                    self.style.WARNING('Superuser already exists. Skipping creation.')
                )
                return
            
            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser: {username}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Email: {email}')
            )
            self.stdout.write(
                self.style.SUCCESS('Password: admin123456')
            )
            self.stdout.write(
                self.style.WARNING('IMPORTANT: Change the password after first login!')
            )
            
        except IntegrityError:
            self.stdout.write(
                self.style.WARNING(f'User {username} already exists.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )