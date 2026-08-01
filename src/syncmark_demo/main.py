from faststream.rabbit import RabbitBroker

from syncmark_demo.api import create_app
from syncmark_demo.infrastructure.database import AsyncSqlAlchemyRepository
from syncmark_demo.infrastructure.queue import FastStreamPublisher
from syncmark_demo.settings import Settings

settings = Settings()
repository = AsyncSqlAlchemyRepository(settings.database_url)
broker = RabbitBroker(settings.rabbit_url)
app = create_app(repository, FastStreamPublisher(broker))


@app.on_event("startup")
async def prepare_dependencies() -> None:
    await broker.connect()
