# SyncMark Demo

A clean-room FastAPI showcase of a synthetic product-marking shipment workflow. It has no connection to commercial, regulatory, or production APIs.

## What it demonstrates

Upload an XLSX with `GTIN`, `category`, `quantity`, and `product_name`; normalize and validate it; submit a validated shipment idempotently; then process it through a synthetic catalogue and PDF-label adapter. Domain rules and use cases are independent of HTTP, XLSX, queues, and persistence adapters.

## Quick start

```bash
uv sync --python python3.12 --group dev
uv run uvicorn syncmark_demo.main:app --reload
```

Then open `http://127.0.0.1:8000/docs`. Start the local service dependencies with:

```bash
docker compose up --build
```

Compose starts the API, PostgreSQL, RabbitMQ, and a FastStream worker. `GET /health` verifies the API's PostgreSQL and RabbitMQ wiring.
The `migrate` service applies the tracked Alembic revision before the API and worker start.

## API flow

`POST /shipments/import` accepts an `.xlsx` upload. `POST /shipments/{id}/submit` requires `Idempotency-Key`. `GET /shipments/{id}` returns status, structured validation issues, item count, and synthetic label URLs. `GET /health` exposes component status.

## Testing

```bash
uv run ruff check .
uv run pyright
uv run pytest -q
```

## Demo limits

Catalogue records, GTINs, workbook data, and PDF labels are synthetic. The demo intentionally omits real provider credentials, regulatory integration, multi-tenancy, and production access controls.

Licensed under the MIT License. See [architecture notes](docs/architecture.md).
