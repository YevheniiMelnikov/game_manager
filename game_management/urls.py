from django.contrib import admin
from django.http.response import HttpResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from games.views import (
    CompanyViewSet,
    GameViewSet,
    GameSessionViewSet,
    GameResultsViewSet,
    UserViewSet,
    RegisterView,
    LoginView,
    UserRegistrationView,
    RegistrationSuccessView,
)
from django.contrib.auth import views as auth_views

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)
router.register(r"games", GameViewSet)
router.register(r"gamesessions", GameSessionViewSet)
router.register(r"gameresults", GameResultsViewSet)
router.register(r"users", UserViewSet)


def health_check(request):
    return HttpResponse("OK")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health"),
    path("api/auth/", include("rest_framework.urls")),
    path("api/register/", RegisterView.as_view(), name="api-register"),
    path("api/login/", LoginView.as_view(), name="api-login"),
    path("api/logout/", auth_views.LogoutView.as_view(), name="api-logout"),
    path("api/", include(router.urls)),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("register/success/", RegistrationSuccessView.as_view(), name="register_success"),
]
