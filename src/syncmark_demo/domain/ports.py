from typing import Protocol

from .models import RawItem, Shipment


class SpreadsheetReader(Protocol):
    def read(self, content: bytes) -> list[RawItem]: ...


class LabelGenerator(Protocol):
    def generate(self, shipment_id: str) -> str: ...


class ShipmentRepository(Protocol):
    def by_hash(self, content_hash: str) -> Shipment | None: ...
    def get(self, shipment_id: str) -> Shipment | None: ...
    def save(self, shipment: Shipment) -> None: ...


class CommandPublisher(Protocol):
    def publish(self, shipment_id: str) -> None: ...


class CatalogGateway(Protocol):
    async def lookup(self, gtin: str) -> dict[str, str | bool]: ...
