from __future__ import annotations

from typing import List

from dataclasses import dataclass
from uuid import UUID

from constants import TRANSACTION_FEE, WALLET_CNT_LIMIT
from library.core.entities import Transaction, User, Wallet, IEntity
from library.core.errors import (
    ApiKeyWrong,
    DoesNotExistError,
    SendAmountExceedsBalance,
    WalletAddressNotOwn,
    WalletLimitReached,
)
from library.core.serialization import Serializer, \
    SerializeWallet, SerializeTransaction, SerializeUser
from library.infra.repository.repository import Repository


# drota ganmavlobashi chasashlelia ramdenime
# servisad (tore single responsibilitys argvevs dzaaaan)
# wallets tavisi eqneba, trannazqciebs - tavisi da a.sh
@dataclass
class Service:
    repo: Repository

    def create(self, input_entity: IEntity, table_name: str) -> None:
        self.repo.create(input_entity, table_name)

    def create_wallet(self, wallet: Wallet) -> None:
        wallet_count = len(self.repo.read_multi(wallet.user_key, "wallets"))
        if wallet_count >= WALLET_CNT_LIMIT:
            raise WalletLimitReached
        input_entity: IEntity = wallet
        self.repo.create(input_entity, "wallets")

    def read_wallet_bitcoins(
            self, entity_id: UUID, table_name: str, column_name: str = "key"
    ) -> float:
        res = self.repo.read_one(entity_id, table_name, column_name)
        return SerializeWallet().deserialize(res).bitcoins

    def read(
            self, entity_id: UUID, table_name: str, column_name: str = "key"
    ) -> User | Wallet | IEntity:
        res = self.repo.read_one(entity_id, table_name, column_name)
        if (
                table_name == "wallets"
        ):  # es dzaan sashinelebaa, if ar unda mchirdebodes wesit
            return SerializeWallet().deserialize(res)
        return SerializeUser().deserialize(res)

    def exists(
            self, entity_id: UUID, table_name: str, column_name: str = "key"
    ) -> bool:
        res = self.repo.read_one(entity_id, table_name, column_name)
        if len(res) == 0:
            return False
        return True

    # egreve transaction klass s ver gadavce tore SOLID-is I dairgveva mgoni.
    def transfer(
            self,
            wallet_from_address: UUID,
            wallet_to_address: UUID,
            send_amount: float,
            x_api_key: UUID,
    ) -> None:
        wallet_from = SerializeWallet().deserialize(
            self.repo.read_one(wallet_from_address, "wallets", "address")
        )
        wallet_to = SerializeWallet().deserialize(
            self.repo.read_one(wallet_to_address, "wallets", "address")
        )

        if wallet_from.user_key != x_api_key:
            raise WalletAddressNotOwn

        wallet_from_initial = wallet_from.bitcoins
        wallet_to_initial = wallet_to.bitcoins

        if wallet_from_initial < send_amount:
            raise SendAmountExceedsBalance

        fee_percent = 0.0
        if wallet_from.user_key != wallet_to.user_key:
            fee_percent = TRANSACTION_FEE

        fee_amount = fee_percent * send_amount
        changes_from = {"bitcoins": wallet_from_initial - send_amount - fee_amount}
        changes_to = {"bitcoins": wallet_to_initial + send_amount}

        # update respective wallets in db
        self.repo.update(wallet_from_address, "address", "wallets", changes_from)
        self.repo.update(wallet_to_address, "address", "wallets", changes_to)

        # add new transaction to repository
        transaction = Transaction(
            address_from=wallet_from_address,
            address_to=wallet_to_address,
            amount=send_amount,
            fee_amount=fee_amount,
        )
        self.create(transaction, "transactions")

    def read_multi(
            self, entity_id: UUID, table_name: str, column_name: str = "key"
    ) -> List[IEntity] | List[Wallet] | List[Transaction] | List[User]:
        list_result = self.repo.read_multi(entity_id, table_name, column_name)
        deserialized = []
        for list_item in list_result:
            deserialized.append(Serializer().deserialize(list_item))
        return deserialized

    def read_transactions(self, user_key: UUID) -> List[Transaction]:
        user_wallets = self.repo.read_multi(user_key, "wallets")
        transactions = []
        for wallet_raw in user_wallets:
            wallet_item = SerializeWallet().deserialize(wallet_raw)

            # get transactions where amount was sent from given address.
            list_result = self.repo.read_multi(
                wallet_item.address, "transactions", "address_from"
            )
            for list_item in list_result:
                transactions.append(
                    SerializeTransaction().deserialize(input_data=list_item)
                )

        return transactions

    def read_transactions_by_address(self, address: UUID) -> List[Transaction]:
        transactions = []
        from_list = self.repo.read_multi(address, 'transactions', 'address_from')
        to_list = self.repo.read_multi(address, 'transactions', 'address_to')
        for item in from_list + to_list:
            transactions.append(
                # old version
                # SerializerForDB().deserialize_transaction(item)
                SerializeTransaction().deserialize(input_data=item)
            )
        return transactions


@dataclass
class Authenticator:
    repo: Repository

    def authenticate(self, api_key: UUID) -> None:
        try:
            res = self.repo.read_one(api_key, "users", "key")
        except DoesNotExistError:
            raise ApiKeyWrong
