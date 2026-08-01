from faststream.rabbit import RabbitBroker


class FastStreamPublisher:
    def __init__(self, broker: RabbitBroker) -> None:
        self.broker = broker

    async def publish(self, shipment_id: str) -> None:
        await self.broker.publish({"shipment_id": shipment_id}, queue="shipment.commands")

    async def ping(self) -> None:
        if not await self.broker.ping(timeout=1):
            raise ConnectionError("RabbitMQ is unavailable")
