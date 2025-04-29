from django.urls import path
from ..users.views import UserRegistrationView, RegistrationSuccessView

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("register/success/", RegistrationSuccessView.as_view(), name="register_success"),
]
