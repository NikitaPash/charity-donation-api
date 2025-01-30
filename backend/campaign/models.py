"""
Database model for Campaign API.
"""
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from decimal import Decimal
from datetime import timedelta
import uuid
import os


def campaign_image_file_path(instance, filename):
    """Generate file path for new campaign image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'campaign', filename)


def default_deadline():
    """Return a default campaign deadline"""
    return now() + timedelta(days=90)


class Campaign(models.Model):
    """Campaign object."""

    class CampaignStatusChoice(models.TextChoices):
        """Status choices for campaign."""
        ACTIVE = 'AC', _('Active')
        COMPLETED = 'CO', _('Completed')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    goal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    status = models.CharField(
        max_length=10,
        choices=CampaignStatusChoice,
        default=CampaignStatusChoice.ACTIVE,
        db_index=True,
    )
    raised_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    deadline = models.DateTimeField(default=default_deadline)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    image = models.ImageField(null=True, upload_to=campaign_image_file_path)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Override save method to handle custom validation."""
        if self.goal_amount <= self.raised_amount:
            self.status = Campaign.CampaignStatusChoice.COMPLETED

        super().save(*args, **kwargs)
