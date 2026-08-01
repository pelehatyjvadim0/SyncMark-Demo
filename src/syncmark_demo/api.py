from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from pydantic import BaseModel

from syncmark_demo.application.import_shipment import ImportShipment
from syncmark_demo.application.submit_shipment import SubmitShipment
from syncmark_demo.domain.models import Shipment
from syncmark_demo.domain.ports import CommandPublisher, ShipmentRepository
from syncmark_demo.infrastructure.catalog import MockCatalogGateway
from syncmark_demo.infrastructure.memory import MemoryRepository, RecordingPublisher
from syncmark_demo.infrastructure.pdf import SyntheticLabelGenerator
from syncmark_demo.infrastructure.xlsx import OpenpyxlReader


class ShipmentResponse(BaseModel):
    id: str
    status: str
    item_count: int
    errors: list[dict]
    label_urls: list[str]


def _view(shipment: Shipment) -> ShipmentResponse:
    return ShipmentResponse(id=shipment.id, status=shipment.status, item_count=len(shipment.items), errors=[issue.model_dump() for issue in shipment.issues], label_urls=shipment.label_urls)


def create_app(repository: ShipmentRepository | None = None, publisher: CommandPublisher | None = None) -> FastAPI:
    repository = repository or MemoryRepository()
    publisher = publisher or RecordingPublisher()
    importer = ImportShipment(repository, OpenpyxlReader())
    submitter = SubmitShipment(repository, publisher)
    app = FastAPI(title="SyncMark Demo", version="0.1.0")
    app.state.services = {"repository": repository, "publisher": publisher, "importer": importer, "submitter": submitter, "gateway": MockCatalogGateway(), "labels": SyntheticLabelGenerator()}

    @app.post("/shipments/import", response_model=ShipmentResponse)
    async def import_shipment(file: UploadFile = File(...)) -> ShipmentResponse:  # noqa: B008
        try:
            return _view(await importer.execute(file.filename or "", await file.read()))
        except ValueError as error:
            raise HTTPException(422, detail={"code": str(error)}) from error

    @app.post("/shipments/{shipment_id}/submit", response_model=ShipmentResponse, status_code=202)
    async def submit_shipment(shipment_id: str, idempotency_key: str = Header(..., alias="Idempotency-Key")) -> ShipmentResponse:
        try:
            return _view(await submitter.execute(shipment_id, idempotency_key))
        except LookupError as error:
            raise HTTPException(404, detail={"code": "not_found"}) from error
        except ValueError as error:
            raise HTTPException(409, detail={"code": str(error)}) from error

    @app.get("/shipments/{shipment_id}", response_model=ShipmentResponse)
    async def get_shipment(shipment_id: str) -> ShipmentResponse:
        shipment = await repository.get(shipment_id)
        if shipment is None:
            raise HTTPException(404, detail={"code": "not_found"})
        return _view(shipment)

    @app.get("/health")
    async def health() -> dict[str, str]:
        database = "ok" if hasattr(repository, "engine") else "in_memory"
        queue = "ok" if publisher.__class__.__name__ == "FastStreamPublisher" else "in_memory"
        return {"api": "ok", "postgresql": database, "rabbitmq": queue}

    return app
