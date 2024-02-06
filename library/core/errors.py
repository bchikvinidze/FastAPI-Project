# To do is: make all messages contain inputs and not just plain text.
from dataclasses import dataclass

from starlette.responses import JSONResponse


@dataclass
class WebException(Exception):
    status_code: int
    msg: str

    def json_response(self) -> JSONResponse:
        return JSONResponse(status_code=self.status_code,
                            content={"error": {"message": self.msg}}, )


class DoesNotExistError(WebException):
    def __init__(self, class_name: str, attr: str, inp: str):
        self.status_code = 404
        self.msg = class_name + " with " + attr + "<" + inp + "> does not exist."


class WalletLimitReached(WebException):
    def __init__(self) -> None:
        self.status_code = 409
        self.msg = "wallet limit reached. Can't create any new wallets."


class ApiKeyWrong(WebException):
    def __init__(self) -> None:
        self.status_code = 404
        self.msg = "API key is wrong."


class WalletAddressNotOwn(WebException):
    def __init__(self) -> None:
        self.status_code = 403
        self.msg = "Can only transfer from own wallet addresses"


class SendAmountExceedsBalance(WebException):
    def __init__(self) -> None:
        self.status_code = 403
        self.msg = "Can only transfer if balance is more than send amount"


class UnsuccessfulRequest(Exception):
    pass


class DoesNotExistErrorTable(WebException):
    def __init__(self, table_name: str,):
        self.status_code = 404
        self.msg = table_name + " does not exist."
