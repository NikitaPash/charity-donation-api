"""
URL mappings for the user API.
"""
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path

from .views import CreateUserView, ManageUserView, TopUpView

app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('profile/', ManageUserView.as_view(), name='profile'),
    path('profile/topup', TopUpView.as_view(), name='topup_balance'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
