
from __future__ import annotations

from typing import Protocol, Dict, List
from uuid import UUID

from dacite import Config, from_dict

import library.core.entities as entities


class Serializer(Protocol):
    def serialize(self, entity_type: str, input_data: entities.Entity) -> List[object]:
        pass

    def deserialize(
            self, entity_type: str, input_data: Dict[str, object]
    ) -> entities.Entity | List[entities.Entity]:
        pass


class SerializerForDB:
    @staticmethod
    def serialize(
           dt: entities.Entity, columns: List[str]
    ) -> Dict[str, object]:
        result = dt.__dict__
        result = {k: result[k] for k in columns}
        # db can't accept UUID, so converting to string
        for key in result.keys():
            if ("key" in key) or ("address" in key):
                result[key] = str(result[key])
        return result

    @staticmethod
    def deserialize(
            entity_type: str, input_data: Dict[str, object]
    ) -> entities.Entity:
        class_data = eval("entities." + entity_type.capitalize()[:-1])
        result: entities.Entity = from_dict(
            data_class=class_data,
            data=input_data,
            config=Config(cast=[UUID]),
        )
        return result

    @staticmethod
    def deserialize_wallet(input_data: Dict[str, object]) -> entities.Wallet:
        return from_dict(
            data_class=entities.Wallet,
            data=input_data,
            config=Config(cast=[UUID]),
        )

    @staticmethod
    def deserialize_transaction(
            input_data: Dict[str, object]
    ) -> entities.Transaction:
        return from_dict(
            data_class=entities.Transaction,
            data=input_data,
            config=Config(cast=[UUID]),
        )