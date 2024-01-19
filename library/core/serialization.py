from __future__ import annotations

from typing import Protocol
from uuid import UUID

from dacite import Config, from_dict

import library.core.entities as entities


class Serializer(Protocol):
    def serialize(self, entity_type: str, input_data: entities.Entity) -> list[object]:
        pass

    def deserialize(
        self, entity_type: str, input_data: dict[str, object]
    ) -> entities.Entity | list[entities.Entity]:
        pass


class SerializerForDB:
    primitives = (bool, str, int, float, type(None))

    def serialize(
        self, table_name: str, dt: entities.Entity, columns: list[str]
    ) -> dict[str, object]:
        result = dt.__dict__
        result = {k: result[k] for k in columns}
        for key in result.keys():
            if "key" in key:
                result[key] = str(result[key])
        return result

    def deserialize(
        self, entity_type: str, input_data: dict[str, object]
    ) -> entities.Entity:
        class_data = eval("entities." + entity_type.capitalize()[:-1])
        result: entities.Entity = from_dict(
            data_class=class_data,
            data=input_data,
            config=Config(cast=[UUID]),
        )
        return result

    def deserialize_unit(self, input_data: dict[str, object]) -> entities.Unit:
        return from_dict(
            data_class=entities.Unit,
            data=input_data,
            config=Config(cast=[UUID]),
        )

    def deserialize_product(self, input_data: dict[str, object]) -> entities.Product:
        return from_dict(
            data_class=entities.Product,
            data=input_data,
            config=Config(cast=[UUID]),
        )

    def deserialize_receipt(self, input_data: dict[str, object]) -> entities.Receipt:
        return from_dict(
            data_class=entities.Receipt,
            data=input_data,
            config=Config(cast=[UUID]),
        )

    def deserialize_purchase(self, input_data: dict[str, object]) -> entities.Purchase:
        return from_dict(
            data_class=entities.Purchase,
            data=input_data,
            config=Config(cast=[UUID]),
        )
