"""
Views for the user API.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import TopUpSerializer, UserProfileSerializer, UserSerializer

import logging

logger = logging.getLogger(__name__)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class TopUpView(generics.CreateAPIView):
    """Top up the authenticated user's balance."""
    serializer_class = TopUpSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Handle the balance update logic."""
        user = self.request.user
        amount = serializer.validated_data['amount']

        logger.info(f'Top-up initiated for {user.email} - amount: {amount}')

        user.add_balance(amount)
        logger.info(f'Balance updated for {user.email}. New balance: {user.balance}')

    def create(self, request, *args, **kwargs):
        """Wrap creation to handle custom response and errors."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            response = super().create(request, *args, **kwargs)

            response.data = {'status': 'Balance updated', 'new_balance': request.user.balance}
            response.status_code = status.HTTP_200_OK
            return response

        except ValidationError as e:
            logger.warning(f'Top-up validation failed for {request.user.email}. '
                           f'Errors: {e.detail}')
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
