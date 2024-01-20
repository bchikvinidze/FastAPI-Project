import os
from random import choice
from string import ascii_uppercase
from unittest.mock import ANY
from uuid import uuid4, UUID

import pytest
from fastapi.testclient import TestClient

from constants import DB_NAME, WALLET_CNT_LIMIT
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
    api_key = response.json()["user"]["key"]

    response = client.get(f"/users/{api_key}", headers={'x-api-key': api_key})

    assert response.status_code == 200
    assert response.json() == {"user": {"key": ANY}}


def test_bitcoin_to_usd_api(client: TestClient) -> None:
    converter = BitcoinToCurrency()
    usd = converter.convert(10)

    assert usd > 0


def test_wallet_create(client: TestClient) -> None:
    response = client.post("/users")
    api_key = response.json()["user"]["key"]

    response = client.post(f"/wallets", headers={'x-api-key': api_key})

    assert response.status_code == 201
    assert response.json() == {"usd_wallet": {'wallet_address': ANY,
                                        'bitcoins_balance': 1.0,
                                        'usd_balance': ANY}}


def test_wallet_create_over_limit(client: TestClient) -> None:
    response = client.post("/users")
    api_key = response.json()["user"]["key"]
    print('type is:', type(api_key))

    for i in range(0, WALLET_CNT_LIMIT+1):
        response = client.post(f"/wallets", headers={'x-api-key': api_key})

    assert response.status_code == 409
    assert response.json() == {'error': {'message': "wallet limit reached. Can't create any new wallets."}}


def test_wallet_unknown_key(client: TestClient) -> None:
    api_key = uuid4().__str__()
    response = client.post(f"/wallets", headers={'x-api-key': api_key})

    assert response.status_code == 404
    assert response.json() == {'error': {'message': f'User with key<{api_key}> does not exist.'}}

