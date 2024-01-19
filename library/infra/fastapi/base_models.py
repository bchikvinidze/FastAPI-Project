from uuid import UUID

from pydantic import BaseModel

#from library.core.entities import Purchase


# Requests:


# Items
class UserItem(BaseModel):
    key: UUID


# Envelopes for item
class UserItemEnvelope(BaseModel):
    user: UserItem

# Envelopes for list
