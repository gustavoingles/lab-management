from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import EmailTokenObtainPairView, MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="api_register"),
    path("token/", EmailTokenObtainPairView.as_view(), name="api_token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="api_token_refresh"),
    path("me/", MeView.as_view(), name="api_me"),
]
