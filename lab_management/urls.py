"""
URL configuration for lab_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from lab_management.views import RegisterView

urlpatterns = [
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/", include("inventory.urls")),
    path('admin/', admin.site.urls),
    path("app/", include("lab_management.web_urls")),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path(
        "painel/",
        RedirectView.as_view(pattern_name="app:dashboard", permanent=False),
        name="painel",
    ),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('forgot-password/', auth_views.PasswordResetView.as_view(template_name='forgot_password.html', success_url='/forgot-password/done/'), name='forgot_password'),
    path('forgot-password/done/', auth_views.PasswordResetDoneView.as_view(template_name='forgot_password_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html', success_url='/reset/done/'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]
