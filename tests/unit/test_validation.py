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
    assert {issue.code for issue in result.errors} == {"duplicate_gtin", "invalid_quantity"}


def test_validation_keeps_all_row_errors_and_valid_neighbours() -> None:
    result = validate_rows([
        RawItem(2, "bad", "unknown", 0, ""),
        RawItem(3, "00012345678900", "outer wear", 1, "Demo jacket"),
    ])
    assert {issue.code for issue in result.errors} == {"invalid_gtin", "unknown_category", "invalid_quantity", "required"}
    assert [item.row for item in result.normalized_items] == [3]


def test_validation_rejects_inactive_category() -> None:
    result = validate_rows([RawItem(2, "00012345678900", "inactive", 1, "Demo jacket")])
    assert result.errors[0].code == "unknown_category"


def test_shipment_disallows_completed_from_draft() -> None:
    shipment = Shipment("hash", [], [], ShipmentStatus.DRAFT)
    with pytest.raises(ValueError, match="invalid state transition"):
        shipment.transition_to(ShipmentStatus.COMPLETED)
