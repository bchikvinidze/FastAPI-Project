from fastapi.testclient import TestClient


def test_transaction_own(client: TestClient) -> None:
    response = client.post("/users")
    api_key = response.json()["user"]["key"]

    response = client.post("/wallets", headers={"x-api-key": api_key})
    resp_wallet = response.json()["usd_wallet"]
    wallet_from = resp_wallet["wallet_address"]
    bitcoin_from_initial = resp_wallet["bitcoins_balance"]

    response = client.post("/wallets", headers={"x-api-key": api_key})
    resp_wallet = response.json()["usd_wallet"]
    wallet_to = resp_wallet["wallet_address"]
    bitcoin_to_initial = resp_wallet["bitcoins_balance"]

    send_amount = 0.7
    transaction_response = client.post(
        "/transactions",
        headers={"x-api-key": api_key},
        json={
            "address_from": wallet_from,
            "address_to": wallet_to,
            "amount": send_amount,
        },
    )
    wallet_from_response = client.get(
        f"/wallets/{wallet_from}", headers={"x-api-key": api_key}
    )
    bitcoin_from_final = wallet_from_response.json()["bitcoins"]
    wallet_to_response = client.get(
        f"/wallets/{wallet_to}", headers={"x-api-key": api_key}
    )
    bitcoin_to_final = wallet_to_response.json()["bitcoins"]

    assert transaction_response.status_code == 201
    assert transaction_response.json() == {}
    assert wallet_from_response.status_code == 200
    assert wallet_to_response.status_code == 200
    assert bitcoin_from_final == bitcoin_from_initial - send_amount
    assert bitcoin_to_final == bitcoin_to_initial + send_amount


def test_transaction_send_from_not_own(client: TestClient) -> None:
    response = client.post("/users")
    api_key = response.json()["user"]["key"]
    response = client.post("/wallets", headers={"x-api-key": api_key})
    resp_wallet = response.json()["usd_wallet"]
    own_wallet = resp_wallet["wallet_address"]

    response2 = client.post("/users")
    api_key2 = response2.json()["user"]["key"]
    response2 = client.post("/wallets", headers={"x-api-key": api_key2})
    resp_wallet2 = response2.json()["usd_wallet"]
    foreign_wallet = resp_wallet2["wallet_address"]
    expected_msg = (
        f"Error for address f{foreign_wallet}, "
        f"can only transfer from own wallet addresses"
    )

    send_amount = 0.7
    transaction_response = client.post(
        "/transactions",
        headers={"x-api-key": api_key},
        json={
            "address_from": foreign_wallet,
            "address_to": own_wallet,
            "amount": send_amount,
        },
    )

    assert transaction_response.status_code == 403
    assert transaction_response.json() == {"error": {"message": expected_msg}}


def test_transaction_overspend(client: TestClient) -> None:
    response = client.post("/users")
    api_key = response.json()["user"]["key"]

    response = client.post("/wallets", headers={"x-api-key": api_key})
    resp_wallet = response.json()["usd_wallet"]
    wallet_from = resp_wallet["wallet_address"]

    response = client.post("/wallets", headers={"x-api-key": api_key})
    resp_wallet = response.json()["usd_wallet"]
    wallet_to = resp_wallet["wallet_address"]

    send_amount = 10.0
    exp_msg = f"Send amount {send_amount} less than balance"
    transaction_response = client.post(
        "/transactions",
        headers={"x-api-key": api_key},
        json={
            "address_from": wallet_from,
            "address_to": wallet_to,
            "amount": send_amount,
        },
    )

    assert transaction_response.status_code == 403
    assert transaction_response.json() == {"error": {"message": exp_msg}}


def test_transactions_get(client: TestClient) -> None:
    response = client.post("/users")
    api_key = response.json()["user"]["key"]

    response = client.post("/wallets", headers={"x-api-key": api_key})
    resp_wallet = response.json()["usd_wallet"]
    wallet_from = resp_wallet["wallet_address"]

    response = client.post("/wallets", headers={"x-api-key": api_key})
    resp_wallet = response.json()["usd_wallet"]
    wallet_to = resp_wallet["wallet_address"]

    send_amount = 0.7
    transaction_response = client.post(
        "/transactions",
        headers={"x-api-key": api_key},
        json={
            "address_from": wallet_from,
            "address_to": wallet_to,
            "amount": send_amount,
        },
    )
    assert transaction_response.status_code == 201
    get_response = client.get("/transactions", headers={"x-api-key": api_key})

    assert get_response.status_code == 200
    assert get_response.json() == {
        "transactions": [
            {
                "address_from": wallet_from,
                "address_to": wallet_to,
                "amount": send_amount,
            }
        ]
    }

    from_resp = client.get(
        f"/wallets/{wallet_from}/transactions",
        headers={"x-api-key": api_key},
    )
    to_resp = client.get(
        f"/wallets/{wallet_to}/transactions",
        headers={"x-api-key": api_key},
    )
    assert to_resp.json() == get_response.json()
    assert from_resp.json() == get_response.json()
    assert from_resp.status_code == 200
    assert to_resp.status_code == 200
