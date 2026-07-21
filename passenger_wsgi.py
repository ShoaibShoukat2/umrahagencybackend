import sys
import os

# Virtualenv Python path (matches .htaccess Python version 3.9)
INTERP = "/home/tmfouzys/virtualenv/backend.tmfouzy.sg/3.9/bin/python"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Project root path
sys.path.insert(0, '/home/tmfouzys/backend.tmfouzy.sg')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv('/home/tmfouzys/backend.tmfouzy.sg/.env')
except ImportError:
    pass

# Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
