"""
Django admin customizations for Donation model.
"""
from django.contrib import admin

from .models import Donation

admin.site.register(Donation)
