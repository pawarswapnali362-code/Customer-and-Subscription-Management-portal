from starlette.testclient import TestClient
import pytest

from backend.database import SQLiteDatabase
from backend.main import create_app
from backend.sample_data import build_sample_data


@pytest.fixture()
def client():
    db = SQLiteDatabase(":memory:")
    for name, records in build_sample_data().items():
        if records:
            db[name].insert_many(records)
    app = create_app(database=db, seed_on_startup=False)
    with TestClient(app) as test_client:
        yield test_client, db
    db.close()


def sign_in(client):
    response = client.post("/api/auth/login", json={"user_id": "admin", "password": "admin"})
    assert response.status_code == 200


def test_api_requires_admin_login(client):
    test_client, _ = client
    assert test_client.get("/api/dashboard").status_code == 401


def test_local_sqlite_file_persists_records(tmp_path):
    database_path = tmp_path / "portal.sqlite3"
    first = SQLiteDatabase(database_path)
    first.customers.insert_one({"_id": "persistent-customer", "name": "Persistent Example"})
    first.close()

    reopened = SQLiteDatabase(database_path)
    assert reopened.customers.find_one({"_id": "persistent-customer"})["name"] == "Persistent Example"
    reopened.close()


def test_admin_demo_login_and_dashboard_metrics(client):
    test_client, _ = client
    sign_in(test_client)
    response = test_client.get("/api/dashboard")
    assert response.status_code == 200
    result = response.json()
    assert result["customer_total"] == 7
    assert result["customers"] == {"B2C": 3, "B2B": 2, "White-label Partner": 2}
    assert result["issues"]["total"] == 9
    assert result["partner_accounts"]["purchased"] == 253


def test_login_rejects_invalid_password(client):
    test_client, _ = client
    response = test_client.post("/api/auth/login", json={"user_id": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_white_label_activation_allows_available_account(client):
    test_client, _ = client
    sign_in(test_client)
    response = test_client.post("/api/activations", json={"customer_id":"cus-wl-1","product_id":"prod-2","identifier":"PARTNER-TEST-1"})
    assert response.status_code == 200
    allocation = test_client.get("/api/partners/cus-wl-1/allocations").json()
    assessment = next(item for item in allocation if item["product_id"] == "prod-2")
    assert assessment["activated"] == 1
    assert assessment["remaining"] == 49


def test_white_label_activation_blocks_over_allocation(client):
    test_client, db = client
    sign_in(test_client)
    db.entitlements.update_one({"_id":"ent-9"},{"$set":{"purchased":1}})
    db.activations.insert_one({"_id":"already-active","customer_id":"cus-wl-1","product_id":"prod-2","identifier":"PARTNER-ONLY","status":"Active"})
    response = test_client.post("/api/activations", json={"customer_id":"cus-wl-1","product_id":"prod-2","identifier":"PARTNER-EXTRA"})
    assert response.status_code == 409


def test_issue_resolution_sets_date_and_reopening_clears_date(client):
    test_client, _ = client
    sign_in(test_client)
    response = test_client.patch("/api/issues/ISS-0001", json={"status":"Resolved"})
    assert response.status_code == 200
    assert response.json()["resolved_at"]
    reopened = test_client.patch("/api/issues/ISS-0001", json={"status":"In Progress"})
    assert reopened.status_code == 200
    assert reopened.json()["resolved_at"] == ""


def test_payment_amount_must_be_nonnegative(client):
    test_client, _ = client
    sign_in(test_client)
    response = test_client.post("/api/payments", json={"customer_id":"cus-b2c-1","amount":-1,"status":"Paid"})
    assert response.status_code == 422


def test_deactivating_partner_account_releases_allocation(client):
    test_client, _ = client
    sign_in(test_client)
    response = test_client.patch("/api/activations/act-wl-1", json={"status":"Inactive"})
    assert response.status_code == 200
    allocation = test_client.get("/api/partners/cus-wl-1/allocations").json()
    learning = next(item for item in allocation if item["product_id"] == "prod-1")
    assert learning["remaining"] == 89
