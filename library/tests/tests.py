import os
from random import choice
from string import ascii_uppercase
from unittest.mock import ANY
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from constants import DB_NAME
from library.core.bitcoin_converter import BitcoinToCurrency
from library.core.entities import User#Purchase, Receipt, Unit
from library.core.errors import DoesNotExistError
from library.core.serialization import SerializerForDB
from library.core.service import Service
from library.infra.repository.persistent_repo.repository import PersistentRepository
from library.tests.fakes import FakeProduct#, FakeUnit


# Users
def test_users_should_create(client: TestClient) -> None:
    response = client.post("/users")

    assert response.status_code == 201
    assert response.json() == {"user": {"key": ANY}}


def test_user_should_persist(client: TestClient) -> None:
    response = client.post("/users")
    user_key = response.json()["user"]["key"]

    response = client.get(f"/users/{user_key}")

    assert response.status_code == 200
    assert response.json() == {"user": {"key": ANY}}


def test_bitcoint_to_usd_api(client: TestClient) -> None:
    converter = BitcoinToCurrency()
    usd = converter.convert(10)

    assert usd > 0


def test_wallet_create(client: TestClient) -> None:
    response = client.post("/users")
    user_key = response.json()["user"]["key"]

    response = client.post(f"/wallets/{user_key}")

    assert response.status_code == 201
    assert response.json() == {"usd_wallet": {'wallet_address': ANY,
                                        'bitcoins_balance': 1.0,
                                        'usd_balance': ANY}}


def test_wallet_create_over_limit(client: TestClient) -> None:
    response = client.post("/users")
    user_key = response.json()["user"]["key"]

    _ = client.post(f"/wallets/{user_key}")
    _ = client.post(f"/wallets/{user_key}")
    _ = client.post(f"/wallets/{user_key}")
    response = client.post(f"/wallets/{user_key}")

    assert response.status_code == 409
    assert response.json() == {'error': {'message': "wallet limit reached. Can't create any new wallets."}}

