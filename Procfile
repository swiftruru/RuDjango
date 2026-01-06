release: . /app/.venv/bin/activate && python manage.py migrate
web: . /app/.venv/bin/activate && daphne -b 0.0.0.0 -p ${PORT:-8000} RuDjangoProject.asgi:application
