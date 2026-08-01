import asyncio


class MockCatalogGateway:
    def __init__(self, transient_failures: int = 0) -> None:
        self.transient_failures = transient_failures
        self.catalog = {
            "00012345678900": {"product_name": "Demo jacket", "category": "outer_wear", "active": True},
            "00012345678901": {"product_name": "Demo sneakers", "category": "footwear", "active": True},
        }

    async def lookup(self, gtin: str) -> dict[str, str | bool]:
        await asyncio.sleep(0)
        if self.transient_failures:
            self.transient_failures -= 1
            raise TimeoutError("synthetic catalogue timeout")
        return self.catalog.get(gtin, {"product_name": "Unknown", "category": "unknown", "active": False})
