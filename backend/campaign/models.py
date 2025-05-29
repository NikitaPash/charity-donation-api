"""
Database model for Campaign API.
"""
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

from decimal import Decimal
from datetime import timedelta
import uuid
import os


def campaign_image_file_path(instance, filename):
    """Generate a file path for a new campaign image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'campaign', filename)


def default_deadline():
    """Return a default campaign deadline"""
    return (now() + timedelta(days=90)).date()


class Campaign(models.Model):
    """Campaign object."""

    class CampaignStatusChoice(models.TextChoices):
        """Status choices for a campaign."""
        ACTIVE = 'AC', _('Active')
        COMPLETED = 'CO', _('Completed')
        ON_MODERATION = 'OM', _('On Moderation')
        REJECTED = 'RE', _('Rejected')
        EXPIRED = 'EX', _('Expired')

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
        default=CampaignStatusChoice.ON_MODERATION,
        db_index=True,
    )
    raised_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    deadline = models.DateField(default=default_deadline)
    created_at = models.DateField(auto_now_add=True, db_index=True)
    image = models.ImageField(null=True, upload_to=campaign_image_file_path)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Override the save method to handle custom validation."""
        if self.goal_amount <= self.raised_amount:
            self.status = Campaign.CampaignStatusChoice.COMPLETED

        super().save(*args, **kwargs)


class CampaignDocument(models.Model):
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    document = models.FileField(
        upload_to='campaign_documents/%Y/%m/%d/',
        validators=[FileExtensionValidator(['pdf'])],
        help_text='Upload a PDF document supporting this campaign.'
    )
    uploaded_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.campaign.title} – {self.document.name}'
