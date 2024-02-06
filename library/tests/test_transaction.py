from typing import Any, Tuple
from uuid import UUID

from fastapi.testclient import TestClient
from httpx import Response
from starlette.responses import JSONResponse


def create_user(client: TestClient) -> Any:
    response = client.post("/users")
    return response.json()["user"]["key"]


def create_wallet(client: TestClient, api_key: str) -> Tuple[UUID, float, JSONResponse]:
    response = client.post("/wallets", headers={"x-api-key": api_key})
    wallet_from = response.json()["usd_wallet"]["wallet_address"]
    bitcoin_from_initial = response.json()["usd_wallet"]["bitcoins_balance"]
    return wallet_from, bitcoin_from_initial, response.json()


def get_wallet_balance(
    client: TestClient, wallet_address: str, api_key: str
) -> Tuple[Response, float]:
    response = client.get(f"/wallets/{wallet_address}", headers={"x-api-key": api_key})
    return response, response.json()["bitcoins"]


def make_transaction(
    client: TestClient, api_key: str, address_from: str, address_to: str, amount: float
) -> Tuple[int, Response]:
    response = client.post(
        "/transactions",
        headers={"x-api-key": api_key},
        json={"address_from": address_from, "address_to": address_to, "amount": amount},
    )
    return response.status_code, response


def test_transaction_own(client: TestClient) -> None:
    api_key = create_user(client)
    wallet_from_response = create_wallet(client, api_key)
    wallet_to_response = create_wallet(client, api_key)
    send_amount = 0.7
    response = make_transaction(
        client,
        api_key,
        str(wallet_from_response[0]),
        str(wallet_to_response[0]),
        send_amount,
    )
    bitcoin_from_final = get_wallet_balance(
        client, str(wallet_from_response[0]), api_key
    )
    bitcoin_to_final = get_wallet_balance(client, str(wallet_to_response[0]), api_key)
    assert response[0] == 201
    assert bitcoin_from_final[0].status_code == 200
    assert bitcoin_to_final[0].status_code == 200
    assert bitcoin_from_final[1] == wallet_from_response[1] - send_amount
    assert bitcoin_to_final[1] == wallet_to_response[1] + send_amount


def test_transaction_send_from_not_own(client: TestClient) -> None:
    api_key1 = create_user(client)
    wallet_from, _, _ = create_wallet(client, api_key1)

    api_key2 = create_user(client)
    foreign_wallet_address, _, _ = create_wallet(client, api_key2)
    expected_msg = (
        f"Error for address f{foreign_wallet_address}, "
        f"can only transfer from own wallet addresses"
    )

    send_amount = 0.7
    transaction_response = make_transaction(
        client, api_key1, str(foreign_wallet_address), str(wallet_from), send_amount
    )

    assert transaction_response[0] == 403
    assert transaction_response[1].json() == {"error": {"message": expected_msg}}


def test_transaction_overspend(client: TestClient) -> None:
    api_key = create_user(client)
    wallet_from, _, _ = create_wallet(client, api_key)
    wallet_to, _, _ = create_wallet(client, api_key)

    send_amount = 10.0
    exp_msg = f"Send amount {send_amount} less than balance"
    transaction_response = make_transaction(
        client, api_key, str(wallet_from), str(wallet_to), send_amount
    )

    assert transaction_response[0] == 403
    assert transaction_response[1].json() == {"error": {"message": exp_msg}}


def test_transactions_get(client: TestClient) -> None:
    api_key = str(create_user(client))
    wallet_from, _, _ = create_wallet(client, api_key)
    wallet_to, _, _ = create_wallet(client, api_key)

    send_amount = 0.7
    make_transaction(client, api_key, str(wallet_from), str(wallet_to), send_amount)

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
