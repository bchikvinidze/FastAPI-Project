from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from library.core.entities import Entity, User
from library.core.errors import DoesNotExistError
from library.core.serialization import SerializerForDB
from library.infra.repository.repository import Repository


@dataclass
class Service:
    repo: Repository

    def create(self, input_entity: Entity, table_name: str) -> None:
        self.repo.create(input_entity, table_name)

    def read(
        self, entity_id: UUID, table_name: str
    ) -> User | Entity:
        res = self.repo.read_one(entity_id, table_name)
        return SerializerForDB().deserialize(
            table_name, res
        )

    """
    def read_all(
        self, table_name: str
    ) -> list[Unit] | list[Product] | list[Receipt] | list[Purchase] | list[Entity]:
        if table_name == "receipts":
            receipts = [
                SerializerForDB().deserialize_receipt(r)
                for r in self.repo.read_all(table_name)
            ]
            purchases = [
                SerializerForDB().deserialize_purchase(p)
                for p in self.repo.read_all("purchases")
            ]
            result = []
            for receipt in receipts:
                purchase_list = [p for p in purchases if p.receipt_id == receipt.id]
                receipt.products = purchase_list
                result.append(receipt)
            return result
        else:
            return [
                SerializerForDB().deserialize(table_name, i)
                for i in self.repo.read_all(table_name)
            ]

    def add_product(
        self, entity_id: UUID, table_name: str, product_id: UUID, product_quantity: int
    ) -> None:
        # get corresponding product from db:
        product = SerializerForDB().deserialize_product(
            self.repo.read_one(product_id, "products")
        )

        purchase_price = product.price * product_quantity
        purchase = Purchase(
            quantity=product_quantity,
            price=product.price,
            total=purchase_price,
            receipt_id=entity_id,
            id=product.id,
        )
        self.repo.create_without_dupe_check(purchase, "purchases")

        # change total price:
        cur_receipt = SerializerForDB().deserialize_receipt(
            self.repo.read_one(entity_id, table_name)
        )
        cur_total = cur_receipt.total
        self.repo.update(entity_id, table_name, {"total": cur_total + purchase_price})

    def update(
        self, entity_id: UUID, table_name: str, changes: dict[str, object]
    ) -> None:
        self.repo.update(entity_id, table_name, changes)

    def delete(self, entity_id: UUID, table_name: str) -> None:
        self.repo.delete(entity_id, table_name)

    def sales(self, amount: bool = True) -> float:
        result = 0.0
        receipts: list[Receipt] = [
            SerializerForDB().deserialize_receipt(r)
            for r in self.repo.read_all("receipts")
        ]
        for receipt in receipts:
            if receipt.status == "closed":
                if amount:
                    result += receipt.total
                else:
                    result += 1
        return result

    """