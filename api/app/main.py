from fastapi import FastAPI

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
