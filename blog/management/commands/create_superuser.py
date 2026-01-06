from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Creates a superuser if one does not exist'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'ru')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@rudjango.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '6JIIcUfc6qlc5ZCu')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" created successfully')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Superuser "{username}" already exists')
            )
