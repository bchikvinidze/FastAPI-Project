from typing import List
from uuid import UUID

from pydantic import BaseModel


class UserItem(BaseModel):
    key: UUID


class WalletItem(BaseModel):
    user_key: UUID
    bitcoins: float
    address: UUID


class UsdWalletItem(BaseModel):
    wallet_address: UUID
    bitcoins_balance: float
    usd_balance: float


class TransactionItem(BaseModel):
    address_from: UUID
    address_to: UUID
    amount: float


class StatisticsItem(BaseModel):
    count_transactions: int
    total_profit: float


class UserItemEnvelope(BaseModel):
    user: UserItem


class StatisticsItemEnvelope(BaseModel):
    statistics: StatisticsItem


class UsdWalletItemEnvelope(BaseModel):
    usd_wallet: UsdWalletItem


class WalletItemEnvelope(BaseModel):
    wallet_address: UUID
    bitcoins: float
    usd: float


class TransactionListEnvelope(BaseModel):
    transactions: List[TransactionItem]
