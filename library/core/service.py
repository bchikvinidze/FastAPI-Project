from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from constants import WALLET_CNT_LIMIT
from library.core.entities import Entity, User, Wallet
from library.core.errors import DoesNotExistError, WalletLimitReached
from library.core.serialization import SerializerForDB
from library.infra.repository.repository import Repository


@dataclass
class Service:
    repo: Repository

    def create(self, input_entity: Entity, table_name: str) -> None:
        self.repo.create(input_entity, table_name)

    def create_wallet(self, wallet: Wallet) -> None:
        user_cnt = len(self.repo.read_one(wallet.user_key, 'users'))
        if user_cnt == 0:
            raise DoesNotExistError
        wallet_count = len(self.repo.read_multi(wallet.user_key, 'wallets'))
        if wallet_count >= WALLET_CNT_LIMIT:
            raise WalletLimitReached
        self.create(wallet, "wallets")

    def read(
        self, entity_id: UUID, table_name: str
    ) -> User | Entity:
        res = self.repo.read_one(entity_id, table_name)
        return SerializerForDB().deserialize(
            table_name, res
        )

    def exists(self, entity_id: UUID, table_name: str) -> bool:
        res = self.repo.read_one(entity_id, table_name)
        if len(res) == 0:
            return False
        return True
