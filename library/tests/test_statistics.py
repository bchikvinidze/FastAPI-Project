from starlette.testclient import TestClient


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

    response = client.get("/statistics")
    transaction_number = response.json()['count_transactions']
    platform_profit = response.json()['total_profit']
    # # observe post-transaction balances:
    # wallet_from_response = client.get(f"/wallets/{wallet_from}", headers={'x-api-key': api_key})
    # bitcoin_from_final = wallet_from_response.json()['bitcoins']
    # wallet_to_response = client.get(f"/wallets/{wallet_to}", headers={'x-api-key': api_key})
    # bitcoin_to_final = wallet_to_response.json()['bitcoins']

    assert transaction_response.status_code == 201
    assert transaction_response.json() == {}
    # assert wallet_from_response.status_code == 200
    # assert wallet_to_response.status_code == 200
    # assert bitcoin_from_final == bitcoin_from_initial - send_amount
    # assert bitcoin_to_final == bitcoin_to_initial + send_amount
