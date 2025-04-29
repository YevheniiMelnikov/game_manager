import json
import random
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from apps.games.models import Company, Game, GameSession, GameResults

User = get_user_model()
FIXTURES_DIR = Path("games/fixtures")
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)


class Command(BaseCommand):
    help = "Generate test data fixtures for the project"

    SESSION_COUNT = 100
    USER_COUNT = 10
    GAME_COUNT = 10
    COMPANY_COUNT = 5

    ROLE_CHOICES = ["SuperAdmin", "CompanyAdmin", "Participant"]
    LANGUAGES = ["EN", "RU", "DE"]
    CATEGORIES = ["Action", "Puzzle", "Strategy"]

    def handle(self, *args, **options):
        fixtures = []

        # Companies
        Company.objects.filter(name__startswith="Company").delete()
        companies = [Company.objects.create(name=f"Company {i}") for i in range(1, self.COMPANY_COUNT + 1)]
        fixtures += [{"model": "games.company", "pk": c.pk, "fields": {"name": c.name}} for c in companies]

        # Users
        users = []
        for i in range(1, self.USER_COUNT + 1):
            role = random.choice(self.ROLE_CHOICES)
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
                    "model": "users.user",
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

        # Games
        games = [
            Game.objects.create(
                name=f"Game {i}",
                language=random.choice(self.LANGUAGES),
                category=random.choice(self.CATEGORIES),
            )
            for i in range(1, self.GAME_COUNT + 1)
        ]
        fixtures += [
            {
                "model": "games.game",
                "pk": g.pk,
                "fields": {
                    "name": g.name,
                    "language": g.language,
                    "category": g.category,
                },
            }
            for g in games
        ]

        # Sessions and Results
        for _ in range(self.SESSION_COUNT):
            game = random.choice(games)
            session = GameSession.objects.create(
                game=game,
                start_datetime=now(),
            )
            participant_ids = random.sample([u.pk for u in users], k=random.randint(1, min(5, len(users))))
            session.participants.set(participant_ids)

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

        out_path = FIXTURES_DIR / "test_data.json"
        out_path.write_text(json.dumps(fixtures, indent=2, ensure_ascii=False), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(f"Fixtures generated successfully: {out_path}"))
