'''

winaze feedback mivige rom radgan bevri testebia , calcalke failebshi sjobs mqondes.
axla ert failshia rom yvela ertad martivad gavushva magram bolosken calcalke failebad gadanawileba kargi ideaa
'''

import os
from random import choice
from string import ascii_uppercase
from unittest.mock import ANY
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from constants import WALLET_CNT_LIMIT
from library.core.bitcoin_converter import BitcoinToCurrency
from library.core.entities import Transaction


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

    response = client.post("/wallets", headers={'x-api-key': api_key})

    assert response.status_code == 201
    assert response.json() == {"usd_wallet": {'wallet_address': ANY,
                                              'bitcoins_balance': 1.0,
                                              'usd_balance': ANY}}


def test_wallet_create_over_limit(client: TestClient) -> None:
    response = client.post("/users")
    api_key = response.json()["user"]["key"]

    for i in range(0, WALLET_CNT_LIMIT + 1):
        response = client.post("/wallets", headers={'x-api-key': api_key})

    assert response.status_code == 409
    assert response.json() == {'error': {'message': "wallet limit reached. Can't create any new wallets."}}


def test_wallet_unknown_key(client: TestClient) -> None:
    api_key = uuid4().__str__()
    response = client.post("/wallets", headers={'x-api-key': api_key})

    assert response.status_code == 404
    assert response.json() == {'error': {'message': 'API key is wrong.'}}


def test_wallet_persists(client: TestClient) -> None:
    response = client.post("/users")
    api_key = response.json()["user"]["key"]
    response = client.post("/wallets", headers={'x-api-key': api_key})
    address = response.json()['usd_wallet']['wallet_address']

    response = client.get(f"/wallets/{address}", headers={'x-api-key': api_key})

    assert response.status_code == 200
    assert response.json() == {'wallet_address': address,
                               'bitcoins': ANY,
                               'usd': ANY}


# transaction tests are quite heavy - I'm not a huge fan.
def test_transaction_own(client: TestClient) -> None:
    # create user and wallets
    response = client.post("/users")
    api_key = response.json()["user"]["key"]

    # wallet number 1
    response = client.post("/wallets", headers={'x-api-key': api_key})
    resp_wallet = response.json()['usd_wallet']
    wallet_from = resp_wallet['wallet_address']
    bitcoin_from_initial = resp_wallet['bitcoins_balance']

    # wallet number 2
    response = client.post("/wallets", headers={'x-api-key': api_key})
    resp_wallet = response.json()['usd_wallet']
    wallet_to = resp_wallet['wallet_address']
    bitcoin_to_initial = resp_wallet['bitcoins_balance']

    # do transaction
    send_amount = 0.7
    transaction_response = client.post(f"/transactions",
                                       headers={'x-api-key': api_key},
                                       json={"address_from": wallet_from,
                                             "address_to": wallet_to,
                                             "amount": send_amount})

    # observe post-transaction balances:
    wallet_from_response = client.get(f"/wallets/{wallet_from}", headers={'x-api-key': api_key})
    bitcoin_from_final = wallet_from_response.json()['bitcoins']
    wallet_to_response = client.get(f"/wallets/{wallet_to}", headers={'x-api-key': api_key})
    bitcoin_to_final = wallet_to_response.json()['bitcoins']

    assert transaction_response.status_code == 201
    assert transaction_response.json() == {}
    assert wallet_from_response.status_code == 200
    assert wallet_to_response.status_code == 200
    assert bitcoin_from_final == bitcoin_from_initial - send_amount
    assert bitcoin_to_final == bitcoin_to_initial + send_amount


def test_transaction_send_from_not_own(client: TestClient) -> None:
    # should throw error if one tries sending from other user's wallet

    # create user and wallets 1
    response = client.post("/users")
    api_key = response.json()["user"]["key"]
    response = client.post("/wallets", headers={'x-api-key': api_key})
    resp_wallet = response.json()['usd_wallet']
    own_wallet = resp_wallet['wallet_address']

    # creation of another wallet for another user:
    response2 = client.post("/users")
    api_key2 = response2.json()["user"]["key"]
    response2 = client.post("/wallets", headers={'x-api-key': api_key2})
    resp_wallet2 = response2.json()['usd_wallet']
    foreign_wallet = resp_wallet2['wallet_address']

    # do transaction
    send_amount = 0.7
    transaction_response = client.post(f"/transactions",
                                       headers={'x-api-key': api_key},
                                       json={"address_from": foreign_wallet,
                                             "address_to": own_wallet,
                                             "amount": send_amount}
                                       )

    assert transaction_response.status_code == 403
    assert transaction_response.json() == {'error': {'message': "Can only transfer from own wallet addresses"}}


def test_transaction_overspend(client: TestClient) -> None:
    # create user and wallets
    response = client.post("/users")
    api_key = response.json()["user"]["key"]

    # wallet number 1
    response = client.post("/wallets", headers={'x-api-key': api_key})
    resp_wallet = response.json()['usd_wallet']
    wallet_from = resp_wallet['wallet_address']
    bitcoin_from_initial = resp_wallet['bitcoins_balance']

    # wallet number 2
    response = client.post("/wallets", headers={'x-api-key': api_key})
    resp_wallet = response.json()['usd_wallet']
    wallet_to = resp_wallet['wallet_address']
    bitcoin_to_initial = resp_wallet['bitcoins_balance']

    # do transaction
    send_amount = 10
    transaction_response = client.post(f"/transactions",
                                       headers={'x-api-key': api_key},
                                       json={"address_from": wallet_from,
                                             "address_to": wallet_to,
                                             "amount": send_amount}
                                       )

    assert transaction_response.status_code == 403
    assert transaction_response.json() == {
        'error': {'message': "Can only transfer if balance is more than send amount"}}


def test_transactions_get(client: TestClient) -> None:
    # create user and wallets
    response = client.post("/users")
    api_key = response.json()["user"]["key"]

    # wallet number 1
    response = client.post("/wallets", headers={'x-api-key': api_key})
    resp_wallet = response.json()['usd_wallet']
    wallet_from = resp_wallet['wallet_address']
    bitcoin_from_initial = resp_wallet['bitcoins_balance']

    # wallet number 2
    response = client.post("/wallets", headers={'x-api-key': api_key})
    resp_wallet = response.json()['usd_wallet']
    wallet_to = resp_wallet['wallet_address']
    bitcoin_to_initial = resp_wallet['bitcoins_balance']

    # do transaction
    send_amount = 0.7
    transaction_response = client.post(f"/transactions/{wallet_from}/{wallet_to}/{send_amount}",
                                       headers={'x-api-key': api_key})

    get_response = client.get("/transactions", headers={'x-api-key': api_key})

    assert get_response.status_code == 200
    assert get_response.json() == {'transactions': []} #jerjerobit ar maq daimplementirebuli


