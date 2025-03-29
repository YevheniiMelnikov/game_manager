import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from games.models import Company, Participant, Game, GameSession, GameResults
from django.utils.timezone import now
import json
import os

FIXTURES_DIR = "games/fixtures/"
os.makedirs(FIXTURES_DIR, exist_ok=True)


class Command(BaseCommand):
    help = "Generate test data fixtures for the project"

    def handle(self, *args, **kwargs):
        fixtures = []

        companies = []
        for i in range(5):
            company = Company.objects.create(name=f"Company {i + 1}")
            companies.append(company)
            fixtures.append({"model": "games.company", "pk": company.id, "fields": {"name": company.name}})

        participants = []
        for i in range(10):
            user = User.objects.create(username=f"user{i + 1}")
            role = random.choice(["SuperAdmin", "CompanyAdmin", "Participant"])
            company = random.choice(companies) if role == "CompanyAdmin" else None
            participant = Participant.objects.create(user=user, role=role, company=company)
            participants.append(participant)
            fixtures.append(
                {
                    "model": "auth.user",
                    "pk": user.id,
                    "fields": {
                        "username": user.username,
                        "password": "pbkdf2_sha256$260000$dummyhash",
                        "is_active": True,
                    },
                }
            )
            fixtures.append(
                {
                    "model": "games.participant",
                    "pk": participant.id,
                    "fields": {"user": user.id, "role": participant.role, "company": company.id if company else None},
                }
            )

        games = []
        for i in range(10):
            game = Game.objects.create(
                name=f"Game {i + 1}",
                language=random.choice(["EN", "RU", "DE"]),
                category=random.choice(["Action", "Puzzle", "Strategy"]),
            )
            games.append(game)
            fixtures.append(
                {
                    "model": "games.game",
                    "pk": game.id,
                    "fields": {"name": game.name, "language": game.language, "category": game.category},
                }
            )

        for i in range(100):
            game = random.choice(games)
            session = GameSession.objects.create(game=game, start_datetime=now())
            user_ids = [participant.user.id for participant in participants]
            selected_user_ids = random.sample(user_ids, k=random.randint(1, 5))
            session.participants.set(selected_user_ids)
            fixtures.append(
                {
                    "model": "games.gamesession",
                    "pk": session.id,
                    "fields": {
                        "game": session.game.id,
                        "start_datetime": session.start_datetime.isoformat(),
                        "participants": selected_user_ids,
                    },
                }
            )

            result = GameResults.objects.create(
                game_session=session,
                score=random.randint(0, 1000),
                status=random.choice(["Created", "InProgress", "Finished", "Filed"]),
                is_completed=random.choice([True, False]),
            )
            fixtures.append(
                {
                    "model": "games.gameresults",
                    "pk": result.id,
                    "fields": {
                        "game_session": session.id,
                        "score": result.score,
                        "status": result.status,
                        "is_completed": result.is_completed,
                    },
                }
            )

        with open(os.path.join(FIXTURES_DIR, "test_data.json"), "w") as f:
            json.dump(fixtures, f, indent=4)

        self.stdout.write(self.style.SUCCESS("Fixtures generated successfully!"))
