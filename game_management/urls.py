from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

from games.views import GameListCreateView, GameSessionListCreateView, GameResultsListCreateView


def health_check(request):
    return HttpResponse("OK")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health"),
    path("api/auth/", include("rest_framework.urls")),
    path("api/games/", GameListCreateView.as_view(), name="game-list"),
    path("api/gamesessions/", GameSessionListCreateView.as_view(), name="gamesession-list"),
    path("api/gameresults/", GameResultsListCreateView.as_view(), name="gameresults-list"),
]
