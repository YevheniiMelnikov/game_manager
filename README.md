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

## ✅ Health Check

To verify the app is up:

```bash
curl http://localhost:8000/health/
```

Returns plain `OK` response.

---

## 🧱 Taskfile Commands

The project uses [Taskfile](https://taskfile.dev/) to automate common tasks:

| Task         | Description                                  |
|--------------|----------------------------------------------|
| migrate      | Run database migrations                     |
| run          | Build and run all services (docker compose) |
| lint         | Run linters (ruff + mypy)                   |
| format       | Format the codebase                         |
| update       | Update Python dependencies                  |
| test         | Run tests with pytest                       |
| pre-commit   | Run all pre-commit hooks                    |
| generate     | Generate and load test data fixtures        |

Example:

```bash
task lint
```

---

## 🧹 Pre-Commit Hooks

The project uses [pre-commit](https://pre-commit.com/) to ensure code quality automatically on commits.

Installed hooks:

- `ruff` — Python linter and formatter
- `mypy` — Static type checker
- `pytest` — Run tests
- `check-yaml`, `end-of-file-fixer`, `trailing-whitespace` — Miscellaneous file checks
- `uv-lock` — Sync Python dependencies lockfile

Install and run manually if needed:

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

---

## 🚀 Deploy to Server

1. Make sure `Docker` and `Docker Compose` are installed on the server.
2. Copy the project files to the server.
3. Create and configure `.env` file.
4. Run the project:

```bash
docker compose up -d --build
```

5. (Optional) Set up SSL certificates and a reverse proxy if needed (Nginx config is prepared).

The app will be available at:

- API: `http://your-server:8000/`
- Admin panel: `http://your-server:8080/admin/`
- Docs: `http://your-server:8080/docs/`
