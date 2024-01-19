import pytest
from fastapi.testclient import TestClient

from library.infra.repository.persistent_repo.repository import PersistentRepository
from library.runner.setup import init_app


# This filename is special in the way that fixture
# defined here can be seen form other files in this directory.
@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())  # type: ignore


# to make sure db is fresh for each test and deterministic
# in production system, will need to be modified by a test double db
# otherwise production data will be lost.
@pytest.fixture(autouse=True)
def cleaner() -> None:
    PersistentRepository().drop_all()
