"""
URL mappings for the campaign app.
"""
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import CampaignViewSet

router = DefaultRouter()
router.register('campaigns', CampaignViewSet)

app_name = 'campaign'

urlpatterns = [
    path('', include(router.urls)),
]
