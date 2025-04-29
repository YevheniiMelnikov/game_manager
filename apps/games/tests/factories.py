import factory
from datetime import datetime
from django.utils.timezone import make_aware

from apps.games.models import Game, GameSession, GameResults


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Game

    name = factory.Sequence(lambda n: f"Game {n}")
    language = "EN"
    category = "Puzzle"


class GameSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GameSession

    game = factory.SubFactory(GameFactory)

    @factory.lazy_attribute
    def start_datetime(self):
        return make_aware(datetime(2025, 1, 15))

    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if create and extracted:
            for user in extracted:
                self.participants.add(user)


class GameResultsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GameResults

    game_session = factory.SubFactory(GameSessionFactory)
    score = 100
    is_completed = True
