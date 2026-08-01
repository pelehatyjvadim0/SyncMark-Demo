# SyncMark Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a clean-room, reproducible backend demo that imports a synthetic marking workbook and completes a shipment through a mocked asynchronous workflow.

**Architecture:** Pure domain models and validation rules sit behind application use cases and ports. FastAPI, SQLAlchemy/PostgreSQL, FastStream/RabbitMQ, XLSX parsing, the mock catalogue, and synthetic PDF generation are adapters.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy async, Alembic, FastStream, RabbitMQ, PostgreSQL, OpenPyXL, ReportLab, uv, pytest, Ruff, Pyright, Docker Compose.

## Global Constraints

- The repository remains clean-room: only synthetic source, fixtures, names, identifiers and docs may be committed.
- Python version floor is 3.12; public code has strict Ruff and Pyright checks.
- Domain/application modules must not import FastAPI, SQLAlchemy, OpenPyXL, FastStream, RabbitMQ, or ReportLab.
- Re-importing identical workbook bytes is idempotent; re-submitting with the same idempotency key is idempotent.
- Every behavior change uses a failing test, minimal implementation, scoped green test, and a Russian finished-step commit.

---

### Task 1: Bootstrap the public package and quality gates

**Files:** Create `pyproject.toml`, `.gitignore`, `.env.example`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `src/syncmark_demo/__init__.py`, `tests/unit/test_package.py`.

**Interfaces:** Produces `syncmark_demo.__version__ == "0.1.0"` and `uv run pytest`.

- [ ] **Step 1: Write a failing test**

```python
from syncmark_demo import __version__

def test_package_exposes_public_version() -> None:
    assert __version__ == "0.1.0"
```

- [ ] **Step 2: Run the scoped test**

Run: `uv run pytest tests/unit/test_package.py -q`
Expected: FAIL because package is absent.

- [ ] **Step 3: Add package metadata, tool configuration, ignored local data, CI, and version export**

- [ ] **Step 4: Verify the quality baseline**

Run: `uv run ruff check . && uv run pyright && uv run pytest -q`
Expected: exit 0.

- [ ] **Step 5: Commit**

`git commit -m 'Создана основа публичного backend demo'`

### Task 2: Define and test the domain validation layer

**Files:** Create `src/syncmark_demo/domain/models.py`, `src/syncmark_demo/domain/validation.py`, `src/syncmark_demo/domain/ports.py`, `tests/unit/test_validation.py`.

**Interfaces:** Produces `validate_rows(rows: list[RawItem]) -> ValidationResult`, `Shipment.transition_to(status)`, `CatalogGateway.lookup(gtin)`, and `ShipmentRepository`/`CommandPublisher` protocols.

- [ ] **Step 1: Write failing tests for normalized valid input, duplicate GTIN, invalid quantity, unsupported category, and invalid state transition**

```python
def test_validation_normalizes_gtin_and_category() -> None:
    result = validate_rows([RawItem(row=2, gtin=" 0001234567890 ", category=" Outer Wear ", quantity="2", product_name="Demo jacket")])
    assert result.is_valid is True
    assert result.normalized_items[0].gtin == "00012345678900"
    assert result.normalized_items[0].category == "outer_wear"
```

- [ ] **Step 2: Run validation tests and confirm missing imports/functions fail**

Run: `uv run pytest tests/unit/test_validation.py -q`
Expected: FAIL because domain modules are absent.

- [ ] **Step 3: Implement immutable public models, normalization, validation issues, and transition guard**

- [ ] **Step 4: Run scoped tests**

Run: `uv run pytest tests/unit/test_validation.py -q`
Expected: exit 0.

- [ ] **Step 5: Commit**

`git commit -m 'Добавлен доменный слой валидации заявок'`

### Task 3: Add application use cases with deterministic fakes

**Files:** Create `src/syncmark_demo/application/import_shipment.py`, `src/syncmark_demo/application/submit_shipment.py`, `src/syncmark_demo/infrastructure/memory.py`, `tests/unit/test_import_shipment.py`, `tests/unit/test_submit_shipment.py`.

**Interfaces:** Produces `ImportShipment.execute(filename, content) -> ShipmentView` and `SubmitShipment.execute(shipment_id, idempotency_key) -> ShipmentView`.

- [ ] **Step 1: Write failing tests that prove identical bytes return one shipment and submit rejects a draft/returns one command per key**

```python
def test_identical_import_returns_original_shipment() -> None:
    first = use_case.execute("demo.xlsx", workbook_bytes)
    second = use_case.execute("demo.xlsx", workbook_bytes)
    assert second.id == first.id
```

- [ ] **Step 2: Run scoped tests**

Run: `uv run pytest tests/unit/test_import_shipment.py tests/unit/test_submit_shipment.py -q`
Expected: FAIL because use cases are absent.

- [ ] **Step 3: Implement use cases using only ports, deterministic SHA-256 idempotency, and recorded command publication**

- [ ] **Step 4: Run scoped tests**

Run: `uv run pytest tests/unit/test_import_shipment.py tests/unit/test_submit_shipment.py -q`
Expected: exit 0.

- [ ] **Step 5: Commit**

`git commit -m 'Добавлены сценарии импорта и отправки'`

### Task 4: Implement adapters and asynchronous processing

**Files:** Create `src/syncmark_demo/infrastructure/xlsx.py`, `src/syncmark_demo/infrastructure/catalog.py`, `src/syncmark_demo/infrastructure/pdf.py`, `src/syncmark_demo/application/process_shipment.py`, `src/syncmark_demo/worker.py`, `tests/unit/test_xlsx.py`, `tests/unit/test_process_shipment.py`, `tests/fixtures/synthetic_shipment.xlsx`.

**Interfaces:** Produces `OpenpyxlReader.read(content) -> list[RawItem]`, `MockCatalogGateway.lookup(gtin)`, and `ProcessShipment.execute(shipment_id) -> ShipmentView`.

- [ ] **Step 1: Write failing tests for rejected malformed XLSX, timeout retry success, incompatible catalogue category, and synthetic PDF label output**

```python
async def test_processor_retries_timeout_then_completes() -> None:
    view = await processor.execute(validated_shipment_id)
    assert view.status == ShipmentStatus.COMPLETED
    assert view.label_urls == [f"/labels/{validated_shipment_id}.pdf"]
```

- [ ] **Step 2: Run scoped tests**

Run: `uv run pytest tests/unit/test_xlsx.py tests/unit/test_process_shipment.py -q`
Expected: FAIL because adapters/processor are absent.

- [ ] **Step 3: Implement parser, bounded transient retry, synthetic hard-coded catalogue, synthetic PDF output, and worker command handler**

- [ ] **Step 4: Run scoped tests**

Run: `uv run pytest tests/unit/test_xlsx.py tests/unit/test_process_shipment.py -q`
Expected: exit 0.

- [ ] **Step 5: Commit**

`git commit -m 'Добавлены адаптеры XLSX каталога и обработки'`

### Task 5: Expose FastAPI, configuration, composition, and health

**Files:** Create `src/syncmark_demo/settings.py`, `src/syncmark_demo/api.py`, `src/syncmark_demo/main.py`, `tests/integration/test_api.py`.

**Interfaces:** Produces `create_app() -> FastAPI` and the four specified HTTP routes.

- [ ] **Step 1: Write failing API tests for upload/status, submit idempotency, status conflict, and health shape**

```python
def test_submit_rejects_unvalidated_shipment(client: TestClient) -> None:
    response = client.post(f"/shipments/{draft_id}/submit", headers={"Idempotency-Key": "demo-key"})
    assert response.status_code == 409
    assert response.json()["code"] == "invalid_state"
```

- [ ] **Step 2: Run integration tests**

Run: `uv run pytest tests/integration/test_api.py -q`
Expected: FAIL because app factory is absent.

- [ ] **Step 3: Implement the dependency wiring, upload limits, structured API errors, and health checks using test-safe adapters**

- [ ] **Step 4: Run integration tests**

Run: `uv run pytest tests/integration/test_api.py -q`
Expected: exit 0.

- [ ] **Step 5: Commit**

`git commit -m 'Добавлен HTTP API и проверки состояния'`

### Task 6: Add production deployment adapters and publication package

**Files:** Create `docker-compose.yml`, `Dockerfile`, `alembic.ini`, `migrations/env.py`, `README.md`, `docs/architecture.md`, `LICENSE`, `tests/integration/test_end_to_end.py`; modify `pyproject.toml`, `.github/workflows/ci.yml`.

**Interfaces:** Documents `docker compose up --build`, publishes async SQLAlchemy/FastStream adapter configuration, and provides local end-to-end completion.

- [ ] **Step 1: Write a failing end-to-end test that imports the synthetic fixture, submits it, dispatches one recorded command, and observes completed with a label link**

```python
async def test_import_submit_and_complete_flow(app_services) -> None:
    shipment = app_services.import_shipment.execute("synthetic_shipment.xlsx", fixture_bytes)
    app_services.submit_shipment.execute(shipment.id, "e2e-demo-key")
    completed = await app_services.process_shipment.execute(shipment.id)
    assert completed.status == ShipmentStatus.COMPLETED
```

- [ ] **Step 2: Run the end-to-end test**

Run: `uv run pytest tests/integration/test_end_to_end.py -q`
Expected: FAIL before composition is complete.

- [ ] **Step 3: Add reproducible Docker/Compose, migration scaffold, README, architecture diagram, MIT license, pre-commit, and CI**

- [ ] **Step 4: Run release checks and clean-room scan**

Run: `uv run ruff check . && uv run pyright && uv run pytest -q && git ls-files | rg -i '\\.(xlsx|xls|pdf|docx?|odt)$'`
Expected: exit 0; only `tests/fixtures/synthetic_shipment.xlsx` is listed.

- [ ] **Step 5: Commit**

`git commit -m 'Подготовлена воспроизводимая публичная поставка'`
