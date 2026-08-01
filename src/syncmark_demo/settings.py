from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    database_url: str = getenv("SYNCMARK_DEMO_DATABASE_URL", "postgresql+asyncpg://demo:demo@postgres:5432/syncmark_demo")
    rabbit_url: str = getenv("SYNCMARK_DEMO_RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/")
    label_dir: str = getenv("SYNCMARK_DEMO_LABEL_DIR", "generated-labels")
