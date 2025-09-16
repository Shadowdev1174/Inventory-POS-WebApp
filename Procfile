web: python manage.py migrate && python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_pos.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created')
else:
    print('Admin user already exists')
" && gunicorn inventory_pos.wsgi:application
