from __future__ import annotations

from typing import Dict, List, cast
from uuid import UUID

from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

from library.core.authenticate import AdminAuthenticator, UserAuthenticator
from library.core.bitcoin_converter import BitcoinToCurrency
from library.core.entities import (
    IEntity,
    Statistic,
    Transaction,
    UsdWallet,
    User,
    Wallet,
)
from library.core.errors import WebException
from library.core.service import TransferService, UserService, WalletService, TransactionService, StatisticsService
from library.infra.fastapi.base_models import (
    StatisticsItemEnvelope,
    TransactionItem,
    TransactionListEnvelope,
    UsdWalletItemEnvelope,
    UserItemEnvelope,
    WalletItemEnvelope,
)
from library.infra.fastapi.dependables import RepositoryDependable

api = APIRouter()


@api.post("/users", status_code=201, response_model=UserItemEnvelope, tags=["Users"])
def create_user(repo_dependable: RepositoryDependable) -> Dict[str, User]:
    new_user = User()
    UserService(repo_dependable, input_entity=new_user).execute()
    return {"user": new_user}


@api.post(
    "/wallets", status_code=201, response_model=UsdWalletItemEnvelope, tags=["Wallets"]
)
def create_wallet(
    request: Request, repo_dependable: RepositoryDependable
) -> Dict[str, UsdWallet] | JSONResponse:
    x_api_key = UUID(request.headers["x-api-key"])
    try:
        UserAuthenticator(repo_dependable).authenticate(x_api_key)
        wallet = Wallet(user_key=x_api_key)
        WalletService(repo_dependable, "wallets", wallet).execute()
        usd = BitcoinToCurrency().convert(wallet.bitcoins)
        usd_wallet = UsdWallet(
            wallet_address=wallet.address,
            bitcoins_balance=wallet.bitcoins,
            usd_balance=usd,
        )
        return {"usd_wallet": usd_wallet}
    except WebException as we:
        return we.json_response()


@api.post(
    "/transactions",
    status_code=201,
    response_model=TransactionItem,
    tags=["Transactions"],
)
def create_transaction(
    transaction: dict[str, UUID | float],
    request: Request,
    repo_dependable: RepositoryDependable,
) -> JSONResponse:
    x_api_key = UUID(request.headers["x-api-key"])
    try:
        UserAuthenticator(repo_dependable).authenticate(x_api_key)
        wallet_from = cast(UUID, transaction["address_from"])
        wallet_to = cast(UUID, transaction["address_to"])
        send_amount = cast(float, transaction["amount"])
        TransferService(repo_dependable).transfer(
            wallet_from, wallet_to, send_amount, x_api_key
        )
        return JSONResponse(status_code=201, content={})
    except WebException as we:
        return we.json_response()


@api.get(
    "/users/{user_key}/",
    status_code=200,
    response_model=UserItemEnvelope,
    tags=["Users"],
)
def read_one_user(
    user_key: UUID, request: Request, repo_dependable: RepositoryDependable
) -> dict[str, IEntity] | JSONResponse:
    x_api_key = request.headers["x-api-key"]
    try:
        UserAuthenticator(repo_dependable).authenticate(UUID(x_api_key))
        return {"user": UserService(repo_dependable, "users", User()).read_execute(user_key)}
    except WebException as we:
        return we.json_response()


@api.get(
    "/wallets/{address}/",
    status_code=200,
    response_model=WalletItemEnvelope,
    tags=["Wallets"],
)
def read_wallet_address(
    address: UUID, request: Request, repo_dependable: RepositoryDependable
) -> Dict[str, UUID | float] | JSONResponse:
    x_api_key = request.headers["x-api-key"]
    try:
        UserAuthenticator(repo_dependable).authenticate(UUID(x_api_key))
        bitcoins = WalletService(repo_dependable).read_bitcoins(
            address, "address"
        )
        return {
            "wallet_address": address,
            "bitcoins": bitcoins,
            "usd": BitcoinToCurrency().convert(bitcoins),
        }
    except WebException as we:
        return we.json_response()


@api.get(
    "/transactions",
    status_code=200,
    response_model=TransactionListEnvelope,
    tags=["transactions"],
)
def read_transactions(
    request: Request, repo_dependable: RepositoryDependable
) -> Dict[str, List[Transaction]] | JSONResponse:
    x_api_key = UUID(request.headers["x-api-key"])
    try:
        UserAuthenticator(repo_dependable).authenticate(x_api_key)
        transactions = TransactionService(repo_dependable).read_execute(x_api_key)
        return {"transactions": transactions}
    except WebException as we:
        return we.json_response()


@api.get(
    "/wallets/{address}/transactions",
    status_code=200,
    response_model=TransactionListEnvelope,
    tags=["transactions"],
)
def read_wallet_transactions(
    address: UUID, request: Request, repo_dependable: RepositoryDependable
) -> Dict[str, List[Transaction]] | JSONResponse:
    x_api_key = UUID(request.headers["x-api-key"])
    try:
        UserAuthenticator(repo_dependable).authenticate(x_api_key)
        transactions = TransactionService(repo_dependable).read_by_address(address)
        return {"transactions": transactions}
    except WebException as we:
        return we.json_response()


@api.get(
    "/statistics",
    status_code=200,
    response_model=StatisticsItemEnvelope,
    tags=["statistics"],
)
def get_statistics(
    request: Request, repo_dependable: RepositoryDependable
) -> dict[str, Statistic] | JSONResponse:
    x_api_key = UUID(request.headers["x-api-key"])
    try:
        AdminAuthenticator().authenticate(x_api_key)
        curr_statistics = StatisticsService(repo_dependable, "transactions").read_execute()
        return {"statistics": curr_statistics}
    except WebException as we:
        return we.json_response()
