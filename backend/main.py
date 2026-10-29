from __future__ import annotations

import os
from datetime import date
from contextlib import asynccontextmanager, nullcontext
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from backend.database import SQLiteDatabase, get_db
from backend.sample_data import build_sample_data

load_dotenv()

COLLECTIONS = {"customers", "products", "users", "entitlements", "payments", "activations", "issues"}
STATUSES = {"customers": {"Active", "Inactive", "Suspended"}, "entitlements": {"Active", "Inactive", "Expired", "Suspended"}, "payments": {"Pending", "Paid", "Failed", "Partially Paid", "Refunded"}, "activations": {"Active", "Inactive", "Suspended"}, "issues": {"Open", "In Progress", "Resolved", "Closed"}}


def create_app(database: SQLiteDatabase | None = None, seed_on_startup: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        if seed_on_startup:
            db = database if database is not None else get_db()
            db.products.create_index("code", unique=True)
            db.customers.create_index("email", unique=True)
            if db.products.count_documents({}) == 0:
                for name, records in build_sample_data().items():
                    if records:
                        db[name].insert_many(records)
        yield

    app = FastAPI(title="Cliently Customer Portal API", version="1.0.0", lifespan=lifespan)
    app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "local-demo-secret-change-before-deploy"), same_site="lax", https_only=False)
    app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    def db_dependency():
        return database if database is not None else get_db()

    def require_admin(request: Request):
        if not request.session.get("admin"):
            raise HTTPException(status_code=401, detail="Please sign in to continue.")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/auth/me")
    def auth_me(request: Request):
        return {"authenticated": bool(request.session.get("admin")), "user_id": request.session.get("admin")}

    @app.post("/api/auth/login")
    def login(payload: dict[str, Any], request: Request):
        user_id = os.getenv("ADMIN_USER_ID", "admin")
        password = os.getenv("ADMIN_PASSWORD", "admin")
        if payload.get("user_id") != user_id or payload.get("password") != password:
            raise HTTPException(status_code=401, detail="Incorrect user ID or password.")
        request.session["admin"] = user_id
        return {"authenticated": True, "user_id": user_id}

    @app.post("/api/auth/logout")
    def logout(request: Request):
        request.session.clear()
        return {"authenticated": False}

    @app.get("/api/dashboard", dependencies=[Depends(require_admin)])
    def dashboard(db=Depends(db_dependency)):
        customers = list(db.customers.find({}, {"type": 1, "status": 1}))
        subscriptions = list(db.entitlements.find({}, {"status": 1, "customer_id": 1, "product_id": 1}))
        payments = list(db.payments.find({}, {"amount": 1, "status": 1, "payment_date": 1, "reference": 1, "customer_id": 1}))
        allocations = list(db.entitlements.find({"purchased": {"$exists": True}}, {"purchased": 1, "customer_id": 1, "product_id": 1}))
        issues = list(db.issues.find({}, {"status": 1}))
        active_count = sum(x.get("status") == "Active" for x in subscriptions)
        partner_activated = sum(1 for x in db.activations.find({"status": "Active"}) if any(a["customer_id"] == x.get("customer_id") and a["product_id"] == x.get("product_id") for a in allocations))
        return {
            "customers": {kind: sum(x.get("type") == kind for x in customers) for kind in ("B2C", "B2B", "White-label Partner")},
            "customer_total": len(customers), "products": db.products.count_documents({}),
            "entitlements": {"active": active_count, "inactive": len(subscriptions) - active_count},
            "payments": {"received": sum(float(x.get("amount", 0)) for x in payments if x.get("status") == "Paid"), "outstanding": sum(float(x.get("amount", 0)) for x in payments if x.get("status") in {"Pending", "Partially Paid"}), "count": len(payments)},
            "partner_accounts": {"purchased": sum(int(x.get("purchased", 0)) for x in allocations), "activated": partner_activated, "remaining": max(0, sum(int(x.get("purchased", 0)) for x in allocations) - partner_activated)},
            "issues": {"total": len(issues), "open": sum(x.get("status") == "Open" for x in issues), "in_progress": sum(x.get("status") == "In Progress" for x in issues), "resolved": sum(x.get("status") == "Resolved" for x in issues)},
            "recent_payments": _serialize(list(db.payments.find().sort("payment_date", -1).limit(5))),
            "recent_issues": _serialize(list(db.issues.find().sort("reported_at", -1).limit(5))),
        }

    @app.get("/api/{resource}", dependencies=[Depends(require_admin)])
    def list_resource(resource: str, request: Request, db=Depends(db_dependency)):
        if resource not in COLLECTIONS:
            raise HTTPException(404, "Unknown resource")
        collection = _collection(db, resource)
        filters = {}
        for key in ("type", "status", "customer_id", "product_id", "severity"):
            value = request.query_params.get(key)
            if value:
                filters[key] = value
        query = request.query_params.get("q", "").strip()
        rows = list(collection.find(filters).sort("created_at", -1))
        if query:
            q = query.casefold()
            rows = [r for r in rows if any(q in str(r.get(k, "")).casefold() for k in ("name", "email", "_id", "title", "reference", "identifier", "code"))]
        if resource == "activations":
            for row in rows:
                row["partner"] = _partner_name(db, row.get("customer_id"))
        if resource == "customers":
            for row in rows:
                row["type"] = {"White-label Partner": "White-label Partner"}.get(row.get("type"), row.get("type"))
        return _serialize(rows)

    @app.post("/api/{resource}", dependencies=[Depends(require_admin)])
    def create_resource(resource: str, payload: dict[str, Any], db=Depends(db_dependency)):
        if resource not in COLLECTIONS:
            raise HTTPException(404, "Unknown resource")
        data = dict(payload)
        data.pop("_id", None)
        with (db.transaction() if resource == "activations" else nullcontext()):
            _validate(resource, data, db)
            data["_id"] = f"{resource[:-1] if resource.endswith('s') else resource}-{uuid4().hex[:10]}"
            data.setdefault("created_at", str(date.today()))
            if resource == "payments":
                data["currency"] = "INR"
            if resource == "issues":
                data.setdefault("reported_at", str(date.today()))
                data["resolved_at"] = str(date.today()) if data.get("status") == "Resolved" else ""
            if resource == "activations":
                data.setdefault("status", "Active")
                data.setdefault("activated_at", str(date.today()))
            try:
                _collection(db, resource).insert_one(data)
            except Exception as exc:
                raise HTTPException(409, "A record with the same unique identifier already exists.") from exc
        return _serialize(data)

    @app.patch("/api/{resource}/{record_id}", dependencies=[Depends(require_admin)])
    def update_resource(resource: str, record_id: str, payload: dict[str, Any], db=Depends(db_dependency)):
        if resource not in COLLECTIONS:
            raise HTTPException(404, "Unknown resource")
        if "_id" in payload:
            raise HTTPException(422, "Record identifiers cannot be changed.")
        data = dict(payload)
        with (db.transaction() if resource == "activations" else nullcontext()):
            _validate(resource, data, db, updating=True, record_id=record_id)
            if resource == "issues" and "status" in data:
                data["resolved_at"] = str(date.today()) if data["status"] == "Resolved" else ""
            if resource == "payments":
                data["currency"] = "INR"
            result = _collection(db, resource).find_one_and_update({"_id": record_id}, {"$set": data}, return_document=True)
        if result is None:
            raise HTTPException(404, "Record not found.")
        return _serialize(result)

    @app.delete("/api/{resource}/{record_id}", dependencies=[Depends(require_admin)])
    def delete_resource(resource: str, record_id: str, db=Depends(db_dependency)):
        if resource not in COLLECTIONS:
            raise HTTPException(404, "Unknown resource")
        relations = {"customers": ("users", "entitlements", "payments", "activations", "issues"), "products": ("entitlements", "payments", "activations", "issues")}
        if resource in relations and any(_collection(db, child).count_documents({"customer_id" if resource == "customers" else "product_id": record_id}) for child in relations[resource]):
            raise HTTPException(409, "This record is linked to other records and cannot be deleted. Deactivate it instead.")
        result = _collection(db, resource).delete_one({"_id": record_id})
        if not result.deleted_count:
            raise HTTPException(404, "Record not found.")
        return {"deleted": True}

    @app.get("/api/partners/{customer_id}/allocations", dependencies=[Depends(require_admin)])
    def partner_allocations(customer_id: str, db=Depends(db_dependency)):
        partner = db.customers.find_one({"_id": customer_id, "type": "White-label Partner"})
        if not partner:
            raise HTTPException(404, "White-label partner not found.")
        rows = []
        for entitlement in db.entitlements.find({"customer_id": customer_id, "purchased": {"$exists": True}}):
            product = db.products.find_one({"_id": entitlement["product_id"]}) or {}
            activated = db.activations.count_documents({"customer_id": customer_id, "product_id": entitlement["product_id"], "status": "Active"})
            rows.append({"product_id": entitlement["product_id"], "product_name": product.get("name", "Unknown product"), "purchased": entitlement.get("purchased", 0), "activated": activated, "remaining": max(0, int(entitlement.get("purchased", 0))-activated)})
        return rows

    @app.get("/api/customer-details/{customer_id}", dependencies=[Depends(require_admin)])
    def customer_details(customer_id: str, db=Depends(db_dependency)):
        customer = db.customers.find_one({"_id": customer_id})
        if not customer:
            raise HTTPException(404, "Customer not found.")
        detail = _serialize(customer)
        for resource in ("users", "entitlements", "payments", "activations", "issues"):
            detail[resource] = _serialize(list(_collection(db, resource).find({"customer_id": customer_id})))
        return detail

    return app


def _collection(db, resource: str):
    return getattr(db, resource)


def _serialize(value: Any):
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items() if k != "_id"} | ({"id": str(value["_id"])} if "_id" in value else {})
    return value


def _partner_name(db, customer_id):
    customer = db.customers.find_one({"_id": customer_id}, {"name": 1}) or {}
    return customer.get("name", "")


def _validate(resource, data, db, updating=False, record_id=None):
    if resource == "products":
        if not updating and db.products.count_documents({}) >= 5:
            raise HTTPException(422, "The portal supports a maximum of five products.")
        if not data.get("name") or not data.get("code"):
            raise HTTPException(422, "Product name and identifier are required.")
        if "default_limit" in data and int(data["default_limit"]) < 0:
            raise HTTPException(422, "Usage limit cannot be negative.")
    elif resource == "customers":
        if not updating and any(not data.get(field) for field in ("name", "email", "type")):
            raise HTTPException(422, "Name, email, and customer type are required.")
        if data.get("type") and data["type"] not in {"B2C", "B2B", "White-label Partner"}:
            raise HTTPException(422, "Choose B2C, B2B, or White-label Partner.")
    elif resource == "users":
        if not updating and not all(data.get(field) for field in ("customer_id", "name", "email")):
            raise HTTPException(422, "Organization, user name, and email are required.")
        if data.get("customer_id") and not db.customers.find_one({"_id": data["customer_id"], "type": "B2B"}):
            raise HTTPException(422, "Users must be associated with an existing B2B organization.")
    elif resource == "entitlements":
        if not updating and not all(data.get(field) for field in ("customer_id", "product_id", "status")):
            raise HTTPException(422, "Customer, product, and status are required.")
        if data.get("customer_id") and not db.customers.find_one({"_id": data["customer_id"]}):
            raise HTTPException(422, "Select an existing customer.")
        if data.get("product_id") and not db.products.find_one({"_id": data["product_id"]}):
            raise HTTPException(422, "Select an existing product.")
        if "limit" in data and int(data["limit"]) < 0:
            raise HTTPException(422, "Usage limit cannot be negative.")
        if "purchased" in data and int(data["purchased"]) < 0:
            raise HTTPException(422, "Purchased allocation cannot be negative.")
    elif resource == "payments":
        if not updating and not all(data.get(field) for field in ("customer_id", "amount", "status")):
            raise HTTPException(422, "Customer, amount, and payment status are required.")
        if "amount" in data and float(data["amount"]) < 0:
            raise HTTPException(422, "Payment amount cannot be negative.")
        if data.get("customer_id") and not db.customers.find_one({"_id": data["customer_id"]}):
            raise HTTPException(422, "Select an existing customer.")
        if data.get("product_id") and not db.products.find_one({"_id": data["product_id"]}):
            raise HTTPException(422, "Select an existing product.")
    elif resource == "activations":
        existing = db.activations.find_one({"_id": record_id}) if updating and record_id else None
        customer_id = data.get("customer_id")
        product_id = data.get("product_id")
        customer_id = customer_id or (existing or {}).get("customer_id")
        product_id = product_id or (existing or {}).get("product_id")
        if not updating and not all((customer_id, product_id, data.get("identifier"))):
            raise HTTPException(422, "Customer, product, and account identifier are required.")
        customer = db.customers.find_one({"_id": customer_id}) if customer_id else None
        if customer_id and not customer:
            raise HTTPException(422, "Select an existing customer.")
        if product_id and not db.products.find_one({"_id": product_id}):
            raise HTTPException(422, "Select an existing product.")
        if customer and customer["type"] == "White-label Partner" and data.get("status", (existing or {}).get("status", "Active")) == "Active":
            entitlement = db.entitlements.find_one({"customer_id": customer_id, "product_id": product_id, "purchased": {"$exists": True}, "status": "Active"})
            if not entitlement:
                raise HTTPException(422, "No active account allocation exists for this partner and product.")
            active_filter = {"customer_id": customer_id, "product_id": product_id, "status": "Active"}
            if record_id:
                active_filter["_id"] = {"$ne": record_id}
            active = db.activations.count_documents(active_filter)
            if active >= int(entitlement.get("purchased", 0)):
                raise HTTPException(409, "All purchased accounts for this product are activated.")
    elif resource == "issues":
        if not updating and not all(data.get(field) for field in ("customer_id", "title", "description", "severity", "status")):
            raise HTTPException(422, "Customer, title, description, severity, and status are required.")
        if data.get("customer_id") and not db.customers.find_one({"_id": data["customer_id"]}):
            raise HTTPException(422, "Select an existing customer.")
        if data.get("product_id") and not db.products.find_one({"_id": data["product_id"]}):
            raise HTTPException(422, "Select an existing product.")
        if data.get("severity") and data["severity"] not in {"Critical", "High", "Medium", "Low"}:
            raise HTTPException(422, "Choose a valid issue severity.")
        if data.get("status") and data["status"] not in {"Open", "In Progress", "Resolved", "Closed"}:
            raise HTTPException(422, "Choose a valid issue status.")

app = create_app()
