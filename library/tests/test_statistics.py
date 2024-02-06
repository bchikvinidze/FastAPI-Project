from starlette.testclient import TestClient

from constants import ADMIN_API_KEY


def test_statistics(client: TestClient) -> None:
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

    statistics_response = client.get("/statistics", headers={'x-api-key': ADMIN_API_KEY})
    # print("here", statistics_response.json())
    transaction_number = statistics_response.json()['statistics']['count_transactions']
    platform_profit = statistics_response.json()['statistics']['total_profit']

    assert transaction_response.status_code == 201
    assert transaction_response.json() == {}
    assert statistics_response.status_code == 200
    assert transaction_number == 1
    assert platform_profit == 0
