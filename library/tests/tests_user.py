from unittest.mock import ANY

import pytest
from fastapi.testclient import TestClient
from library.core.bitcoin_converter import BitcoinToCurrency


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


