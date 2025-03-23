from rest_framework import generics
from .models import Game, GameSession, GameResults
from .serializers import GameSerializer, GameSessionSerializer, GameResultsSerializer


class GameListCreateView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameSessionListCreateView(generics.ListCreateAPIView):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer


class GameResultsListCreateView(generics.ListCreateAPIView):
    queryset = GameResults.objects.all()
    serializer_class = GameResultsSerializer
