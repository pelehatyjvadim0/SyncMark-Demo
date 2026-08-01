import json

from sqlalchemy import String, Text, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from syncmark_demo.domain.models import NormalizedItem, Shipment, ShipmentStatus, ValidationIssue


class Base(DeclarativeBase):
    pass


class ShipmentRow(Base):
    __tablename__ = "shipments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(16))
    items: Mapped[str] = mapped_column(Text)
    issues: Mapped[str] = mapped_column(Text)
    labels: Mapped[str] = mapped_column(Text)
    submitted_keys: Mapped[str] = mapped_column(Text)


class AsyncSqlAlchemyRepository:
    def __init__(self, url: str) -> None:
        self.engine = create_async_engine(url)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)

    async def create_schema(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def ping(self) -> None:
        async with self.engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    async def by_hash(self, content_hash: str) -> Shipment | None:
        async with self.sessions() as session:
            row = await session.scalar(select(ShipmentRow).where(ShipmentRow.content_hash == content_hash))
            return self._shipment(row) if row else None

    async def get(self, shipment_id: str) -> Shipment | None:
        async with self.sessions() as session:
            row = await session.get(ShipmentRow, shipment_id)
            return self._shipment(row) if row else None

    async def save(self, shipment: Shipment) -> None:
        async with self.sessions() as session:
            row = await session.get(ShipmentRow, shipment.id)
            values = self._values(shipment)
            if row is None:
                session.add(ShipmentRow(id=shipment.id, **values))
            else:
                for name, value in values.items():
                    setattr(row, name, value)
            await session.commit()

    @staticmethod
    def _values(shipment: Shipment) -> dict[str, str]:
        return {"content_hash": shipment.content_hash, "status": shipment.status, "items": json.dumps([item.model_dump() for item in shipment.items]), "issues": json.dumps([issue.model_dump(mode="json") for issue in shipment.issues]), "labels": json.dumps(shipment.label_urls), "submitted_keys": json.dumps(sorted(shipment.submitted_keys))}

    @staticmethod
    def _shipment(row: ShipmentRow) -> Shipment:
        return Shipment(row.content_hash, [NormalizedItem.model_validate(item) for item in json.loads(row.items)], [ValidationIssue.model_validate(issue) for issue in json.loads(row.issues)], ShipmentStatus(row.status), id=row.id, label_urls=json.loads(row.labels), submitted_keys=set(json.loads(row.submitted_keys)))
