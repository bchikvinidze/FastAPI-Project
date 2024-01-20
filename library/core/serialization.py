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
        #db can't accept UUID, so converting to string
        for key in result.keys():
            if ("key" in key) or ("address" in key):
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

    def deserialize_wallet(self, input_data: dict[str, object]) -> entities.Wallet:
        return from_dict(
            data_class=entities.Wallet,
            data=input_data,
            config=Config(cast=[UUID]),
        )