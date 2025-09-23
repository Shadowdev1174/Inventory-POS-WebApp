release: python manage.py migrate && python manage.py create_admin
web: gunicorn inventory_pos.wsgi --bind 0.0.0.0:$PORT