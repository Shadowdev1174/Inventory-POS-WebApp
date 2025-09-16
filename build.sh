#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # exit on error

echo "🚀 Starting build process..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth.models import User
from accounts.models import UserProfile
import os

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username=username, email=email, password=password)
    # Create profile for the superuser
    UserProfile.objects.get_or_create(user=user, defaults={
        'bio': 'System Administrator',
        'job_title': 'Admin',
        'phone': '123-456-7890'
    })
    print(f"✅ Superuser '{username}' created successfully!")
else:
    print(f"✅ Superuser '{username}' already exists.")
EOF

echo "✅ Build completed successfully!"