# Gym Management API

REST API for managing gym memberships, training sessions, and reservations.

## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Framework    | FastAPI 0.115                        |
| ORM          | SQLAlchemy 2.0 (async)              |
| DB Driver    | asyncpg (PostgreSQL)                |
| Migrations   | Alembic                             |
| Validation   | Pydantic v2                         |
| Auth         | JWT (python-jose, HS256)            |
| Passwords    | bcrypt                              |
| Tests        | pytest-asyncio + SQLite in-memory   |
| Container    | Docker + docker-compose             |

## Quick Start

```bash
# 1. Start the database
docker compose up -d db

# 2. Set up virtual environment
cd api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env if needed

# 5. Run migrations
alembic upgrade head

# 6. Seed sample data
python -m app.seed

# 7. Start the server
uvicorn app.main:app --reload
```

API is available at: http://localhost:8000  
Swagger UI: http://localhost:8000/docs

## Project Structure

```
gym_app/
├── docker-compose.yml
├── .gitignore
└── api/
    ├── requirements.txt
    ├── pyproject.toml
    ├── alembic.ini
    ├── .env.example
    ├── alembic/
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions/
    │       └── 001_init_gym_tables.py
    ├── app/
    │   ├── main.py
    │   ├── seed.py
    │   ├── core/
    │   │   ├── config.py
    │   │   ├── database.py
    │   │   ├── deps.py
    │   │   ├── errors.py
    │   │   ├── jwt.py
    │   │   ├── logging.py
    │   │   └── security.py
    │   ├── models/
    │   │   ├── user.py
    │   │   ├── membership.py
    │   │   ├── training.py
    │   │   └── reservation.py
    │   ├── repositories/
    │   │   ├── user_repo.py
    │   │   ├── membership_repo.py
    │   │   ├── training_repo.py
    │   │   └── reservation_repo.py
    │   ├── schemas/
    │   │   ├── auth.py
    │   │   ├── user.py
    │   │   ├── membership.py
    │   │   ├── training.py
    │   │   └── reservation.py
    │   ├── services/
    │   │   ├── auth_service.py
    │   │   ├── user_service.py
    │   │   ├── membership_service.py
    │   │   ├── training_service.py
    │   │   └── reservation_service.py
    │   └── routers/
    │       ├── health.py
    │       ├── auth.py
    │       ├── users.py
    │       ├── memberships.py
    │       ├── trainings.py
    │       └── reservations.py
    └── tests/
        ├── conftest.py
        ├── test_auth.py
        ├── test_users.py
        ├── test_memberships.py
        ├── test_trainings.py
        └── test_reservations.py
```

## Architecture

```
HTTP Request
     │
     ▼
  Router          (app/routers/)      — validates input, calls service
     │
     ▼
  Service         (app/services/)     — business logic, rules, errors
     │
     ▼
  Repository      (app/repositories/) — DB queries (SQLAlchemy)
     │
     ▼
  Model           (app/models/)       — ORM table definitions
     │
     ▼
  PostgreSQL
```

## Data Models

| Table         | Key Fields                                                              |
|---------------|-------------------------------------------------------------------------|
| `users`       | id, username (unique), password_hash, role (admin/trainer/member), is_active |
| `memberships` | id, user_id, start_date, end_date, status (active/cancelled)            |
| `trainings`   | id, trainer_id, title, scheduled_at, duration_minutes, max_capacity, status |
| `reservations`| id, training_id, user_id, status (confirmed/cancelled), UniqueConstraint |

## Roles

| Role      | Permissions                                                    |
|-----------|----------------------------------------------------------------|
| `admin`   | Full access to all resources                                   |
| `trainer` | Create/manage own training sessions, cancel reservations       |
| `member`  | View trainings, make/cancel own reservations (active membership required) |

## API Endpoints

### Health
| Method | Path      | Auth | Description  |
|--------|-----------|------|--------------|
| GET    | /health   | —    | Health check |

### Auth
| Method | Path          | Auth | Description             |
|--------|---------------|------|-------------------------|
| POST   | /auth/login   | —    | Login, get tokens       |
| POST   | /auth/refresh | —    | Refresh access token    |
| GET    | /auth/me      | JWT  | Current user info       |

### Users
| Method | Path              | Auth          | Description         |
|--------|-------------------|---------------|---------------------|
| POST   | /users/register   | —             | Register as member  |
| GET    | /users            | admin         | List all users      |
| GET    | /users/{id}       | self or admin | Get user by id      |

### Memberships
| Method | Path                        | Auth         | Description                 |
|--------|-----------------------------|--------------|-----------------------------|
| GET    | /memberships                | JWT          | List memberships (own/all)  |
| POST   | /memberships                | admin        | Create membership for user  |
| GET    | /memberships/{id}           | self or admin| Get membership              |
| PATCH  | /memberships/{id}/cancel    | self or admin| Cancel membership           |

### Trainings
| Method | Path                         | Auth             | Description              |
|--------|------------------------------|------------------|--------------------------|
| GET    | /trainings                   | JWT              | List all trainings       |
| POST   | /trainings                   | admin, trainer   | Create training session  |
| GET    | /trainings/{id}              | JWT              | Get training details     |
| PATCH  | /trainings/{id}              | admin, owner     | Update training info     |
| PATCH  | /trainings/{id}/start        | admin, owner     | Start training           |
| PATCH  | /trainings/{id}/complete     | admin, owner     | Complete training        |
| PATCH  | /trainings/{id}/cancel       | admin, owner     | Cancel training          |

### Reservations
| Method | Path                                            | Auth              | Description            |
|--------|-------------------------------------------------|-------------------|------------------------|
| GET    | /trainings/{id}/reservations                    | JWT               | List reservations      |
| POST   | /trainings/{id}/reservations                    | member            | Make reservation       |
| DELETE | /trainings/{id}/reservations/{rid}              | self, trainer, admin | Cancel reservation  |

## Business Rules

- Members must have an **active membership** to make a reservation
- A membership is active when `status == "active"` AND `end_date >= today`
- Training capacity: max `max_capacity` confirmed reservations per training
- Only one reservation per member per training (unique constraint)
- Reservations only allowed for `scheduled` trainings
- Training status transitions: `scheduled → in_progress → completed`, `scheduled/in_progress → cancelled`
- Admin can manage all resources; trainers manage their own sessions

## Migrations

```bash
# Apply all migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "description"
```

## Seed Data

After running `python -m app.seed`:

| Username  | Password  | Role    | Membership        |
|-----------|-----------|---------|-------------------|
| admin     | admin123  | admin   | —                 |
| trainer1  | pass123   | trainer | —                 |
| member1   | pass123   | member  | active (30 days)  |
| member2   | pass123   | member  | —                 |

## Running Tests

```bash
cd api
pytest -v
```

Tests use SQLite in-memory. Each test gets a clean database (full isolation).

## Useful Commands

```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run tests with coverage
pytest --tb=short -v

# Check code style
ruff check app/
```
