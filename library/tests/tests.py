import os
from random import choice
from string import ascii_uppercase
from unittest.mock import ANY
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from constants import DB_NAME
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

"""
def test_get_all_units_on_empty(client: TestClient) -> None:
    response = client.get("/units")
    assert response.status_code == 200
    assert response.json() == {"units": []}


def test_units_list(client: TestClient) -> None:
    unit1 = FakeUnit().entity()
    unit2 = FakeUnit().entity()

    response = client.post("/units", json=unit1)
    unit_id1 = response.json()["unit"]["id"]
    response = client.post("/units", json=unit2)
    unit_id2 = response.json()["unit"]["id"]
    response = client.get("/units")

    assert response.status_code == 200
    assert response.json() == {
        "units": [{"id": unit_id1, **unit1}, {"id": unit_id2, **unit2}]
    }


def test_units_duplication(client: TestClient) -> None:
    unit = FakeUnit().entity()

    post_response = client.post("/units", json=unit)
    unit_name = post_response.json()["unit"]["name"]
    post_response2 = client.post("/units", json=unit)

    assert post_response2.status_code == 409
    assert post_response2.json() == {
        "error": {"message": f"Unit with name<{unit_name}> already exists."}
    }


# Products
def test_products_should_create(client: TestClient) -> None:
    # product has dependency on unit, because unit_id must exist.
    unit = FakeUnit().entity()
    post_response = client.post("/units", json=unit)
    unit_id = post_response.json()["unit"]["id"]
    product = FakeProduct().entity(unit_id)

    response = client.post("/products", json=product)

    assert response.status_code == 201
    assert response.json() == {"product": {"id": ANY, **product}}


def test_products_duplication(client: TestClient) -> None:
    # product has dependency on unit, because unit_id must exist.
    unit_id = client.post("/units", json=FakeUnit().entity()).json()["unit"]["id"]
    product = FakeProduct().entity(unit_id)

    prod_barcode = client.post("/products", json=product).json()["product"]["barcode"]
    response = client.post("/products", json=product)

    assert response.status_code == 409
    assert response.json() == {
        "error": {"message": f"Product with barcode<{prod_barcode}> already exists."}
    }


def test_products_should_not_read_unknown(client: TestClient) -> None:
    unknown_id = uuid4()
    response = client.get(f"/products/{unknown_id}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Product with id<{unknown_id}> does not exist."}
    }


def test_products_should_persist(client: TestClient) -> None:
    # product has dependency on unit, because unit_id must exist.
    unit_id = client.post("/units", json=FakeUnit().entity()).json()["unit"]["id"]
    product = FakeProduct().entity(unit_id)

    response = client.post("/products", json=product)
    prod_id = response.json()["product"]["id"]
    response = client.get(f"/products/{prod_id}")

    assert response.status_code == 200
    assert response.json() == {"product": {"id": prod_id, **product}}


def test_get_all_products(client: TestClient) -> None:
    unit_id = client.post("/units", json=FakeUnit().entity()).json()["unit"]["id"]
    product = FakeProduct().entity(unit_id)
    product_post_response = client.post("/products", json=product)

    response = client.get("/products")
    assert response.status_code == 200
    assert response.json() == {"products": [product_post_response.json()["product"]]}


def test_patch_product(client: TestClient) -> None:
    unit_id = client.post("/units", json=FakeUnit().entity()).json()["unit"]["id"]
    product = FakeProduct().entity(unit_id)

    response = client.post("/products", json=product)
    prod_id = response.json()["product"]["id"]
    prod_name = response.json()["product"]["name"]
    prod_barcode = response.json()["product"]["barcode"]
    prod_unit_id = response.json()["product"]["unit_id"]

    updated_price = 530.0
    patch_response = client.patch(f"/products/{prod_id}", json={"price": updated_price})

    assert patch_response.status_code == 200
    assert patch_response.json() == {}

    # check if update really happened:
    response = client.get(f"/products/{prod_id}")
    assert response.status_code == 200
    assert response.json() == {
        "product": {
            "id": prod_id,
            "name": prod_name,
            "barcode": prod_barcode,
            "unit_id": prod_unit_id,
            "price": updated_price,
        }
    }


def test_patch_product_nonexistent(client: TestClient) -> None:
    unknown_id = uuid4()
    patch_response = client.patch(f"/products/{unknown_id}", json={"price": 500.0})

    assert patch_response.status_code == 404
    assert patch_response.json() == {
        "error": {"message": f"Product with id<{unknown_id}> does not exist."}
    }


# Receipts
def test_receipts_should_create(client: TestClient) -> None:
    response = client.post("/receipts")

    assert response.status_code == 201
    assert response.json() == {
        "receipt": {"id": ANY, "products": ANY, "status": "open", "total": ANY}
    }


def test_receipt_persist(client: TestClient) -> None:
    response = client.post("/receipts")
    receipt_id = response.json()["receipt"]["id"]
    get_response = client.get(f"/receipts/{receipt_id}")

    assert get_response.status_code == 200
    assert get_response.json() == {
        "receipt": {
            "id": receipt_id,
            "products": [],
            "status": "open",
            "total": ANY,
        }
    }


def test_receipts_add_product(client: TestClient) -> None:
    response_receipt_post = client.post("/receipts")
    receipt_id = response_receipt_post.json()["receipt"]["id"]

    unit_id = client.post("/units", json=FakeUnit().entity()).json()["unit"]["id"]
    product_post_response = client.post("/products", json=FakeProduct().entity(unit_id))
    product_id = product_post_response.json()["product"]["id"]
    product_price = product_post_response.json()["product"]["price"]
    quantity = 10

    response = client.post(
        f"/receipts/{receipt_id}/products",
        json={"id": product_id, "quantity": quantity},
    )

    assert response.status_code == 201
    assert response.json() == {
        "receipt": {
            "id": receipt_id,
            "products": [
                {
                    "id": product_id,
                    "quantity": quantity,
                    "price": product_price,
                    "total": product_price * quantity,
                }
            ],
            "status": "open",
            "total": product_price * quantity,
        }
    }


def test_receipt_nonexistent(client: TestClient) -> None:
    unknown_id = uuid4()
    response = client.get(f"/receipts/{unknown_id}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Receipt with id<{unknown_id}> does not exist."}
    }


def test_receipt_patch(client: TestClient) -> None:
    response_receipt_post = client.post("/receipts")
    receipt_id = response_receipt_post.json()["receipt"]["id"]

    patch_response = client.patch(f"/receipts/{receipt_id}", json={"status": "closed"})

    assert patch_response.status_code == 200
    assert patch_response.json() == {}


def test_receipt_patch_nonexistent(client: TestClient) -> None:
    unknown_id = uuid4()
    patch_response = client.patch(f"/receipts/{unknown_id}", json={"status": "closed"})

    assert patch_response.status_code == 404
    assert patch_response.json() == {
        "error": {"message": f"Receipt with id<{unknown_id}> does not exist."}
    }


def test_receipt_successful_delete(client: TestClient) -> None:
    response_receipt_post = client.post("/receipts")
    receipt_id = response_receipt_post.json()["receipt"]["id"]

    delete_response = client.delete(f"/receipts/{receipt_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {}


def test_receipt_nonexistent_delete(client: TestClient) -> None:
    unknown_id = uuid4()
    delete_response = client.delete(f"/receipts/{unknown_id}")

    assert delete_response.status_code == 404
    assert delete_response.json() == {
        "error": {"message": f"Receipt with id<{unknown_id}> does not exist."}
    }


def test_receipt_closed_delete(client: TestClient) -> None:
    response_receipt_post = client.post("/receipts")
    receipt_id = response_receipt_post.json()["receipt"]["id"]
    _ = client.patch(f"/receipts/{receipt_id}", json={"status": "closed"})
    delete_response = client.delete(f"/receipts/{receipt_id}")

    assert delete_response.status_code == 403
    assert delete_response.json() == {
        "error": {"message": f"Receipt with id<{receipt_id}> is closed."}
    }


def test_sales(client: TestClient) -> None:
    # prepare an example of store action:
    response_receipt_post = client.post("/receipts")
    receipt_id = response_receipt_post.json()["receipt"]["id"]

    unit_id = client.post("/units", json=FakeUnit().entity()).json()["unit"]["id"]

    # insert product 1:
    product_post_response1 = client.post(
        "/products", json=FakeProduct().entity(unit_id)
    )
    product_id1 = product_post_response1.json()["product"]["id"]
    product_price1 = product_post_response1.json()["product"]["price"]
    quantity1 = 10

    # insert product 2:
    product_post_response2 = client.post(
        "/products", json=FakeProduct().entity(unit_id)
    )
    product_id2 = product_post_response2.json()["product"]["id"]
    product_price2 = product_post_response2.json()["product"]["price"]
    quantity2 = 3

    # add products to the receipt:
    _ = client.post(
        f"/receipts/{receipt_id}/products",
        json={"id": product_id1, "quantity": quantity1},
    )
    _ = client.post(
        f"/receipts/{receipt_id}/products",
        json={"id": product_id2, "quantity": quantity2},
    )

    # create another receipt:
    response_receipt_post = client.post("/receipts")
    _ = response_receipt_post.json()["receipt"]["id"]

    _ = client.patch(f"/receipts/{receipt_id}", json={"status": "closed"})

    response_sales = client.get("/sales")

    assert response_sales.status_code == 200
    assert response_sales.json() == {
        "sales": {
            "n_receipts": 1,
            "revenue": product_price2 * quantity2 + product_price1 * quantity1,
        }
    }


def test_serialize() -> None:
    receipt_id = uuid4()
    purchase = Purchase(
        id=uuid4(), quantity=2, price=1.1, total=3.1, receipt_id=receipt_id
    )
    result = SerializerForDB().serialize(
        "Purchases",
        purchase,
        columns=["id", "quantity", "price", "total", "receipt_id"],
    )
    assert result == {
        "id": ANY,
        "price": 1.1,
        "quantity": 2,
        "receipt_id": str(receipt_id),
        "total": 3.1,
    }


def test_deserialize() -> None:
    purchase = Purchase(id=uuid4(), quantity=20, price=11, total=0, receipt_id=uuid4())
    serialized = SerializerForDB().serialize(
        "Purchases",
        purchase,
        columns=["id", "quantity", "price", "total", "receipt_id"],
    )
    deserialized = SerializerForDB().deserialize("Purchases", serialized)
    assert deserialized == purchase


def test_persistent_init() -> None:
    _ = PersistentRepository()
    assert os.path.exists(DB_NAME + ".db")


def test_persistent_insert() -> None:
    db = PersistentRepository()
    unit = Unit(name="".join(choice(ascii_uppercase) for i in range(30)))
    unit_id = unit.id
    table_name = "units"
    Service(db).create_with_dupe_check(unit, table_name)
    assert Service(db).read(unit_id, table_name) == unit


def test_persistent_update() -> None:
    db = PersistentRepository()
    unit = Unit(name="".join(choice(ascii_uppercase) for i in range(30)))
    unit_id = unit.id
    table_name = "units"
    Service(db).create_with_dupe_check(unit, table_name)
    new_name = "kilogram"
    Service(db).update(unit_id, table_name, {"name": new_name})

    unit.name = new_name
    assert Service(db).read(unit_id, table_name) == unit


def test_persistent_delete() -> None:
    db = PersistentRepository()
    rec_id = uuid4()
    receipt = Receipt(id=rec_id, status="open", products=[], total=100.0)
    table = "receipts"
    db.create_without_dupe_check(receipt, table)
    db.delete(receipt.id, table)

    with pytest.raises(DoesNotExistError):
        db.read_one(receipt.id, table)
"""