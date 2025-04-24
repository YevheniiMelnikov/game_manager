from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.routers import DefaultRouter
from games.views import (
    CompanyViewSet,
    GameViewSet,
    GameSessionViewSet,
    GameResultsViewSet,
    UserViewSet,
    RegisterView,
    LoginView,
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
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("jet/", include(("jet.urls", "jet"), namespace="jet")),
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health"),
    path("api/v1/auth/", include("rest_framework.urls")),
    path("api/v1/register/", RegisterView.as_view(), name="api-register"),
    path("api/v1/login/", LoginView.as_view(), name="api-login"),
    path("api/v1/logout/", auth_views.LogoutView.as_view(), name="api-logout"),
    path("api/v1/", include(router.urls)),
    path("", include("games.urls")),
]
