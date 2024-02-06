from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, TypeVar
from uuid import UUID

from dacite import Config, from_dict

import library.core.entities as entities

T = TypeVar("T")


@dataclass
class Serializer:
    columns: List[str] = field(default_factory=lambda: ["key", "address"])

    def serialize(self, dt: entities.IEntity, columns: List[str]) -> Dict[str, object]:
        result = dt.__dict__
        result = {k: result[k] for k in columns}
        for key in result.keys():
            if self.columns[0] in key or self.columns[1] in key:
                result[key] = str(result[key])
        return result

    def deserialize(self, input_data: Dict[str, object]) -> entities.IEntity:
        return from_dict(
            data_class=entities.Entity,
            data=input_data,
            config=Config(cast=[UUID]),
        )


@dataclass
class SerializeWallet(Serializer):

    def deserialize(self, input_data: Dict[str, object]) -> entities.Wallet:
        return from_dict(
            data_class=entities.Wallet,
            data=input_data,
            config=Config(cast=[UUID]),
        )


@dataclass
class SerializeTransaction(Serializer):

    def deserialize(self, input_data: Dict[str, object]) -> entities.Transaction:
        return from_dict(
            data_class=entities.Transaction,
            data=input_data,
            config=Config(cast=[UUID]),
        )


@dataclass
class SerializeUser(Serializer):

    def deserialize(self, input_data: Dict[str, object]) -> entities.User:
        return from_dict(
            data_class=entities.User,
            data=input_data,
            config=Config(cast=[UUID]),
        )
