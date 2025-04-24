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

---

## 📊 Background Tasks

Powered by Celery & django-celery-beat:

- `generate_monthly_reports`: Aggregates participant scores for each game in the previous month
- `generate_session_ratio`: Calculates session completion/failure rates

---

## 🌐 Web Interface

**Web-based user registration is available at:**

```
http://localhost:8080/register/
```
![Registration page](readme%20images/register.png)

**Admin panel is available at:**

```
http://localhost:8080/admin/
```
*Note: Use the credentials provided in the `.env` file.*
![Django admin](readme%20images/admin.png)

**Docs are available at:**

```
http://localhost:8080/docs/
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
