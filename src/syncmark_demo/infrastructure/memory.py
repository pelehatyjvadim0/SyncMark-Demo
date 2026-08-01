from syncmark_demo.domain.models import Shipment


class MemoryRepository:
    def __init__(self) -> None:
        self.shipments: dict[str, Shipment] = {}

    async def by_hash(self, content_hash: str) -> Shipment | None:
        return next((s for s in self.shipments.values() if s.content_hash == content_hash), None)

    async def get(self, shipment_id: str) -> Shipment | None:
        return self.shipments.get(shipment_id)

    async def save(self, shipment: Shipment) -> None:
        self.shipments[shipment.id] = shipment


class RecordingPublisher:
    def __init__(self) -> None:
        self.commands: list[str] = []

    async def publish(self, shipment_id: str) -> None:
        self.commands.append(shipment_id)
