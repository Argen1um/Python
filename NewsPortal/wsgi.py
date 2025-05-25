"""
WSGI config for NewsPortal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application

# Загрузка переменных окружения из .env
project_base_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(project_base_dir, '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPortal.settings')

application = get_wsgi_application()
