from syncmark_demo.domain.models import Shipment, ShipmentStatus
from syncmark_demo.domain.ports import CommandPublisher, ShipmentRepository


class SubmitShipment:
    def __init__(self, repository: ShipmentRepository, publisher: CommandPublisher) -> None:
        self.repository, self.publisher = repository, publisher

    def execute(self, shipment_id: str, idempotency_key: str) -> Shipment:
        shipment = self.repository.get(shipment_id)
        if shipment is None:
            raise LookupError("shipment not found")
        if idempotency_key in shipment.submitted_keys:
            return shipment
        if shipment.status is not ShipmentStatus.VALIDATED:
            raise ValueError("invalid_state")
        shipment.submitted_keys.add(idempotency_key)
        self.publisher.publish(shipment.id)
        self.repository.save(shipment)
        return shipment
