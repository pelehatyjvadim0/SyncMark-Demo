import asyncio

from syncmark_demo.application.process_shipment import ProcessShipment
from syncmark_demo.application.submit_shipment import SubmitShipment
from syncmark_demo.domain.models import Shipment, ShipmentStatus
from syncmark_demo.infrastructure.catalog import MockCatalogGateway
from syncmark_demo.infrastructure.memory import MemoryRepository, RecordingPublisher
from syncmark_demo.infrastructure.pdf import SyntheticLabelGenerator


def test_submit_is_idempotent_for_same_key() -> None:
    repository, publisher = MemoryRepository(), RecordingPublisher()
    shipment = Shipment("hash", [], [], ShipmentStatus.VALIDATED)
    repository.save(shipment)
    use_case = SubmitShipment(repository, publisher)
    assert use_case.execute(shipment.id, "demo").id == shipment.id
    use_case.execute(shipment.id, "demo")
    assert publisher.commands == [shipment.id]


def test_processor_retries_timeout_then_completes(tmp_path) -> None:
    from syncmark_demo.domain.models import NormalizedItem
    repository = MemoryRepository()
    shipment = Shipment("hash", [NormalizedItem(row=2, gtin="00012345678900", category="outer_wear", quantity=1, product_name="Demo jacket")], [], ShipmentStatus.VALIDATED)
    repository.save(shipment)
    processor = ProcessShipment(repository, MockCatalogGateway(transient_failures=1), SyntheticLabelGenerator(str(tmp_path)))
    result = asyncio.run(processor.execute(shipment.id))
    assert result.status is ShipmentStatus.COMPLETED
    assert result.label_urls == [f"/labels/{shipment.id}.pdf"]
