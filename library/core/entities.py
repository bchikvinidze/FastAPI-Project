from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4

from constants import INITIAL_BITCOINS


class SerializerDB:
    pass


class Entity(Protocol):
    key: UUID


@dataclass(kw_only=True)
class User:
    key: UUID = field(default_factory=uuid4)


@dataclass(kw_only=True)
class Wallet:
    user_key: UUID
    bitcoins: float = INITIAL_BITCOINS
    address: UUID = field(default_factory=uuid4)
    key: UUID = field(default_factory=uuid4)


@dataclass(kw_only=True)
class UsdWallet:
    wallet_address: UUID
    bitcoins_balance: float
    usd_balance: float


@dataclass(kw_only=True)
class Transaction:
    address_from: UUID
    address_to: UUID
    amount: float
    fee_amount: float
    key: UUID = field(default_factory=uuid4)

