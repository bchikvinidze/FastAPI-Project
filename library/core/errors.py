class DoesNotExistError(Exception):
    def msg(self, cls_name: str, attr: str, inp: str) -> str:
        return cls_name + " with " + attr + "<" + inp + "> does not exist."


class DuplicateError(Exception):
    def msg(self, cls_name: str, attr: str, inp: str) -> str:
        return cls_name + " with " + attr + "<" + inp + "> already exists."


class ClosedError(Exception):
    def msg(self, cls_name: str, attr: str, inp: str) -> str:
        return cls_name + " with " + attr + "<" + inp + "> is closed."


class UndefinedTableException(Exception):
    pass
