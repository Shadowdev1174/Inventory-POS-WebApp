release: python manage.py migrate
web: gunicorn inventory_pos.wsgi --bind 0.0.0.0:$PORT