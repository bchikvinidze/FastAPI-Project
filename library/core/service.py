from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, cast
from uuid import UUID, uuid4

from constants import TRANSACTION_FEE, WALLET_CNT_LIMIT
from library.core import entities
from library.core.entities import Entity, IEntity, Statistic, Transaction, User, Wallet
from library.core.errors import (
    SendAmountExceedsBalance,
    WalletAddressNotOwn,
    WalletLimitReached,
)
from library.core.serialization import (
    Serializer,
    SerializeTransaction,
    SerializeUser,
    SerializeWallet,
)
from library.infra.repository.repository import Repository


class ICommand(ABC):

    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def read_execute(self, entity_id: UUID, column_name: str = "key") -> Any:
        pass


class UserService(ICommand):
    def __init__(
        self,
        repo: Repository,
        table_name: str = "users",
        input_entity: IEntity = Entity(),
    ) -> None:
        self.repo = repo
        self.input_entity = input_entity
        self.table_name = table_name

    def execute(self) -> None:
        self.repo.create(self.input_entity, self.table_name)

    def read_execute(self, entity_id: UUID, column_name: str = "key") -> Any:
        res = self.repo.read_one(entity_id, self.table_name, column_name)
        return SerializeUser().deserialize(res)


class WalletService(ICommand):

    def __init__(
        self,
        repo: Repository,
        table_name: str = "wallets",
        input_entity: IEntity = Entity(),
    ) -> None:
        self.repo = repo
        self.input_entity = input_entity
        self.table_name = table_name

    def execute(self) -> None:
        wallet = cast(entities.Wallet, self.input_entity)
        wallet_count = len(self.repo.read_multi(wallet.user_key, self.table_name))
        if wallet_count >= WALLET_CNT_LIMIT:
            raise WalletLimitReached
        self.repo.create(self.input_entity, self.table_name)

    def read_execute(self, entity_id: UUID, column_name: str = "key") -> Any:
        res = self.repo.read_one(entity_id, self.table_name, column_name)
        return SerializeWallet().deserialize(res)

    def read_bitcoins(self, entity_id: UUID, column_name: str = "key") -> float:
        return cast(entities.Wallet, self.read_execute(entity_id, column_name)).bitcoins


class TransactionService(ICommand):
    def __init__(
        self,
        repo: Repository,
        table_name: str = "transactions",
        input_entity: IEntity = Entity(),
    ) -> None:
        self.repo = repo
        self.input_entity = input_entity
        self.table_name = table_name

    def execute(self) -> None:
        self.repo.create(self.input_entity, self.table_name)

    def read_execute(self, entity_id: UUID, column_name: str = "key") -> Any:
        user_wallets = self.repo.read_multi(entity_id, "wallets")
        transactions = []
        for wallet_raw in user_wallets:
            wallet_item = SerializeWallet().deserialize(wallet_raw)

            list_result = self.repo.read_multi(
                wallet_item.address, "transactions", "address_from"
            )
            for list_item in list_result:
                transactions.append(
                    SerializeTransaction().deserialize(input_data=list_item)
                )

        return transactions

    def read_by_address(self, address: UUID) -> List[Transaction]:
        transactions = []
        from_list = self.repo.read_multi(address, "transactions", "address_from")
        to_list = self.repo.read_multi(address, "transactions", "address_to")
        for item in from_list + to_list:
            transactions.append(SerializeTransaction().deserialize(input_data=item))
        return transactions


class StatisticsService(ICommand):

    def __init__(
        self, repo: Repository, table_name: str, input_entity: IEntity = Entity()
    ) -> None:
        self.repo = repo
        self.input_entity = input_entity
        self.table_name = table_name

    def execute(self) -> None:
        pass

    def read_execute(self, entity_id: UUID = uuid4(), column_name: str = "key") -> Any:
        transactions = self.repo.read_all(self.table_name)
        result = []
        for item in transactions:
            result.append(SerializeTransaction().deserialize(input_data=item))
        total_profit = sum(transaction.fee_amount for transaction in result)
        count_transactions = len(result)
        stat = Statistic(
            count_transactions=count_transactions, total_profit=total_profit
        )
        return stat


@dataclass
class TransferService:
    repo: Repository

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
            raise WalletAddressNotOwn(wallet_from_address)

        wallet_from_initial = wallet_from.bitcoins
        wallet_to_initial = wallet_to.bitcoins

        if wallet_from_initial < send_amount:
            raise SendAmountExceedsBalance(send_amount)

        fee_percent = 0.0
        if wallet_from.user_key != wallet_to.user_key:
            fee_percent = TRANSACTION_FEE

        fee_amount = fee_percent * send_amount
        changes_from = {"bitcoins": wallet_from_initial - send_amount - fee_amount}
        changes_to = {"bitcoins": wallet_to_initial + send_amount}

        self.repo.update(wallet_from_address, "address", "wallets", changes_from)
        self.repo.update(wallet_to_address, "address", "wallets", changes_to)

        transaction = Transaction(
            address_from=wallet_from_address,
            address_to=wallet_to_address,
            amount=send_amount,
            fee_amount=fee_amount,
        )
        TransactionService(self.repo, input_entity=transaction).execute()

    def read_multi(
        self, entity_id: UUID, table_name: str, column_name: str = "key"
    ) -> List[IEntity] | List[Wallet] | List[Transaction] | List[User]:
        list_result = self.repo.read_multi(entity_id, table_name, column_name)
        deserialized = []
        for list_item in list_result:
            deserialized.append(Serializer().deserialize(list_item))
        return deserialized
