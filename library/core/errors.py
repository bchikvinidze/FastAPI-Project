# To do is: make all messages contain inputs and not just plain text.


class DoesNotExistError(Exception):
    def msg(self, class_name: str, attr: str, inp: str) -> str:
        return class_name + " with " + attr + "<" + inp + "> does not exist."


class WalletLimitReached(Exception):
    def msg(self) -> str:
        return "wallet limit reached. Can't create any new wallets."


class ApiKeyWrong(Exception):
    def msg(self) -> str:
        return "API key is wrong."


class WalletAddressNotOwn(Exception):
    def msg(self) -> str:
        return "Can only transfer from own wallet addresses"


class SendAmountExceedsBalance(Exception):
    def msg(self) -> str:
        return "Can only transfer if balance is more than send amount"


class UnsuccessfulRequest(Exception):
    pass
