from dataclasses import dataclass
from uuid import UUID

from starlette.responses import JSONResponse


@dataclass
class WebException(Exception):
    status_code: int
    msg: str

    def json_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content={"error": {"message": self.msg}},
        )


class DoesNotExistError(WebException):
    def __init__(self, class_name: str, attr: str, inp: str):
        self.status_code = 404
        self.msg = class_name + " with " + attr + "<" + inp + "> does not exist."


class WalletLimitReached(WebException):
    def __init__(self) -> None:
        self.status_code = 409
        self.msg = "Wallet limit reached. Can't create any new wallets."


class ApiKeyWrong(WebException):
    def __init__(self, key: UUID) -> None:
        self.status_code = 404
        self.msg = f"API key {key} is wrong."


class WalletAddressNotOwn(WebException):
    def __init__(self, address: UUID) -> None:
        self.status_code = 403
        self.msg = (
            f"Error for address f{address}, can only transfer from own wallet addresses"
        )


class SendAmountExceedsBalance(WebException):
    def __init__(self, amount: float) -> None:
        self.status_code = 403
        self.msg = f"Send amount {amount} less than balance"


class UnsuccessfulRequest(Exception):
    pass


class DoesNotExistErrorTable(WebException):
    def __init__(
        self,
        table_name: str,
    ):
        self.status_code = 404
        self.msg = table_name + " does not exist."


class SameAddressTransferError(WebException):
    def __init__(
        self
    ):
        self.status_code = 404
        self.msg = 'not allowed to transfer to same address.'

