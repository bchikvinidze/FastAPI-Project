from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from library.core.bitcoin_converter import BitcoinToCurrency
from library.core.entities import User, Wallet, UsdWallet
from library.core.errors import ClosedError, DoesNotExistError, DuplicateError
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


@api.post("/wallets/{user_key}", status_code=201, response_model=UsdWalletItemEnvelope, tags=["Wallets"])
def create_wallet(
    user_key: UUID, repo_dependable: RepositoryDependable
) -> dict[str, UsdWallet]:
    wallet = Wallet(user_key=user_key)
    Service(repo_dependable).create(wallet, "wallets")
    usd = BitcoinToCurrency().convert(wallet.bitcoins)
    usd_wallet = UsdWallet(wallet_address=wallet.address, bitcoins_balance=wallet.bitcoins, usd_balance=usd)
    return {"usd_wallet": usd_wallet}


@api.get(
    "/users/{user_key}", status_code=200, response_model=UserItemEnvelope, tags=["Users"]
)
def read_one_unit(
    user_key: UUID, repo_dependable: RepositoryDependable
) -> dict[str, User] | JSONResponse:
    try:
        return {"user": Service(repo_dependable).read(user_key, "users")}
    except DoesNotExistError:
        msg = DoesNotExistError().msg("User", "key", str(user_key))
        return JSONResponse(
            status_code=404,
            content={"error": {"message": msg}},
        )

