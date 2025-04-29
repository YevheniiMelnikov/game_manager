from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    RegisterView,
    LoginView,
    UserRegistrationView,
    RegistrationSuccessView,
)
from django.contrib.auth import views as auth_views

router = DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path("api/v1/register/", RegisterView.as_view(), name="api_register"),
    path("api/v1/login/", LoginView.as_view(), name="api_login"),
    path("api/v1/logout/", auth_views.LogoutView.as_view(), name="api_logout"),
    path("api/v1/", include(router.urls)),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("register/success/", RegistrationSuccessView.as_view(), name="register_success"),
]
