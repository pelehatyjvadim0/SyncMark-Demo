import asyncio

from faststream.rabbit import RabbitBroker

from syncmark_demo.application.process_shipment import ProcessShipment
from syncmark_demo.infrastructure.catalog import MockCatalogGateway
from syncmark_demo.infrastructure.database import AsyncSqlAlchemyRepository
from syncmark_demo.infrastructure.pdf import SyntheticLabelGenerator
from syncmark_demo.settings import Settings

settings = Settings()
broker = RabbitBroker(settings.rabbit_url)
repository = AsyncSqlAlchemyRepository(settings.database_url)
processor = ProcessShipment(repository, MockCatalogGateway(), SyntheticLabelGenerator(settings.label_dir))


@broker.subscriber("shipment.commands")
async def process_command(message: dict[str, str]) -> None:
    await repository.create_schema()
    await processor.execute(message["shipment_id"])


if __name__ == "__main__":
    async def run() -> None:
        await broker.start()
        await asyncio.Future()

    asyncio.run(run())
