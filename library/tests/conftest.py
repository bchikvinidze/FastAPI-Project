import pytest
from fastapi.testclient import TestClient

from library.infra.repository.persistent_repo.repository import PersistentRepository
from library.runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())  # type: ignore


@pytest.fixture(autouse=True)
def cleaner() -> None:
    PersistentRepository().drop_all()
