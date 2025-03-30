from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from games.views import (
    CompanyListCreateView,
    ParticipantListCreateView,
    GameListCreateView,
    GameSessionListCreateView,
    GameResultsListCreateView,
)


def health_check(request):
    return HttpResponse("OK")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health"),
    path("api/auth/", include("rest_framework.urls")),
    path("api/companies/", CompanyListCreateView.as_view(), name="company-list"),
    path("api/participants/", ParticipantListCreateView.as_view(), name="participant-list"),
    path("api/games/", GameListCreateView.as_view(), name="game-list"),
    path("api/gamesessions/", GameSessionListCreateView.as_view(), name="gamesession-list"),
    path("api/gameresults/", GameResultsListCreateView.as_view(), name="gameresults-list"),
]
