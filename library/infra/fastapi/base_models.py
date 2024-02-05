from uuid import UUID

from pydantic import BaseModel

# from library.core.entities import Purchase


# Requests:


# Items
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
    # fee_amount: float
    # key: UUID


# Envelopes for item
class UserItemEnvelope(BaseModel):
    user: UserItem


class UsdWalletItemEnvelope(BaseModel):
    usd_wallet: UsdWalletItem


class WalletItemEnvelope(BaseModel):
    wallet_address: UUID
    bitcoins: float
    usd: float


# Envelopes for list
class TransactionListEnvelope(BaseModel):
    transactions: list[TransactionItem]
