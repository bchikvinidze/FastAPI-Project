"""
feedback rac mivige msgavss midgomaze:
Open-Closed Principle: SerializerForDB ცოტა არღვევს:
ახალი ობიექტის სერიალიზაცია/დესერიალიზაცია რომ მოგვინდეს ამ კლასში მოგვიწევს ცვლილებების შეტანა.
თითქმის ყველგან სადაც ამ სერიალიზატორ კლასს იყენებ მაინც ახალი ინსტანსის შექმნა გიწევს
და თითქმის ყველგან კონკრეტულ deserialize მეთოდებს იყენებ (deserialize_unit, deserialize_product...),
რაც, ცალკე კლასად გამოყოფა რისთვისაც შეიძლება გინდოდეს მაგ მიზანსვე ეწინააღმდეგება.
აჯობებდა Serializable ინტერფეისი გქონოდა და ობიექტებშივე გაგეწერა serialization/deserialization ლოგიკა.
"""

from __future__ import annotations

from typing import Dict, List, Type, cast, TypeVar, Generic, Protocol, Union, Any, Never
from uuid import UUID

from dataclasses import dataclass, field
from dacite import Config, from_dict

import library.core.entities as entities

T = TypeVar("T")


@dataclass
class Serializer:
    columns: List[str] = field(default_factory=lambda: ["key", "address"])
    class_data: Any = field(default_factory=type(entities.Entity))

    def serialize(self, dt: entities.Entity, columns: List[str]) -> Dict[str, object]:
        result = dt.__dict__
        result = {k: result[k] for k in columns}
        # db can't accept UUID, so converting to string
        for key in result.keys():
            if key in self.columns:
                result[key] = str(result[key])
        return result

    def deserialize(self, input_data: Dict[str, object]) -> entities.Entity:
        result: entities.Entity = from_dict(
            data_class=self.class_data,
            data=input_data,
            config=Config(cast=[UUID]),
        )
        return result


@dataclass
class SerializeWallet(Serializer):
    class_data: Any = field(default_factory=type(entities.Wallet))

    def deserialize(self, input_data: Dict[str, object]) -> entities.Wallet:
        return cast(entities.Wallet, super().deserialize(input_data))


@dataclass
class SerializeTransaction(Serializer):
    class_data: Any = field(default_factory=type(entities.Transaction))

    def deserialize(self, input_data: Dict[str, object]) -> entities.Transaction:
        return cast(entities.Transaction, super().deserialize(input_data))