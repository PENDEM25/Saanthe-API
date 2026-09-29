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

## Template for Future Entries

```
## [status] `METHOD /path`

**Purpose:** [User Story reference, one line]

[Algorithm, same 8-step shape]

**Key design notes:**
- [Anything genuinely new introduced by this endpoint]
- [Any bugs hit and how they were resolved]
```
