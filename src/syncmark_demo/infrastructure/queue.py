from faststream.rabbit import RabbitBroker


class FastStreamPublisher:
    def __init__(self, broker: RabbitBroker) -> None:
        self.broker = broker

    async def publish(self, shipment_id: str) -> None:
        await self.broker.publish({"shipment_id": shipment_id}, queue="shipment.commands")
