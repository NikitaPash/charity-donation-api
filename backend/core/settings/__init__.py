"""
Dynamic settings import.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Define DJANGO_ENV in .env file as 'production' for production settings.
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')

if DJANGO_ENV == 'production':
    from .production import *
else:
    from .development import *
