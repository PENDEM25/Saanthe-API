# API Endpoint Algorithms
## Saanthe-API — Running Reference

This document is updated immediately after each endpoint is built, while the reasoning is fresh. Each entry follows the same shape: Client → Router → Service → Repository → back up. Use this to recall *why* each endpoint works the way it does, not just *what* the code does.

---

## ✅ `GET /products`

**Purpose:** Browse all active products (User Story US-5). No authentication required, no request body.

```
1. Client sends: GET /products
        ↓
2. main.py has already registered products.router to handle /products
        ↓
3. ROUTER (app/routers/products.py)
   - No request body to validate — simplest possible request
   - Gets a database session via Depends(get_db)
   - Calls: product_service.get_all_active_products(db)
        ↓
4. SERVICE (app/services/product_service.py)
   - Thin pass-through — no business logic needed beyond "active" filtering
     (that filtering itself lives in the Repository, since it's a query concern)
   - Calls: product_repository.get_active_products(db)
        ↓
5. REPOSITORY (app/repositories/product_repository.py)
   - db.query(Product).filter(Product.is_active == True).all()
   - Returns a list of Product objects (or an empty list, if none exist)
        ↓
6. SERVICE receives the list, returns it straight back to the Router
        ↓
7. ROUTER formats it using response_model=list[ProductResponse]
   - Deliberately excludes vendor_profile_id (internal detail, not exposed)
   - Returns HTTP 200, with the JSON array
        ↓
8. Client receives: [] (or a list of product objects)
```

**Key design notes:**
- The Service layer is intentionally thin here — kept in place for pattern consistency, not because this specific endpoint needs real business logic.
- Bug encountered & fixed: SQLAlchemy's string-based `relationship("VendorProfile", ...)` on the `Product` model failed to resolve at runtime, because `main.py`'s import chain never touched the `VendorProfile` class. Fixed by explicitly importing all 6 models together in `main.py`, guaranteeing every class is loaded into memory before any relationship gets resolved.

---

## ✅ `POST /auth/register`

**Purpose:** Register a new user (User Story US-1). First endpoint with a request body, validation rules, and real business logic.

```
1. Client sends: POST /auth/register
   Body: {"name": "...", "email": "...", "password": "..."}
        ↓
2. main.py has already registered auth.router to handle /auth/register
        ↓
3. ROUTER (app/routers/auth.py)
   - FastAPI auto-validates the body against UserRegisterRequest (the Schema):
       - email must look like a real email (EmailStr)
       - password must be at least 8 characters (Field(min_length=8))
       - if either fails → auto-rejected with 422, before any custom code runs
   - Gets a database session via Depends(get_db)
   - Calls: user_service.register_user(db, name, email, password)
        ↓
4. SERVICE (app/services/user_service.py)
   - Calls user_repository.get_user_by_email(db, email) — duplicate check
   - IF a match exists → raises EmailAlreadyExistsError, stops immediately, nothing saved
   - IF no match → calls hash_password(password) — one-way bcrypt hash, never reversible
   - Calls user_repository.create_user(db, name, email, hashed_password)
        ↓
5. REPOSITORY (app/repositories/user_repository.py)
   - Creates a new User object in memory
   - db.add(new_user) — stages it (nothing saved yet)
   - db.commit() — runs the real INSERT INTO users (...) SQL
   - db.refresh(new_user) — reloads the object with the real auto-generated id and created_at
   - Returns the complete, saved User object
        ↓
6. SERVICE receives the saved User, returns it straight back to the Router
        ↓
7. ROUTER formats it using response_model=UserResponse
   - Deliberately excludes password_hash — not a field on UserResponse at all
   - Returns HTTP 201 Created
        ↓
8. Client receives: {"id": 1, "name": "Manoj", "email": "manoj@email.com"}

   ALTERNATE PATH — duplicate email:
   Step 4 raises EmailAlreadyExistsError
        ↓
   ROUTER catches it: except user_service.EmailAlreadyExistsError as e:
   Raises HTTPException(status_code=409, detail=str(e))
        ↓
   Client receives: 409 Conflict, with an error message
```

**Key design notes:**
- Password hashing happens in the **Service** layer, not the Repository — the Repository has no awareness that hashing even exists; it just saves whatever hash it's given.
- A **custom exception** (`EmailAlreadyExistsError`) is how a Service communicates a specific business-rule failure up to the Router, which then translates it into the correct HTTP status code. This pattern will repeat for every future business-rule violation (e.g., cancelling an already-paid order).
- Password rule (minimum 8 characters) lives in the **Schema**, not in `security.py` — `security.py` only knows how to hash/verify, never judges what counts as an acceptable password.
- Bugs encountered & fixed along the way:
  - `app/schemas/user.py` was written but never actually saved as a real file initially — caught via `ModuleNotFoundError`, fixed by recreating it properly.
  - `EmailStr` required an additional package (`email-validator`) not installed by default — fixed with `pip install 'pydantic[email]'`.

---

## ✅ `POST /auth/login`

**Purpose:** Authenticate an existing user and issue a JWT access token (User Story US-2). Introduces JWT for the first time.

```
1. Client sends: POST /auth/login
   Body: {"email": "...", "password": "..."}
        ↓
2. main.py has already registered auth.router to handle /auth/login
        ↓
3. ROUTER (app/routers/auth.py)
   - FastAPI auto-validates the body against UserLoginRequest (Schema)
   - Gets a database session via Depends(get_db)
   - Calls: user_service.login_user(db, email, password)
        ↓
4. SERVICE (app/services/user_service.py)
   - Calls user_repository.get_user_by_email(db, email)
   - Checks: does a user exist AND does verify_password(password, user.password_hash) succeed?
   - Deliberately uses ONE generic check for both "no such email" and "wrong password" —
     never reveals which one failed, preventing attackers from discovering valid emails
   - IF either fails → raises InvalidCredentialsError
   - IF both succeed → calls create_access_token(user.id), returns the signed JWT string
        ↓
5. REPOSITORY — only a read (get_user_by_email), no write involved this time
        ↓
6. SERVICE returns the raw token string back to the Router
        ↓
7. ROUTER wraps it in TokenResponse(access_token=token)
   - Returns HTTP 200 with {"access_token": "...", "token_type": "bearer"}
        ↓
8. Client receives the token, to be sent on all future authenticated requests
   (via an Authorization: Bearer <token> header — not yet built, needed for protected endpoints)

   ALTERNATE PATH — invalid credentials:
   Step 4 raises InvalidCredentialsError
        ↓
   ROUTER catches it: except user_service.InvalidCredentialsError as e:
   Raises HTTPException(status_code=401, detail=str(e))
```

**Key design notes:**
- **JWT structure proven directly:** decoded a real token's payload manually using Base64 — confirmed the payload (`sub`, `exp`) is plainly readable, NOT encrypted. Security comes entirely from the signature (third segment), which can't be forged without the server's `SECRET_KEY`.
- **Generic error message is a deliberate security choice** — same email-enumeration protection discussed in the original Security Design doc, now actually implemented.
- **`SECRET_KEY` is currently hardcoded** in `security.py` as a placeholder — flagged as needing to move to an environment variable before any real deployment (see Future Learning List).
- **Still missing, for later:** an actual dependency that reads the `Authorization` header, verifies the token, and identifies "who is making this request" — needed before building any endpoint that requires being logged in (e.g., `GET /users/me`, creating an order).
- Small bug caught mid-build: `pip install python-jose[cryptography]` failed under `zsh` due to unquoted square brackets being interpreted as a glob pattern — fixed by quoting: `pip install "python-jose[cryptography]"`.

---

## ✅ `GET /users/me`

**Purpose:** Return the logged-in user's own profile. First genuinely protected endpoint — proves the full JWT verification chain works.

```
1. Client sends: GET /users/me
   Header: Authorization: Bearer <token>
        ↓
2. ROUTER (app/routers/auth.py)
   - current_user: User = Depends(get_current_user)
   - FastAPI runs get_current_user BEFORE this function's body executes
        ↓
3. DEPENDENCY (app/core/dependencies.py — get_current_user)
   - OAuth2PasswordBearer automatically extracts the token from the Authorization header
   - Calls decode_access_token(token) → verifies signature + expiry, extracts user_id
   - IF invalid/expired → raises HTTPException(401) immediately, function body never runs
   - Calls user_repository.get_user_by_id(db, user_id)
   - IF no such user → raises HTTPException(401)
   - Returns the real User object
        ↓
4. ROUTER receives the User object as current_user, simply returns it
        ↓
5. Formatted via response_model=UserResponse (password_hash excluded, as always)
        ↓
6. Client receives: {"id": 5, "name": "Manoj", "email": "manoj@email.com"}

   ALTERNATE PATH — no/invalid token:
   Dependency raises HTTPException(401) before the route function ever runs
        ↓
   Client receives: 401, with an error detail
```

**Key design notes:**
- **`Depends(get_current_user)` is now a reusable building block** — every future endpoint requiring login (creating an order, viewing own orders, vendor profile management) will use this exact same pattern.
- **Tested both paths directly:** confirmed `401` with no token, confirmed correct profile returned with a valid token.
- Distinguishing insight confirmed during this build: `GET /products` remains public and untouched — protecting one endpoint does NOT retroactively protect others. Each endpoint's auth requirement is a deliberate, individual design choice.

---

## ✅ `GET /health`

**Purpose:** Report whether the application and its database connection are alive. A production/infrastructure pattern, not a business-logic endpoint.

```
1. Client sends: GET /health
        ↓
2. main.py has already registered health.router to handle /health
        ↓
3. ROUTER (app/routers/health.py) — deliberately skips Service AND Repository
   - Gets a database session via Depends(get_db) — same shared dependency as every other endpoint
   - Runs db.execute(text("SELECT 1")) directly — a throwaway query touching no real table
   - If it succeeds → returns {"status": "ok"}
   - If the database is unreachable → the execute() call itself throws, FastAPI auto-returns 500
        ↓
4. Client receives: {"status": "ok"}  (or a 500 if something is genuinely broken)
```

**Key design notes:**
- **Deliberately breaks the usual layering** — no Schema, no Service, no Repository. There's no business logic or specific table involved, so routing through those layers would add complexity with zero benefit. A legitimate, intentional exception, not a shortcut taken out of laziness.
- **Real-world purpose:** this is the endpoint automated infrastructure (load balancers, monitoring/alerting tools) would repeatedly call, in production, to detect outages automatically — the actual alerting/notification system itself is separate infrastructure, not something built here.
- Cheapest endpoint built so far — proof that the architecture allows shortcuts *when justified*, without breaking the overall pattern for everything else.

---

## ✅ `POST /vendor/profile`

**Purpose:** Let any logged-in user create a Vendor Profile, unlocking selling capability on the same account (User Story US-10). First endpoint to combine authentication with a write action, and the first real implementation of the single-identity model (Option B).

```
1. Client sends: POST /vendor/profile
   Header: Authorization: Bearer <token>
   Body: {"business_name": "..."} (optional field)
        ↓
2. ROUTER (app/routers/vendor.py)
   - current_user: User = Depends(get_current_user) — resolves and verifies identity first
   - FastAPI validates body against VendorProfileRequest
   - Calls: vendor_service.create_vendor_profile(db, current_user.id, request.business_name)
   - Critically: the user_id passed is ALWAYS current_user.id (from the verified token),
     NEVER anything the client could supply in the request body — prevents creating a
     profile on someone else's behalf
        ↓
3. SERVICE (app/services/vendor_service.py)
   - Calls vendor_repository.get_vendor_profile_by_user_id(db, user_id) — duplicate check
   - IF one exists → raises VendorProfileAlreadyExistsError, stops immediately
   - IF none exists → calls vendor_repository.create_vendor_profile(db, user_id, business_name)
        ↓
4. REPOSITORY (app/repositories/vendor_repository.py)
   - Creates a new VendorProfile object, db.add() / db.commit() / db.refresh()
   - Returns the saved object
        ↓
5. Formatted via response_model=VendorProfileResponse
   - Returns HTTP 201 Created

   ALTERNATE PATH — profile already exists:
   Service raises VendorProfileAlreadyExistsError
        ↓
   ROUTER catches it, raises HTTPException(status_code=409, detail=str(e))
```

**Key design notes:**
- **Application-level duplicate check backs up the database's own UNIQUE constraint** (on `vendor_profiles.user_id`) — same reasoning as `EmailAlreadyExistsError`: catching it here gives a clean `409` instead of a raw database `IntegrityError` bubbling up.
- **Identity never comes from client input** — `current_user.id` is the only source of truth for who owns the new profile, a deliberate security pattern worth remembering for every future "create something owned by me" endpoint (creating products, placing orders).
- **Tested both paths directly:** first creation succeeded (`201`, correct `user_id`), second attempt correctly rejected (`409`, "You already have a vendor profile").

---

## ✅ `POST /vendor/products`

**Purpose:** Let a vendor-profile holder list a new product for sale (User Story US-11). Introduces a new authorization tier: "logged in" is not enough — the user must specifically hold a Vendor Profile.

```
1. Client sends: POST /vendor/products
   Header: Authorization: Bearer <token>
   Body: {"name": "...", "description": "...", "price": 90.00, "stock_quantity": 1}
        ↓
2. ROUTER (app/routers/vendor.py)
   - current_user: User = Depends(get_current_user) — identity resolved and verified
   - FastAPI validates body against ProductCreateRequest
   - Calls: product_service.create_product(db, current_user.id, name, description, price, stock_quantity)
        ↓
3. SERVICE (app/services/product_service.py)
   - Calls vendor_repository.get_vendor_profile_by_user_id(db, user_id)
   - IF no vendor profile exists → raises VendorProfileRequiredError, stops immediately
   - IF one exists → translates user_id into vendor_profile.id (the actual Foreign Key
     Product needs), calls product_repository.create_product(db, vendor_profile.id, ...)
        ↓
4. REPOSITORY (app/repositories/product_repository.py)
   - Creates a new Product object, db.add() / db.commit() / db.refresh()
   - Returns the saved object
        ↓
5. Formatted via response_model=ProductResponse
   - Returns HTTP 201 Created

   ALTERNATE PATH — no vendor profile:
   Service raises VendorProfileRequiredError
        ↓
   ROUTER catches it, raises HTTPException(status_code=403, detail=str(e))
```

**Key design notes:**
- **New status code: `403 Forbidden`**, distinct from `401 Unauthorized`. The user IS correctly authenticated (401 would mean "we don't know who you are") — they're simply not PERMITTED to do this specific action yet (no vendor profile). This 401-vs-403 distinction is a common interview question.
- **The Service performs a translation step** that's easy to overlook: the Router only ever knows `current_user.id` (a `users.id`), but `Product` needs a `vendor_profile_id`. The Service looks up the correct `vendor_profile.id` before handing off to the Repository — the Repository never has to know this translation happened.
- **Full loop tested and confirmed:** created a real product as an authenticated vendor, then confirmed it immediately appeared in the public, unauthenticated `GET /products` response — proving the core marketplace mechanic (list → browse) works end-to-end for the first time.
- **Still deferred to later:** `stock_quantity` has no upper sanity bound, and there's no check yet preventing negative values beyond the database's own CHECK constraint (which would reject it, but with a raw error, not yet a clean validated rejection at the Schema level — worth a `Field(ge=0)` addition later if desired).

---

## ✅ `POST /orders`

**Purpose:** Create a multi-item order with server-side price calculation and atomic stock reservation (User Story US-6). First endpoint requiring a true multi-step database transaction — breaks the usual per-function-commit pattern deliberately.

```
1. Client sends: POST /orders
   Header: Authorization: Bearer <token>
   Body: {"items": [{"product_id": 1, "quantity": 1}, ...]}
        ↓
2. ROUTER (app/routers/orders.py)
   - current_user resolved via Depends(get_current_user)
   - Body validated against OrderCreateRequest (quantity > 0, at least 1 item)
   - Calls: order_service.create_order(db, current_user.id, request.items)
        ↓
3. SERVICE (app/services/order_service.py) — the orchestrator, inside one try block
   - For EACH item:
       - order_repository.get_product_for_update() — locks the row (.with_for_update())
       - Checks product exists, is active, and has enough stock
       - IF any check fails → raises ProductNotFoundError or InsufficientStockError immediately
       - Decrements stock IN MEMORY (not committed yet), accumulates running total
   - Only after ALL items pass: order_repository.create_order() — stages the order (flush, no commit)
   - Then creates each order_item — stages them too (no commit)
   - db.commit() — ONE commit, finalizing order + all items + all stock decrements together
   - On ANY exception anywhere above → db.rollback(), re-raise — nothing partial survives
        ↓
4. REPOSITORY — functions use db.flush(), never db.commit() — the Service alone decides
   when to finalize
        ↓
5. Formatted via response_model=OrderResponse
   - Returns HTTP 201 Created, status: "PENDING"

   ALTERNATE PATHS:
   - Product missing/inactive → 404
   - Insufficient stock → 409, and the entire attempt rolls back (confirmed: a failed
     second order attempt left stock at exactly 0, not negative, and created no phantom order)
```

**Key design notes:**
- **Deliberate break from the per-function-commit pattern** used in every prior endpoint — Repository functions here only stage changes (`add`/`flush`); the Service is the single place that calls `db.commit()` or `db.rollback()`. This is the correct, necessary shape for any multi-step write, not a one-off exception.
- **Row-level locking (`.with_for_update()`)** implemented exactly as flagged — prevents two concurrent requests from both reading stale stock and both succeeding on the last unit of inventory.
- **Price taken from the live `product.price` at the moment of order, stored separately in `unit_price_at_purchase`** — matches the original ERD design decision (price history must stay frozen even if the vendor changes it later).
- **Tested directly:** successful order correctly decremented stock (1 → 0); a second attempt on the now-empty stock was cleanly rejected with `409`, with no partial data left behind.

---

## ✅ `POST /orders/{order_id}/pay`

**Purpose:** Process a simulated payment for an existing order (User Story US-8). Implements idempotency, ownership verification, and atomic order-status update together.

```
1. Client sends: POST /orders/{order_id}/pay
   Header: Authorization: Bearer <token>
        ↓
2. ROUTER (app/routers/orders.py)
   - current_user resolved via Depends(get_current_user)
   - Calls: payment_service.process_payment(db, order_id, current_user.id)
        ↓
3. SERVICE (app/services/payment_service.py)
   - Fetches the order; IF missing → raises OrderNotFoundError (404)
   - Ownership check: order.buyer_user_id != user_id → raises OrderNotOwnedError (403)
     (prevents paying for someone ELSE's order, even with a guessed valid order_id)
   - IDEMPOTENCY CHECK: looks for an existing SUCCESS payment on this order
     IF found → returns it immediately, no new charge attempted, function exits here
   - IF order.status is not "PENDING" (e.g., already PAID, or CANCELLED) → raises
     OrderNotPayableError (409)
   - Simulated processor: random.choice() → ~75% success rate
   - try block:
       - IF success → creates a SUCCESS payment row AND updates order.status to "PAID"
       - IF failure → creates a FAILED payment row only (order stays PENDING, retryable)
       - db.commit() — both the payment record and the status change finalize TOGETHER
   - except → db.rollback(), re-raise
        ↓
4. Formatted via response_model=PaymentResponse
   - Returns HTTP 200 with the payment result (SUCCESS or FAILED)
```

**Key design notes:**
- **Idempotency proven directly, not just implemented:** called this endpoint twice in a row after a successful payment — both calls returned the exact same payment `id`, confirming no duplicate charge was processed.
- **Atomicity confirmed:** payment creation and order status update are committed in the same transaction — a crash between them is structurally impossible, not just unlikely.
- **Three distinct, correctly-chosen status codes for three distinct failure reasons:** `404` (order doesn't exist), `403` (exists, but isn't yours), `409` (exists, is yours, but isn't in a payable state) — a clean demonstration of choosing HTTP status codes by actual meaning, not arbitrarily.
- **The simulated processor's ~75% success rate was deliberately chosen** so both outcomes could be observed directly during testing, rather than assuming the logic works from reading the code alone.

---

## ✅ `PATCH /orders/{order_id}/cancel`

**Purpose:** Cancel a still-pending order, reversing its stock reservation (User Story US-7). First use of `PATCH` (a partial update) and the first endpoint to perform a true reverse-transaction.

```
1. Client sends: PATCH /orders/{order_id}/cancel
   Header: Authorization: Bearer <token>
        ↓
2. ROUTER (app/routers/orders.py)
   - current_user resolved via Depends(get_current_user)
   - Calls: order_service.cancel_order(db, order_id, current_user.id)
        ↓
3. SERVICE (app/services/order_service.py)
   - Fetches the order; IF missing → OrderNotFoundError (404)
   - Ownership check: order.buyer_user_id != user_id → OrderNotOwnedError (403)
   - STATE MACHINE CHECK: order.status != "PENDING" → OrderNotCancellableError (409)
     (enforces the ONLY valid transition is PENDING → CANCELLED — a PAID order
     cannot be cancelled this way)
   - try block:
       - Fetches all order_items for this order
       - For EACH item: restores the product's stock_quantity (locked via
         .with_for_update(), same race-condition protection as order creation)
       - Updates order.status to "CANCELLED"
       - db.commit() — stock restoration AND status change finalize together
   - except → db.rollback(), re-raise
        ↓
4. Formatted via response_model=OrderResponse
   - Returns HTTP 200 with the now-CANCELLED order
```

**Key design notes:**
- **This is a genuine reverse-transaction** — the mirror image of order creation's stock decrement. Same atomicity and locking requirements apply in reverse: stock restoration and status update must succeed or fail together.
- **State machine enforcement tested directly, both directions:** a `PENDING` order was successfully cancelled (confirmed `CANCELLED` status, confirmed stock restored from 3 back to 5 — exact units ordered, no over- or under-restoration); a `PAID` order was correctly rejected with `409`, proving the state machine isn't just documented, it's enforced.
- **First use of HTTP `PATCH`** — chosen deliberately over `PUT` or `POST`, since this is a partial update (just the status field), not a full resource replacement or creation.

---

## ✅ `GET /orders`

**Purpose:** Let a logged-in user view their own order history (User Story US-9). Simple, ownership-scoped read — same pattern as `GET /users/me`, applied to a list instead of a single record.

```
1. Client sends: GET /orders
   Header: Authorization: Bearer <token>
        ↓
2. ROUTER (app/routers/orders.py)
   - current_user resolved via Depends(get_current_user)
   - Calls: order_service.get_my_orders(db, current_user.id)
        ↓
3. SERVICE — thin pass-through, same shape as get_all_active_products
   - Calls: order_repository.get_orders_by_user_id(db, user_id)
        ↓
4. REPOSITORY
   - db.query(Order).filter(Order.buyer_user_id == user_id).all()
   - Returns only orders belonging to this specific user — never another user's
        ↓
5. Formatted via response_model=list[OrderResponse]
   - Returns HTTP 200 with the user's own order list
```

**Key design notes:**
- **Ownership scoping happens at the query level**, not via a post-fetch filter — `WHERE buyer_user_id = user_id` is part of the SQL itself, meaning there's no risk of accidentally fetching-then-forgetting-to-filter another user's data.
- **Tested directly:** correctly returned both existing orders (one `PAID`, one `CANCELLED`) for the authenticated user, confirming historical status changes persist and display correctly through a simple read.

---


```
## [status] `METHOD /path`

**Purpose:** [User Story reference, one line]

[Algorithm, same 8-step shape]

**Key design notes:**
- [Anything genuinely new introduced by this endpoint]
- [Any bugs hit and how they were resolved]
```
