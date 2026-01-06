release: python manage.py migrate
web: python manage.py collectstatic --no-input && gunicorn --bind 0.0.0.0:${PORT:-8000} RuDjangoProject.wsgi:application
