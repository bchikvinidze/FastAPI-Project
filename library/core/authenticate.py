from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from constants import ADMIN_API_KEY
from library.core.errors import ApiKeyWrong, DoesNotExistError
from library.infra.repository.repository import Repository


class Authenticator(Protocol):
    def authenticate(self, api_key: UUID) -> None:
        pass


@dataclass
class UserAuthenticator:
    repo: Repository

    def authenticate(self, api_key: UUID) -> None:
        try:
            _ = self.repo.read_one(api_key, "users", "key")
        except DoesNotExistError:
            raise ApiKeyWrong(api_key)


@dataclass
class AdminAuthenticator:
    __admin_api_key: str = ADMIN_API_KEY

    def authenticate(self, api_key: UUID) -> None:
        if str(api_key) != self.__admin_api_key:
            print("here")
            raise ApiKeyWrong(api_key)
