from __future__ import annotations

from typing import Dict
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.responses import JSONResponse

from library.core.bitcoin_converter import BitcoinToCurrency
from library.core.entities import User, Wallet, UsdWallet, Entity, Transaction, Statistic
from library.core.errors import WebException
from library.core.service import Service
from library.core.authenticate import UserAuthenticator, AdminAuthenticator
from library.infra.fastapi.base_models import UserItemEnvelope, UsdWalletItemEnvelope, WalletItemEnvelope, \
    TransactionItem, TransactionListEnvelope, StatisticsItem, StatisticsItemEnvelope
from library.infra.fastapi.dependables import RepositoryDependable

api = APIRouter()


@api.post("/users", status_code=201, response_model=UserItemEnvelope, tags=["Users"])
def create_user(
        repo_dependable: RepositoryDependable
) -> dict[str, User]:
    new_user = User()
    Service(repo_dependable).create(new_user, "users")
    return {"user": new_user}


@api.post("/wallets", status_code=201, response_model=UsdWalletItemEnvelope, tags=["Wallets"])
def create_wallet(
        request: Request,
        repo_dependable: RepositoryDependable
) -> dict[str, UsdWallet] | JSONResponse:
    x_api_key = UUID(request.headers['x-api-key'])
    try:
        UserAuthenticator(repo_dependable).authenticate(x_api_key)
        wallet = Wallet(user_key=x_api_key)
        Service(repo_dependable).create_wallet(wallet)
        usd = BitcoinToCurrency().convert(wallet.bitcoins)
        usd_wallet = UsdWallet(wallet_address=wallet.address,
                               bitcoins_balance=wallet.bitcoins,
                               usd_balance=usd)
        return {"usd_wallet": usd_wallet}
    except WebException as we:
        return we.json_response()
    # except ApiKeyWrong:
    #     return ApiKeyWrong().json_response()


# es shesacvlelia: query parameters ar unda iyos rogorc gavige. request-shi unda iyos es wallet from, to da amount.
@api.post("/transactions",
          status_code=201,
          response_model=TransactionItem,
          tags=["Transactions"])
def create_transaction(
        transaction: dict[str, UUID | float],
        request: Request,
        repo_dependable: RepositoryDependable
) -> JSONResponse:
    x_api_key = UUID(request.headers['x-api-key'])
    try:
        UserAuthenticator(repo_dependable).authenticate(x_api_key)
        wallet_from = transaction['address_from']
        wallet_to = transaction['address_to']
        send_amount = transaction['amount']
        Service(repo_dependable).transfer(wallet_from, wallet_to, send_amount, x_api_key)
        return JSONResponse(status_code=201, content={})
    except WebException as we:
        return we.json_response()
    # except ApiKeyWrong as e:
    #     return ApiKeyWrong().json_response()
    # except WalletAddressNotOwn:
    #     return WalletAddressNotOwn().json_response()
    # except SendAmountExceedsBalance:
    #     return SendAmountExceedsBalance().json_response()


@api.get(
    "/users/{user_key}/", status_code=200, response_model=UserItemEnvelope, tags=["Users"]
)
def read_one_user(
        user_key: UUID,
        request: Request,
        repo_dependable: RepositoryDependable
) -> dict[str, Entity] | JSONResponse:
    x_api_key = request.headers['x-api-key']
    try:
        UserAuthenticator(repo_dependable).authenticate(UUID(x_api_key))
        return {"user": Service(repo_dependable).read(user_key, "users")}
    except WebException as we:
        return we.json_response()
    # except DoesNotExistError:
    #     return DoesNotExistError(
    #         "User", "key", str(user_key)
    #     ).json_response()
    # except ApiKeyWrong:
    #     return ApiKeyWrong().json_response()


@api.get(
    "/wallets/{address}/", status_code=200, response_model=WalletItemEnvelope, tags=["Wallets"]
)
def read_wallet_address(
        address: UUID,
        request: Request,
        repo_dependable: RepositoryDependable
) -> dict[str, UUID | float] | JSONResponse:
    x_api_key = request.headers['x-api-key']
    try:
        UserAuthenticator(repo_dependable).authenticate(UUID(x_api_key))
        bitcoins = Service(repo_dependable).read_wallet_bitcoins(address, 'wallets', 'address')
        return {"wallet_address": address, 'bitcoins': bitcoins, 'usd': BitcoinToCurrency().convert(bitcoins)}
    except WebException as we:
        return we.json_response()
    # except DoesNotExistError:
    #     return DoesNotExistError(
    #         "Wallet", "address", str(address)
    #     ).json_response()
    # except ApiKeyWrong:
    #     return ApiKeyWrong.json_response()


@api.get(
    "/transactions", status_code=200, response_model=TransactionListEnvelope, tags=["transactions"]
)
def read_transactions(
        request: Request,
        repo_dependable: RepositoryDependable
) -> dict[str, list[Transaction]] | JSONResponse:
    x_api_key = UUID(request.headers['x-api-key'])
    try:
        UserAuthenticator(repo_dependable).authenticate(x_api_key)
        transactions = Service(repo_dependable).read_transactions(x_api_key)
        return {"transactions": transactions}
    except WebException as we:
        return we.json_response()
    # except ApiKeyWrong:
    #     return ApiKeyWrong().json_response()


@api.get(
    "/wallets/{address}/transactions", status_code=200, response_model=TransactionListEnvelope, tags=["transactions"]
)
def read_wallet_transactions(
        address: UUID,
        request: Request,
        repo_dependable: RepositoryDependable
) -> dict[str, list[Transaction]] | JSONResponse:
    x_api_key = UUID(request.headers['x-api-key'])
    try:
        UserAuthenticator(repo_dependable).authenticate(x_api_key)
        transactions = Service(repo_dependable).read_transactions_by_address(address)
        return {"transactions": transactions}
    except WebException as we:
        return we.json_response()
    # except ApiKeyWrong:
    #     return ApiKeyWrong().json_response()


@api.get(
    "/statistics", status_code=200, response_model=StatisticsItemEnvelope, tags=["statistics"]
)
def get_statistics(
        request: Request,
        repo_dependable: RepositoryDependable
) -> dict[str, Statistic] | JSONResponse:
    x_api_key = UUID(request.headers['x-api-key'])
    try:
        AdminAuthenticator().authenticate(x_api_key)
        curr_statistics = Service(repo_dependable).get_statistics()
        print("aaa", curr_statistics)
        return {"statistics": curr_statistics}
    except WebException as we:
        return we.json_response()
