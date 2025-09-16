web: python manage.py migrate && python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_pos.settings')
django.setup()
from django.contrib.auth.models import User
try:
    user = User.objects.create_user('testuser', 'test@example.com', 'password123')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print('Test user created successfully')
except:
    print('User might already exist')
" && gunicorn inventory_pos.wsgi:application
