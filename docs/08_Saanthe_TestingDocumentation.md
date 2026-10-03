# Testing Documentation
## Saanthe-API — v0.9 Automated Test Suite

---

## 1. Overview

This document covers the complete automated test suite built for Saanthe-API, following manual `curl`-based testing of all 19 API endpoints. The goal of this phase was not to achieve exhaustive endpoint-by-endpoint coverage, but to convert the most important, previously manually-verified behaviors into permanent, repeatable, automated checks — with deliberate emphasis on the hardest, most differentiated parts of the system (atomic transactions, authorization, idempotency) rather than simple CRUD happy-paths.

**Result:** 10 automated tests, all passing, covering registration, authentication, authorization, transactional integrity, and payment idempotency.

---

## 2. Tools Used

| Tool | Purpose |
|---|---|
| **pytest** (v9.1.1) | The test framework — discovers, runs, and reports on test functions |
| **httpx** | Installed as a dependency of FastAPI's `TestClient`; handles the underlying HTTP simulation |
| **FastAPI `TestClient`** | Wraps the real, actual FastAPI `app` object and simulates requests to it directly in-process — no real network port, no separate Uvicorn process required, but still exercises real Routers, Services, Repositories, and a real PostgreSQL connection |

**Installation:**
```bash
pip install pytest httpx
```

---

## 3. Test File Structure

```
tests/
    __init__.py                      # marks tests/ as a Python package (empty, existence is the point)
    conftest.py                      # shared pytest configuration — the cleanup fixture lives here
    test_health.py                   # 1 test
    test_registration.py             # 2 tests
    test_login.py                    # 2 tests
    test_auth_protection.py          # 1 test
    test_orders.py                   # 2 tests
    test_authorization.py            # 1 test
    test_payment_idempotency.py      # 1 test
```

**Total: 10 tests.**

**Why `conftest.py` specifically:** pytest automatically recognizes this exact filename in the `tests/` folder and applies anything inside it (fixtures, shared configuration) to every test file in that folder, without needing to manually import it anywhere.

---

## 4. The Cleanup Fixture (`conftest.py`) — Explained in Detail

### The Problem It Solves

Every test that registers a user, creates a vendor profile, or places an order writes **real data** into the actual `saanthe_db` database — the same one used for manual testing. Without cleanup:
- Running the suite twice would fail on duplicate-email checks (since test users from the first run would still exist)
- The real database would accumulate permanent test clutter over time

### The Mechanism: `@pytest.fixture(autouse=True)`

A **fixture** is reusable setup/teardown code. `autouse=True` means it applies automatically to every test in the folder, without any test needing to explicitly request it.

```python
@pytest.fixture(autouse=True)
def cleanup_test_users():
    yield
    # cleanup code here
```

**The `yield` keyword is the key mechanism:** everything *before* `yield` would run as setup (unused here — no setup needed); everything *after* `yield` runs as cleanup, **after each test completes — regardless of whether that test passed or failed.** This mirrors the same `try/finally` reliability pattern already used in `get_db()` (`app/database/connection.py`).

### Why Cleanup Must Respect the Database's Own Dependency Order

Test data spans multiple related tables (`users → vendor_profiles → products`, and `users → orders → order_items/payments`). Deleting a `user` who still has a `vendor_profile` referencing them would violate the Foreign Key constraint — the same protection verified deliberately back when the schema was first built and tested.

**The cleanup fixture therefore deletes in the correct dependency order, every time:**
```
payments → order_items → orders → products → vendor_profiles → users
```

### How Test Data Is Identified

All test-created users use emails ending in `@test.com` (e.g., `testuser1@test.com`). The fixture filters specifically on this pattern (`User.email.like("%@test.com")`), ensuring cleanup never touches real data (like `manoj@email.com`) created during earlier manual testing sessions.

### Verified Behavior

The full suite was run twice in direct succession with no failures either time — confirming cleanup correctly removes all test-created rows (across all 6 tables) after every run, leaving the real database exactly as it was before testing began.

---

## 5. Test-by-Test Breakdown

### `test_health.py` — 1 test
- **`test_health_check`** — Calls `GET /health`, asserts `200` and the exact body `{"status": "ok"}`. The first test written; establishes the basic pattern every other test follows (call → assert).

### `test_registration.py` — 2 tests
- **`test_register_new_user_succeeds`** — Registers a new user, asserts `201`, and explicitly asserts `"password"` and `"password_hash"` are **absent** from the response — directly testing the Schema's deliberate field exclusion, not just that registration "worked."
- **`test_register_duplicate_email_fails`** — Registers a user, then attempts to register a second user with the *same* email, asserting `409`.

### `test_login.py` — 2 tests
- **`test_login_with_correct_credentials_succeeds`** — Registers then logs in, asserts `200` and that `access_token` is present with `token_type: "bearer"`.
- **`test_login_with_wrong_password_fails`** — Registers, then attempts login with an incorrect password, asserting `401`.

### `test_auth_protection.py` — 1 test
- **`test_get_my_profile_without_token_fails`** — Calls `GET /users/me` with no `Authorization` header at all, asserting `401`. Proves the endpoint is genuinely protected, not just that a valid token happens to work.

### `test_orders.py` — 2 tests (the most technically significant pair)
- **`test_create_order_with_sufficient_stock_succeeds`** — Full setup (register → login → create vendor profile → create product with known stock) then places a valid order, asserting `201` and `status: "PENDING"`.
- **`test_create_order_with_insufficient_stock_fails_and_does_not_change_stock`** — Creates a product with stock of 1, attempts to order 5, asserts `409` — **and then independently re-fetches the product via `GET /products` to confirm `stock_quantity` is still exactly 1.** This second assertion is the real point of the test: it proves the atomic transaction's rollback genuinely works, not merely that the request was rejected.

### `test_authorization.py` — 1 test
- **`test_cannot_cancel_another_users_order`** — Creates two fully independent users (User A and User B), has User A place a real order, then has User B — using their own genuinely valid token — attempt to cancel User A's order, asserting `403`. This specifically isolates the *ownership* check from the *authentication* check: User B is a real, logged-in user; the rejection must come from `order.buyer_user_id != user_id` in the Service layer.

### `test_payment_idempotency.py` — 1 test
- **`test_paying_twice_does_not_duplicate_payment`** — Full setup through order creation, then calls `/orders/{id}/pay` in a retry loop (up to 10 attempts) until a `SUCCESS` result is obtained — necessary because the simulated payment processor only succeeds ~75% of the time. Once successful, calls `/pay` a second time and asserts the returned payment `id` is **identical** to the first — proving no duplicate payment record was created.

---

## 6. Deliberate Scope Decisions

**This suite does not test all 19 endpoints individually.** This was a deliberate choice, not an oversight:

- Many endpoints (e.g., `GET /orders`, `GET /payments`, `GET /vendor/orders`) share the same fundamental pattern already proven by `test_health_check` and the order tests (simple read, correctly scoped by ownership) — re-testing that identical pattern repeatedly would add volume without adding genuine coverage value.
- The 10 tests were chosen specifically to span every *category* of behavior worth demonstrating: input validation, authentication, authorization, atomic transactions with rollback, and idempotency — the hardest and most interview-relevant aspects of the system.
- This matches real-world practice: test suites prioritize coverage of business-critical and failure-prone logic over exhaustively re-testing structurally identical, low-risk code paths.

---

## 7. Known, Harmless Warnings

Every run produces 7 deprecation warnings, none of which indicate a problem:

- **1 `StarletteDeprecationWarning`** — from FastAPI's `TestClient` internals (a dependency's own code, not ours), noting a future version will expect `httpx2` instead of `httpx`.
- **6 `PydanticDeprecatedSince20` warnings** — one per Schema file using `class Config: from_attributes = True`, Pydantic's older (but still fully functional) syntax; the newer equivalent is `model_config = ConfigDict(from_attributes=True)`. Flagged as a low-priority future cleanup, not a current bug.

---

## 8. How to Run the Suite

```bash
cd ~/Documents/Git_Projects/Saanthe-API
source venv/bin/activate
pytest
```

**Prerequisites:** PostgreSQL must be running (`brew services start postgresql@16`) — tests hit a real database connection, exactly like the application does when run normally. Uvicorn does **not** need to be running separately; `TestClient` bypasses the network layer entirely.

**Reading the output:**
- Each `.` represents one passing test; an `F` would represent a failure
- `collected N items` confirms how many total test functions pytest discovered across all files
- The final summary line (`N passed, M warnings in X.XXs`) is the authoritative pass/fail count

---

## 9. What's Next

With v0.9 complete, the remaining roadmap item is **v1.0 — Deployment**: Docker containerization, moving configuration (including the currently hardcoded `SECRET_KEY`) into environment variables, CI/CD pipeline setup, and cloud hosting.
