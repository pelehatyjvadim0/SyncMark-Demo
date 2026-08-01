import pytest

from syncmark_demo.domain.models import RawItem, Shipment, ShipmentStatus
from syncmark_demo.domain.validation import validate_rows


def test_validation_normalizes_gtin_and_category() -> None:
    result = validate_rows([RawItem(2, " 0001234567890 ", " Outer Wear ", "2", "Demo jacket")])
    assert result.is_valid
    assert result.normalized_items[0].gtin == "00001234567890"
    assert result.normalized_items[0].category == "outer_wear"


def test_validation_reports_duplicate_and_bad_quantity() -> None:
    result = validate_rows([RawItem(2, "00012345678900", "outer wear", 1, "A"), RawItem(3, "00012345678900", "outer wear", 0, "B")])
    assert {issue.code for issue in result.errors} == {"duplicate_gtin"}


def test_shipment_disallows_completed_from_draft() -> None:
    shipment = Shipment("hash", [], [], ShipmentStatus.DRAFT)
    with pytest.raises(ValueError, match="invalid state transition"):
        shipment.transition_to(ShipmentStatus.COMPLETED)
