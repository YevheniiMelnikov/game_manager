# GameManager

GameManager is a Django-based platform for managing multiplayer cognitive games, user sessions, and performance reports. It features user roles, session statistics, Celery-powered background tasks, and both ORM and raw SQL support for reporting.

---

## 🚀 Features

- User registration (via API and web interface)
- Role-based user management (`SuperAdmin`, `CompanyAdmin`, `Participant`)
- Game and session tracking with real-time status
- Celery tasks for:
  - Monthly reports on game participation
  - Session ratio metrics
- Dual data access via Django ORM and raw SQL
- Minimalist web registration UI
- PostgreSQL and SQLite support

---

## 🧰 Requirements

- Docker
- Docker Compose
- Python 3.11+ (for local development without containers)

---

## 🛠 Installation and Running

### Step 1: Environment Setup

1. Copy the example env file and modify as needed:

    ```bash
    cp .env.example .env
    ```

### Step 2: Build and Start Services

```bash
docker compose build
docker compose up
```

---

## 🧪 Running Tests

```bash
docker compose exec web pytest
```

Test suite includes coverage for:
- Celery task reports (ORM + raw SQL)
- Game and session models
- User roles and registration

---

## 📊 Background Tasks

Powered by Celery & django-celery-beat:

- `generate_monthly_reports`: Aggregates participant scores for each game in the previous month
- `generate_session_ratio`: Calculates session completion/failure rates

Raw SQL alternatives included for performance testing and analytics accuracy comparison.

---

## 🌐 Web Interface

Minimalist web-based user registration is available at:

```
http://localhost:8000/register/
```

Useful for manually onboarding users with specific roles (SuperAdmin, CompanyAdmin, etc.)

---

## 📁 Project Structure

```
game_management/     # Django settings and root config
games/               # Main app with models, tasks, views
    └── templates/
        └── games/
            ├── register.html
            └── register_success.html
reports/             # Celery task output as JSON
```

---

## 🧑‍💻 Development Notes

- You can use ORM or raw SQL to fetch report data.
- SQL transactions are used where data integrity is critical (e.g., raw insertions during registration or analytics).
- Use Django admin panel or `/api/` routes for managing objects.

---

## ✅ Health Check

To verify the app is up:

```bash
curl http://localhost:8000/health/
```

Returns plain `OK` response.
