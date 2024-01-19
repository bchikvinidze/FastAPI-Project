from uuid import UUID

from pydantic import BaseModel

#from library.core.entities import Purchase


# Requests:


# Items
class UserItem(BaseModel):
    key: UUID


class WalletItem(BaseModel):
    user_key: UUID
    bitcoins: float
    address: UUID


# Envelopes for item
class UserItemEnvelope(BaseModel):
    user: UserItem


class WalletItemEnvelope(BaseModel):
    wallet: WalletItem

# Envelopes for list
