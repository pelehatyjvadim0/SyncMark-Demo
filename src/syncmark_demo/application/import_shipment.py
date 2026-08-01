from hashlib import sha256

from syncmark_demo.domain.models import Shipment, ShipmentStatus
from syncmark_demo.domain.ports import ShipmentRepository, SpreadsheetReader
from syncmark_demo.domain.validation import validate_rows


class ImportShipment:
    def __init__(self, repository: ShipmentRepository, reader: SpreadsheetReader) -> None:
        self.repository, self.reader = repository, reader

    async def execute(self, filename: str, content: bytes) -> Shipment:
        if not filename.endswith(".xlsx"):
            raise ValueError("only .xlsx uploads are supported")
        digest = sha256(content).hexdigest()
        if existing := await self.repository.by_hash(digest):
            return existing
        rows = self.reader.read(content)
        result = validate_rows(rows)
        status = ShipmentStatus.VALIDATED if result.is_valid else ShipmentStatus.DRAFT
        shipment = Shipment(digest, result.normalized_items, result.errors, status)
        await self.repository.save(shipment)
        return shipment
