from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4

from constants import INITIAL_BITCOINS


class SerializerDB:
    pass


class IEntity(Protocol):
    key: UUID


@dataclass(kw_only=True)
class Entity(IEntity):
    key: UUID = field(default_factory=uuid4)


@dataclass(kw_only=True)
class User(IEntity):
    key: UUID = field(default_factory=uuid4)


@dataclass(kw_only=True)
class Wallet(IEntity):
    user_key: UUID
    bitcoins: float = INITIAL_BITCOINS
    address: UUID = field(default_factory=uuid4)
    key: UUID = field(default_factory=uuid4)


@dataclass(kw_only=True)
class UsdWallet(IEntity):
    wallet_address: UUID
    bitcoins_balance: float
    usd_balance: float
    key: UUID = field(default_factory=uuid4)


@dataclass(kw_only=True)
class Transaction(IEntity):
    address_from: UUID
    address_to: UUID
    amount: float
    fee_amount: float = 0.0
    key: UUID = field(default_factory=uuid4)


# @dataclass(kw_only=True)
@dataclass
class Statistic:
    count_transactions: int
    total_profit: float
    # key: UUID = field(default_factory=uuid4)

