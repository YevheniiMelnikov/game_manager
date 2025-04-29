from rest_framework import viewsets

from .models import Game, GameSession, GameResults, Company
from .serializers import GameSerializer, GameSessionSerializer, GameResultsSerializer, CompanySerializer


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameSessionViewSet(viewsets.ModelViewSet):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer


class GameResultsViewSet(viewsets.ModelViewSet):
    queryset = GameResults.objects.all()
    serializer_class = GameResultsSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
