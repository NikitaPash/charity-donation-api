"""
Django admin customizations for Campaign model.
"""
from django.contrib import admin

from .models import Campaign

admin.site.register(Campaign)
