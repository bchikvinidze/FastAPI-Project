from typing import Any, Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse

from library.core.bitcoin_converter import BitcoinToCurrency
from library.core.entities import User, Wallet, UsdWallet
from library.core.errors import DoesNotExistError, WalletLimitReached
from library.core.service import Service
from library.infra.fastapi.base_models import UserItemEnvelope, UsdWalletItemEnvelope
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
        Service(repo_dependable).exists(x_api_key, 'users')
        wallet = Wallet(user_key=x_api_key)
        Service(repo_dependable).create_wallet(wallet)
        usd = BitcoinToCurrency().convert(wallet.bitcoins)
        usd_wallet = UsdWallet(wallet_address=wallet.address,
                               bitcoins_balance=wallet.bitcoins,
                               usd_balance=usd)
        return {"usd_wallet": usd_wallet}
    except WalletLimitReached:
        msg = WalletLimitReached().msg()
        return JSONResponse(
            status_code=409,
            content={"error": {"message": msg}},
        )
    except DoesNotExistError:
        msg = DoesNotExistError().msg("User", "key", str(x_api_key))
        return JSONResponse(
            status_code=404,
            content={"error": {"message": msg}},
        )


@api.get(
    "/users/{user_key}/", status_code=200, response_model=UserItemEnvelope, tags=["Users"]
)
def read_one_unit(
    user_key: UUID,
    request: Request,
    repo_dependable: RepositoryDependable
) -> dict[str, User] | JSONResponse:
    x_api_key = request.headers['x-api-key']
    try:
        # next line will throw doesnotexist error if api key not working.
        Service(repo_dependable).read(x_api_key, 'users')
        return {"user": Service(repo_dependable).read(user_key, "users")}
    except DoesNotExistError:
        msg = DoesNotExistError().msg("User", "key", str(user_key))
        return JSONResponse(
            status_code=404,
            content={"error": {"message": msg}},
        )

