"""
Database model for User API.
"""
from django.contrib.auth.base_user import (AbstractBaseUser, BaseUserManager)
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db import models

import logging

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not email:
            logger.error('Attempted to create a user without an email.')
            raise ValueError(_('User must have an email'))
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        logger.info('New user created.')

        return user

    def create_superuser(self, email, password):
        """Create, save and return a new superuser."""
        logger.info('Creating superuser')
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.role = User.UserRoleChoice.ADMIN
        user.save(using=self._db)
        logger.info('Superuser created.')

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""

    class UserRoleChoice(models.TextChoices):
        """Role choices for user"""
        DONOR = 'DO', _('Donor')
        CAMPAIGN_MANAGER = 'CM', _('Campaign Manager')
        ADMIN = 'AD', _('Admin')

    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(
        max_length=50,
        choices=UserRoleChoice,
        default=UserRoleChoice.DONOR,
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def add_balance(self, amount):
        """Add some amount to user's balance."""
        if amount <= 0:
            logger.error(f'Invalid balance addition attempt for user {self.email}: {amount}')
            raise ValueError(_('Amount must be positive.'))

        self.balance += amount
        self.save()
        logger.info(f'Added {amount} to balance for user {self.email}. New balance: {self.balance}')

    def deduct_balance(self, amount):
        """Deduct some amount from user's balance."""
        if amount > self.balance:
            logger.warning(
                f'Insufficient balance for user {self.email}. '
                f'Tried to deduct: {amount}, available: {self.balance}'
            )
            raise ValueError(_('Insufficient balance.'))
        if amount < 0:
            logger.error(f'Invalid balance deduction attempt for user {self.email}: {amount}')
            raise ValueError(_('Incorrect amount to deduct'))

        self.balance -= amount
        self.save()
        logger.info(f'Deducted {amount} from balance for user {self.email}. New balance: {self.balance}')
