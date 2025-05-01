from pathlib import Path
import json
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from apps.games.models import Company, Game, GameSession, GameResults

User = get_user_model()
FIXTURES_DIR = Path("apps/games/fixtures")
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

        today = now()
        start_of_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        end_of_last_month = today.replace(day=1) - timedelta(seconds=1)

        Company.objects.filter(name__startswith="Company").delete()
        companies = []
        for i in range(1, self.COMPANY_COUNT + 1):
            company = Company.objects.create(name=f"Company {i}")
            companies.append(company)
            fixtures.append({
                "model": "games.company",
                "pk": company.pk,
                "fields": {
                    "name": company.name,
                    "created_at": company.created_at.isoformat(),
                    "updated_at": company.updated_at.isoformat(),
                },
            })

        users = []
        for i in range(1, self.USER_COUNT + 1):
            role = random.choice(self.ROLE_CHOICES)
            company = random.choice(companies) if role == "CompanyAdmin" else None
            user = User.objects.create_user(
                username=f"user{i}",
                password="pass123",
                is_active=True,
                role=role,
                company=company,
            )
            users.append(user)
            fixtures.append({
                "model": "users.user",
                "pk": user.pk,
                "fields": {
                    "username": user.username,
                    "password": user.password,
                    "is_active": user.is_active,
                    "role": user.role,
                    "company": company.pk if company else None,
                    "created": user.created.isoformat(),
                    "updated": user.updated.isoformat(),
                },
            })

        games = []
        for i in range(1, self.GAME_COUNT + 1):
            game = Game.objects.create(
                name=f"Game {i}",
                language=random.choice(self.LANGUAGES),
                category=random.choice(self.CATEGORIES),
            )
            games.append(game)
            fixtures.append({
                "model": "games.game",
                "pk": game.pk,
                "fields": {
                    "name": game.name,
                    "language": game.language,
                    "category": game.category,
                    "created_at": game.created_at.isoformat(),
                    "updated_at": game.updated_at.isoformat(),
                },
            })

        for _ in range(self.SESSION_COUNT):
            game = random.choice(games)
            start_time = start_of_last_month + timedelta(
                days=random.randint(0, (end_of_last_month - start_of_last_month).days),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            session = GameSession.objects.create(
                game=game,
                start_datetime=start_time,
            )
            participants = random.sample(users, k=random.randint(1, min(5, len(users))))
            session.participants.set(participants)

            GameResults.objects.create(
                game_session=session,
                score=random.randint(0, 1000),
                is_completed=random.choice([True, False]),
            )

            fixtures.append({
                "model": "games.gamesession",
                "pk": session.pk,
                "fields": {
                    "game": game.pk,
                    "start_datetime": session.start_datetime.isoformat(),
                    "status": session.status,
                    "participants": [u.pk for u in participants],
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                },
            })

        out_path = FIXTURES_DIR / "test_data.json"
        out_path.write_text(json.dumps(fixtures, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(f"Fixtures generated successfully: {out_path}"))
        self.stdout.write(
            self.style.SUCCESS(f"Users: {len(users)} | Games: {len(games)} | Sessions: {self.SESSION_COUNT}")
        )
