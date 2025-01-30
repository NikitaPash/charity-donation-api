"""
URL mappings for the donation app.
"""
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import DonationViewSet

router = DefaultRouter()
router.register(r'donations', DonationViewSet, basename='donation')

app_name = 'donation'

urlpatterns = [
    path('', include(router.urls)),
]
