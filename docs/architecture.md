# Architecture

```text
XLSX upload -> parser -> validation -> shipment repository -> command publisher
                                                         -> worker -> mock catalogue -> synthetic PDF
```

Tests wire local in-memory adapters; the Compose application wires the async SQLAlchemy PostgreSQL repository and FastStream RabbitMQ publisher. The domain uses explicit protocols for its repository, command publisher, spreadsheet reader, catalogue gateway, and label generator; deployment adapters can be substituted without coupling validation rules to framework code.

Docker Compose starts PostgreSQL and RabbitMQ alongside the API so deployment wiring can be exercised locally. The included catalogue is hard-coded synthetic data and labels contain only generated shipment identifiers.
