from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request

from library.infra.repository.persistent_repo.repository import PersistentRepository


def get_repository(request: Request) -> PersistentRepository:
    return request.app.state.repo  # type: ignore


RepositoryDependable = Annotated[PersistentRepository, Depends(get_repository)]

