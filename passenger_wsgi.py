"""
WSGI config for cPanel deployment
This file is used by cPanel's Python application to serve the Django backend

DEPLOYMENT INSTRUCTIONS:
1. Upload backend folder to: /home/tmfouzys/backend.tmfouzy.sg/
2. Update project_home path below to match your cPanel username
3. Install requirements: pip install -r requirements.txt
4. Run migrations: python manage.py migrate
5. Collect static files: python manage.py collectstatic
6. Create superuser: python manage.py createsuperuser
"""

import os
import sys

# Add your project directory to the sys.path
# IMPORTANT: Update 'tmfouzys' to your actual cPanel username
project_home = '/home/tmfouzys/backend.tmfouzy.sg'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variable to tell Django where settings are
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(project_home, '.env'))
except ImportError:
    pass  # python-dotenv not installed

# Import Django's WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
