from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import AppError, app_error_handler
from app.core.logging import setup_logging
from app.routers import auth, health, memberships, reservations, trainings, users


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="Gym Management API",
        version="1.0.0",
        description="REST API for gym membership, training sessions, and reservations",
    )

    # CORS: dopusti frontendu (na drugom origin-u) da zove API iz browsera.
    # Origin-i se citaju iz CORS_ORIGINS env varijable (zarezom odvojeni).
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppError, app_error_handler)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(memberships.router)
    app.include_router(trainings.router)
    app.include_router(
        reservations.router,
        prefix="/trainings/{training_id}/reservations",
    )

    return app


app = create_app()
