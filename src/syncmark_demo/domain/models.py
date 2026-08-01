from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


class ShipmentStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ValidationIssue(BaseModel):
    code: str
    field: str
    row: int | None
    message: str
    severity: Severity = Severity.ERROR


@dataclass(frozen=True)
class RawItem:
    row: int
    gtin: str | None
    category: str | None
    quantity: str | int | None
    product_name: str | None


class NormalizedItem(BaseModel):
    row: int
    gtin: str
    category: str
    quantity: int
    product_name: str


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[ValidationIssue]
    normalized_items: list[NormalizedItem]


@dataclass
class Shipment:
    content_hash: str
    items: list[NormalizedItem]
    issues: list[ValidationIssue]
    status: ShipmentStatus
    id: str = field(default_factory=lambda: str(uuid4()))
    label_urls: list[str] = field(default_factory=list)
    submitted_keys: set[str] = field(default_factory=set)

    def transition_to(self, target: ShipmentStatus) -> None:
        allowed = {
            ShipmentStatus.DRAFT: {ShipmentStatus.VALIDATED},
            ShipmentStatus.VALIDATED: {ShipmentStatus.PROCESSING},
            ShipmentStatus.PROCESSING: {ShipmentStatus.COMPLETED, ShipmentStatus.FAILED},
        }
        if target not in allowed.get(self.status, set()):
            raise ValueError(f"invalid state transition: {self.status} -> {target}")
        self.status = target
