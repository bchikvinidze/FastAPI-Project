from dataclasses import dataclass, field
from typing import Any

from faker import Faker

FAKER_PRODUCT_DEFAULT_PRICE = 1.1

'''
@dataclass
class FakeUser:
    faker: Faker = field(default_factory=Faker)

    def entity(self, author: str = "") -> dict[str, Any]:
        return {"key": self.faker. ()}
'''


# albat amaze damchirdeba rom Product-is shvilobili gavxado
@dataclass
class FakeProduct:
    faker: Faker = field(default_factory=Faker)
    as_dict: dict[str, object] = field(default_factory=dict)

    def entity(
        self, unit_id: str = "", price: float = FAKER_PRODUCT_DEFAULT_PRICE
    ) -> dict[str, Any]:
        self.as_dict = {
            "name": self.faker.catch_phrase(),
            "unit_id": unit_id,
            "barcode": "1",
            "price": price,
        }
        return self.as_dict


@dataclass
class FakeReceipt:
    faker: Faker = field(default_factory=Faker)

    def entity(self, products: list[dict[str, Any]]) -> dict[str, Any]:
        return {"status": "open", "products": products, "total": 0}
