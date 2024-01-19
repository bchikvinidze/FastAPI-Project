from fastapi import FastAPI

from library.infra.fastapi import api
from library.infra.repository.persistent_repo.repository import PersistentRepository


def init_app():  # type: ignore
    app = FastAPI()
    app.include_router(api)
    app.state.repo = PersistentRepository()

    return app
