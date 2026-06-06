from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "dev"
    DATABASE_URL: str = "postgresql+asyncpg://gym_user:gym_pass@localhost:5432/gym_db"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ISSUER: str = "gym-app"
    # Origin-i kojima je dopusten CORS (zarezom odvojeni).
    # Dev: Vite na 5173. Produkcija: dodaj URL deployanog frontenda.
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
