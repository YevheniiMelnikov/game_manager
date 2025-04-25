import os
import json
import random

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from apps.games.models import Company, Game, GameSession, GameResults

FIXTURES_DIR = os.path.join("games", "fixtures")
os.makedirs(FIXTURES_DIR, exist_ok=True)

User = get_user_model()

ROLE_CHOICES = ["SuperAdmin", "CompanyAdmin", "Participant"]
LANGUAGES = ["EN", "RU", "DE"]
CATEGORIES = ["Action", "Puzzle", "Strategy"]
SESSION_COUNT = 100
USER_COUNT = 10
GAME_COUNT = 10
COMPANY_COUNT = 5


class Command(BaseCommand):
    help = "Generate test data fixtures for the project"

    def handle(self, *args, **options):
        fixtures = []
        companies = []
        Company.objects.filter(name__startswith="Company").delete()
        for i in range(1, COMPANY_COUNT + 1):
            company = Company.objects.create(name=f"Company {i}")
            companies.append(company)
            fixtures.append(
                {
                    "model": "games.company",
                    "pk": company.pk,
                    "fields": {"name": company.name},
                }
            )

        users = []
        for i in range(1, USER_COUNT + 1):
            role = random.choice(ROLE_CHOICES)
            company = random.choice(companies) if role == "CompanyAdmin" else None

            user = User.objects.create_user(
                username=f"user{i}",
                password="pbkdf2_sha256$260000$dummyhash",
                is_active=True,
                role=role,
                company=company,
            )
            users.append(user)

            fixtures.append(
                {
                    "model": "games.customuser",
                    "pk": user.pk,
                    "fields": {
                        "username": user.username,
                        "password": user.password,
                        "is_active": user.is_active,
                        "role": user.role,
                        "company": company.pk if company else None,
                    },
                }
            )

        games = []
        for i in range(1, GAME_COUNT + 1):
            game = Game.objects.create(
                name=f"Game {i}",
                language=random.choice(LANGUAGES),
                category=random.choice(CATEGORIES),
            )
            games.append(game)
            fixtures.append(
                {
                    "model": "games.game",
                    "pk": game.pk,
                    "fields": {
                        "name": game.name,
                        "language": game.language,
                        "category": game.category,
                    },
                }
            )

        for _ in range(SESSION_COUNT):
            game = random.choice(games)
            session = GameSession.objects.create(
                game=game,
                start_datetime=now(),
            )

            participant_ids = random.sample([u.pk for u in users], k=random.randint(1, 5))
            session.participants.set(participant_ids)

            fixtures.append(
                {
                    "model": "games.gamesession",
                    "pk": session.pk,
                    "fields": {
                        "game": game.pk,
                        "start_datetime": session.start_datetime.isoformat(),
                        "status": session.status,
                        "participants": participant_ids,
                    },
                }
            )

            GameResults.objects.create(
                game_session=session,
                score=random.randint(0, 1000),
                is_completed=random.choice([True, False]),
            )

            fixtures.append(
                {
                    "model": "games.gamesession",
                    "pk": session.pk,
                    "fields": {
                        "game": game.pk,
                        "start_datetime": session.start_datetime.isoformat(),
                        "status": session.status,
                        "participants": participant_ids,
                    },
                }
            )

        out_path = os.path.join(FIXTURES_DIR, "test_data.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(fixtures, f, indent=2, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"Fixtures generated successfully: {out_path}"))
