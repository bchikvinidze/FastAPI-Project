class DoesNotExistError(Exception):
    def msg(self, class_name: str, attr: str, inp: str) -> str:
        return class_name + " with " + attr + "<" + inp + "> does not exist."


class UndefinedTableException(Exception):
    pass


class UnsuccessfulRequest(Exception):
    pass


class WalletLimitReached(Exception):
    def msg(self) -> str:
        return "wallet limit reached. Can't create any new wallets."


class ApiKeyWrong(Exception):
    def msg(self) -> str:
        return "API key is wrong."

