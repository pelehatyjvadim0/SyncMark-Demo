# SyncMark Demo — design specification

## Goal

Deliver an independently runnable public Python backend demonstration for a synthetic product-marking shipment workflow. It must not contain code, history, fixtures, names, credentials, endpoints, or documentation from the closed SyncMark project.

## Constraints and acceptance criteria

- Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 async, Alembic, PostgreSQL, RabbitMQ, FastStream, Docker Compose, uv, pytest, Ruff, Pyright, pre-commit, and GitHub Actions.
- One tracked, synthetic `.xlsx` file exercises import through successful completion.
- HTTP API: `POST /shipments/import`, `POST /shipments/{id}/submit`, `GET /shipments/{id}`, and `GET /health`.
- Valid state transitions are `draft -> validated -> processing -> completed` and `processing -> failed`; a submit is allowed only for a validated shipment.
- Validation returns the public `ValidationResult(is_valid, errors, normalized_items)` model. Each issue has `code`, `field`, `row`, `message`, and `severity`.
- Gateways have explicit ports and adapters. Domain and application code do not import FastAPI, SQLAlchemy, OpenPyXL, RabbitMQ, FastStream, or PDF libraries.
- All test data, catalogue responses, identifiers, GTINs, labels, and documents are demonstrably synthetic.

## Considered approaches

1. Recommended: a modular monolith with pure domain/application layers and replaceable in-memory, SQLAlchemy, and FastStream adapters. It keeps the API/worker architecture honest while unit tests remain fast and independent of containers.
2. A single FastAPI service with direct ORM, spreadsheet, and queue calls. It has the lowest initial file count but violates the required dependency boundaries and makes retry/idempotency rules hard to test.
3. Separate import, API, worker, and gateway services. It resembles production deployment but over-scopes a showcase and makes local reproduction needlessly fragile.

## Architecture

```text
HTTP API / worker
      |
application use cases
      |
domain entities, validation and ports
      |
infrastructure adapters: XLSX, SQLAlchemy/PostgreSQL, FastStream/RabbitMQ,
                         mock catalogue, synthetic PDF labels
```

`ImportShipment` parses rows through an `SpreadsheetReader` port, normalizes and validates them, then creates or returns an idempotent shipment using a SHA-256 content digest. Validation errors are retained on the shipment, while valid rows remain available for inspection; only a fully valid shipment becomes `validated`.

`SubmitShipment` atomically checks state and records an idempotency key before publishing a command. The worker changes the shipment to `processing`, calls `CatalogGateway` with bounded retry for timeout/transient 5xx failures, produces a synthetic PDF through `LabelGenerator`, and persists either `completed` with label links or `failed` with a structured processing issue.

## Data and contracts

The synthetic workbook has the headers `GTIN`, `category`, `quantity`, and `product_name`. GTIN is normalized to its 14-digit representation, category is normalized to lowercase snake-style tokens, and quantity is a positive integer. Duplicate GTINs, unsupported or inactive categories, and incompatible catalogue product/category pairs create errors. A gateway outage is a warning during import preflight and a retryable processing failure after submit.

The mock catalogue provides only a hard-coded synthetic catalogue. Its contract is an async lookup by normalized GTIN returning product name, category, and active state. The HTTP-like mock accepts the `Idempotency-Key` header in its adapter boundary, has a configurable timeout, and retries only timeout/5xx-class failures with a capped attempt count.

`ShipmentRepository` and `CommandPublisher` are ports. The production repository is async SQLAlchemy with PostgreSQL; tests use an in-memory repository. Queue publication is represented by a FastStream RabbitMQ adapter and a recording fake for tests. This makes submission idempotency observable without requiring RabbitMQ for every test.

## API behavior

- `POST /shipments/import` accepts an XLSX upload and returns shipment id, status, normalized item count, and validation issues. Re-uploading byte-identical content returns the original shipment.
- `POST /shipments/{id}/submit` accepts `Idempotency-Key`, returns `202` for a newly queued shipment and the current representation for an equivalent retry. Invalid state returns a structured 409 response.
- `GET /shipments/{id}` returns status, item count, validation/processing issues, and generated label URLs.
- `GET /health` reports API liveness and the independently checked PostgreSQL/RabbitMQ dependency statuses. In local test mode adapters may report their in-memory status.

## Error handling and security

Uploads are limited by configuration, parsed only as `.xlsx`, and reject malformed or header-invalid workbooks without stack traces in responses. Public error codes are stable; exception details remain server-side. Configuration is environment-driven with `.env.example` placeholders only. The repository includes ignored local environment files, generated labels, database volumes, and Python caches. A release scan rejects office documents outside the synthetic fixture, credential-like files, and references to closed-project naming.

## Test strategy

Unit tests cover normalization, all required validation classes, state transitions, idempotent imports/submits, and retry classification. Integration tests exercise API upload/status behavior, SQLAlchemy persistence, mock gateway transient failure, and the import-to-completed flow using recording adapters. Container verification exercises PostgreSQL and RabbitMQ via Docker Compose. CI runs Ruff, Pyright, and pytest; the compose command remains the documented local smoke path.

## Scope boundary

The demo does not connect to regulators, commercial catalogues, identity providers, or real label generation systems. It exposes no multi-tenant access control, production observability stack, or deployment automation beyond reproducible local Compose and CI quality checks.
