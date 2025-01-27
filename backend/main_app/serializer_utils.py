"""
Utils for project serializers.
"""
import logging

from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class RestrictedFieldValidatorMixin:
    """Mixin to prevent updates to restricted fields"""

    def validate(self, data):
        """Validation for restricted fields"""
        restricted_fields = getattr(self.Meta, 'restricted_fields', [])  # type: ignore

        for field in restricted_fields:
            if field in self.initial_data:  # type: ignore
                user_email = self.instance.email if hasattr(self.instance, 'email') else 'unknown'  # type: ignore
                logger.warning(f"User {user_email} attempted to update restricted field '{field}'")
                raise ValidationError({field: f'Updating {field} is not allowed.'})

        return super().validate(data)  # type: ignore
