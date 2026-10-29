# Cliently Customer Management Portal

An admin portal for managing B2C customers, B2B organizations and users, white-label partners, products, entitlements, payments, account activations and customer issues. The UI is built with Next.js; the API is Python/FastAPI; a local SQLite database persists the records. The interface displays amounts in INR (₹).

## Requirements

- Python 3.10+
- Node.js 20.9+
- No separate database server is needed; SQLite is included with Python.

## Run locally

1. Copy `.env.example` to `.env`. For local demo login, `admin` / `admin` are the default. These credentials are for local evaluation only; set unique `ADMIN_USER_ID`, `ADMIN_PASSWORD`, and `SESSION_SECRET` values before deployment.
2. In the repository root, create a Python virtual environment, activate it, install `pip install -r requirements.txt`, then run `uvicorn backend.main:app --reload --port 8000`.
3. In a second terminal, `cd frontend`, run `npm install`, then `npm run dev`.
4. Open `http://localhost:3000` and sign in with user ID `admin`, password `admin` (unless overridden in `.env`).

The API initializes five products and demo records on first start if the local database is empty. By default, data is stored in `data/cliently.sqlite3`; set `DATABASE_PATH` in `.env` to choose another file location. The parent directory is created automatically. Set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` only if the API is not at `http://localhost:8000`. SQLite is persistent across app restarts and requires no separate service.

## Tests and checks

Backend tests: from the root run `pip install -r requirements.txt`, then `pytest -q`. Each test uses an isolated in-memory SQLite database. Frontend checks: `cd frontend`, `npm install`, `npm run lint`, and `npm run build`.

## Core workflows

- **Dashboard:** counts by customer type, products, active/inactive entitlements, INR payments received/outstanding, partner account allocation totals, issue counts, recent payment and issue activity.
- **Customers:** filter/search customers by name, email or ID; create typed customer and organization records; open a customer profile with users, entitlements, payments, activations and issues.
- **B2B users:** add users only to B2B organizations, see organization membership and status.
- **Products:** manage up to five products and configurable usage units/default limits.
- **Entitlements:** associate a customer and product; record access state, quantities and usage limits.
- **White-label activation:** active partner activations cannot exceed the purchased quantity. Deactivating an account returns one slot for reuse. Allocation views show purchased, active and remaining counts.
- **Payments:** record amounts and payment status in INR. Dashboard totals aggregate paid transactions and pending/partially-paid amounts.
- **Issues:** filter by status and severity, change workflow state, and automatically set/clear `resolved_at` on resolution/reopening.

## Assumptions and design decisions

- Authentication is intentionally a small administrator session login for this evaluation; it is not a full identity/role system. The requested demo credentials are `admin` / `admin`; never deploy with defaults.
- A customer record represents an individual, organization, or white-label partner. B2B individual users are separate records linked to an organization. Shared payments/issues/product entitlements are linked to the customer record.
- White-label purchased allocations are stored as entitlements with a `purchased` quantity. Active activations count against this allocation; inactive ones do not. This makes deactivation release an allocation deterministically.
- Usage is a sample counter; no external product telemetry is integrated. Product and entitlement limits are separately configurable.
- Outstanding payment summary includes Pending and Partially Paid transaction amounts because this demonstration does not model partial-payment balance breakdowns.
- Product/customer references use application-level IDs stored with JSON documents in SQLite; the API validates references before writes. Related records are not hard-deleted when references exist; the API asks the administrator to deactivate instead.
- Five illustrative products, seven customers, six B2B users, ten payments and nine issues are seeded for demonstration. The sample dataset intentionally mixes customer, subscription, payment, activation and issue states.
- No payment gateway, email delivery, end-user portal, or live product integration is included.

## Demo media

See `screenshots/README.md` for suggested screenshots and walkthrough. Capture actual images from the running portal before submission; screenshots are not fabricated placeholders.

## GitHub submission

The project is ready for source control. Create a GitHub repository, initialize/commit this folder, and push it to that remote. No remote URL or GitHub credentials were supplied here, so repository publication remains a user step. Do not commit `.env` or other secrets.
