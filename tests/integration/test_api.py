from io import BytesIO

from fastapi.testclient import TestClient
from openpyxl import Workbook

from syncmark_demo.api import create_app


def workbook_bytes() -> bytes:
    book = Workbook(); sheet = book.active
    assert sheet is not None
    sheet.append(["GTIN", "category", "quantity", "product_name"])
    sheet.append(["00012345678900", "outer wear", 1, "Demo jacket"])
    output = BytesIO(); book.save(output)
    return output.getvalue()


def test_import_and_submit_are_idempotent() -> None:
    client = TestClient(create_app())
    upload = {"file": ("synthetic.xlsx", workbook_bytes(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    first = client.post("/shipments/import", files=upload).json()
    second = client.post("/shipments/import", files=upload).json()
    assert first["id"] == second["id"]
    response = client.post(f"/shipments/{first['id']}/submit", headers={"Idempotency-Key": "demo-key"})
    assert response.status_code == 202
    assert client.get("/health").json()["api"] == "ok"
