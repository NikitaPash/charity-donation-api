"""
Database model for Campaign API.
"""
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from decimal import Decimal
from datetime import timedelta


def default_deadline():
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

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Override save method to handle custom validation."""
        if self.deadline <= now():
            raise ValidationError(_('Deadline must be in the future'))

        if self.goal_amount <= self.raised_amount:
            self.status = Campaign.CampaignStatusChoice.COMPLETED

        super().save(*args, **kwargs)
