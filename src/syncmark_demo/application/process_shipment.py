import asyncio

from syncmark_demo.domain.models import Shipment, ShipmentStatus, ValidationIssue
from syncmark_demo.domain.ports import CatalogGateway, LabelGenerator, ShipmentRepository


class ProcessShipment:
    def __init__(self, repository: ShipmentRepository, gateway: CatalogGateway, labels: LabelGenerator) -> None:
        self.repository, self.gateway, self.labels = repository, gateway, labels

    async def execute(self, shipment_id: str) -> Shipment:
        shipment = self.repository.get(shipment_id)
        if shipment is None:
            raise LookupError("shipment not found")
        if shipment.status is ShipmentStatus.VALIDATED:
            shipment.transition_to(ShipmentStatus.PROCESSING)
        if shipment.status is not ShipmentStatus.PROCESSING:
            return shipment
        try:
            for item in shipment.items:
                record = await self._lookup(item.gtin)
                if not record["active"] or record["category"] != item.category:
                    raise ValueError("catalogue_mismatch")
            shipment.label_urls = [self.labels.generate(shipment.id)]
            shipment.transition_to(ShipmentStatus.COMPLETED)
        except (TimeoutError, ValueError) as error:
            shipment.issues.append(ValidationIssue(code=str(error), field="catalog", row=None, message="Synthetic catalogue processing failed"))
            shipment.transition_to(ShipmentStatus.FAILED)
        self.repository.save(shipment)
        return shipment

    async def _lookup(self, gtin: str) -> dict[str, str | bool]:
        for attempt in range(3):
            try:
                return await self.gateway.lookup(gtin)
            except TimeoutError:
                if attempt == 2:
                    raise
                await asyncio.sleep(0)
        raise RuntimeError("unreachable")
