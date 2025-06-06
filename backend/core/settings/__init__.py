"""
Dynamic settings import.
"""

import os

from dotenv import load_dotenv

from .base import *
from .logging import *
from .rest_framework import *

load_dotenv()

# Define DJANGO_ENV ('development'/'production') in .env file for desired settings.
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')

if DJANGO_ENV == 'production':
    from .production import *
else:
    from .development import *
