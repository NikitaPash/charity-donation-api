"""
Database model for Donation API.
"""
from django.conf import settings
from django.db import models

from campaign.models import Campaign


class Donation(models.Model):
    """Donation object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - ${self.amount} - {self.campaign}'
