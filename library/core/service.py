from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from constants import WALLET_CNT_LIMIT, TRANSACTION_FEE
from library.core.entities import Entity, User, Wallet, Transaction
from library.core.errors import DoesNotExistError, WalletLimitReached, ApiKeyWrong, WalletAddressNotOwn, \
    SendAmountExceedsBalance
from library.core.serialization import SerializerForDB
from library.infra.repository.repository import Repository

#drota ganmavlobashi chavshli ramdenime servisad - wallets tavisi eqneba, trannazqciebs - tavisi da a.sh
@dataclass
class Service:
    repo: Repository

    def create(self, input_entity: Entity, table_name: str) -> None:
        self.repo.create(input_entity, table_name)

    def create_wallet(self, wallet: Wallet) -> None:
        wallet_count = len(self.repo.read_multi(wallet.user_key, 'wallets'))
        if wallet_count >= WALLET_CNT_LIMIT:
            raise WalletLimitReached
        input_entity: Entity = wallet
        self.repo.create(input_entity, "wallets")

    def read_wallet_bitcoins(self, entity_id: UUID, table_name: str, column_name: str = "key") -> float:
        res = self.repo.read_one(entity_id, table_name, column_name)
        return SerializerForDB().deserialize_wallet(res).bitcoins

    def read(
        self, entity_id: UUID, table_name: str, column_name: str = "key"
    ) -> User | Wallet | Entity:
        res = self.repo.read_one(entity_id, table_name, column_name)
        if table_name == "wallets": #es dzaan sashinelebaa, if ar unda mchirdebodes wesit
            return SerializerForDB().deserialize_wallet(res)
        return SerializerForDB().deserialize(table_name, res)

    def exists(self, entity_id: UUID, table_name: str, column_name: str = "key") -> bool:
        res = self.repo.read_one(entity_id, table_name, column_name)
        if len(res) == 0:
            return False
        return True

    def transfer(self, wallet_from_address: UUID, wallet_to_address: UUID, send_amount: float, x_api_key: UUID) -> None:
        wallet_from = self.read(wallet_from_address, "wallets", "address")
        wallet_to = self.read(wallet_to_address, "wallets", "address")

        if wallet_from.user_key != x_api_key:
            raise WalletAddressNotOwn

        wallet_from_initial = wallet_from.bitcoins
        wallet_to_initial = wallet_to.bitcoins

        if wallet_from_initial < send_amount:
            raise SendAmountExceedsBalance

        fee_percent = 0
        if wallet_from.user_key != wallet_to.user_key:
            fee_percent = TRANSACTION_FEE

        fee_amount = fee_percent*send_amount
        changes_from = {'bitcoins': wallet_from_initial-send_amount-fee_amount}
        changes_to = {'bitcoins': wallet_to_initial+send_amount}

        # update respective wallets in db
        self.repo.update(wallet_from_address, "address", "wallets", changes_from)
        self.repo.update(wallet_to_address, "address", "wallets", changes_to)

        # add new transaction to repository
        transaction = Transaction(address_from=wallet_from_address,
                                  address_to=wallet_to_address,
                                  amount=send_amount,
                                  fee_amount=fee_amount)
        self.create(transaction, "transactions")


@dataclass
class Authenticator:
    repo: Repository

    def authenticate(self, api_key: UUID) -> None:
        try:
            res = self.repo.read_one(api_key, 'users', 'key')
        except DoesNotExistError:
            raise ApiKeyWrong
