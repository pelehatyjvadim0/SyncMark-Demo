import re

from .models import NormalizedItem, RawItem, ValidationIssue, ValidationResult

ALLOWED_CATEGORIES = {"outer_wear", "footwear", "accessories"}


def _category(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def validate_rows(rows: list[RawItem]) -> ValidationResult:
    issues: list[ValidationIssue] = []
    items: list[NormalizedItem] = []
    seen: set[str] = set()
    for raw in rows:
        error_count = len(issues)
        gtin = (raw.gtin or "").strip()
        category = _category(raw.category or "")
        name = (raw.product_name or "").strip()
        try:
            quantity = int(str(raw.quantity).strip())
        except (TypeError, ValueError):
            quantity = 0
        if not gtin.isdigit() or len(gtin) not in {13, 14}:
            issues.append(ValidationIssue(code="invalid_gtin", field="gtin", row=raw.row, message="GTIN must contain 13 or 14 digits"))
        else:
            gtin = gtin.zfill(14)
            if gtin in seen:
                issues.append(ValidationIssue(code="duplicate_gtin", field="gtin", row=raw.row, message="GTIN is duplicated"))
            seen.add(gtin)
        if not name:
            issues.append(ValidationIssue(code="required", field="product_name", row=raw.row, message="Product name is required"))
        if category not in ALLOWED_CATEGORIES:
            issues.append(ValidationIssue(code="unknown_category", field="category", row=raw.row, message="Category is unsupported"))
        if quantity <= 0:
            issues.append(ValidationIssue(code="invalid_quantity", field="quantity", row=raw.row, message="Quantity must be positive"))
        if len(issues) == error_count:
            items.append(NormalizedItem(row=raw.row, gtin=gtin, category=category, quantity=quantity, product_name=name))
    return ValidationResult(is_valid=not issues, errors=issues, normalized_items=items)
