# Technical Design Doc
## Saanthe-API — v0.1 MVP

This document combines four things that are often separate at larger companies, condensed here per our agreed pace: **High-Level Design (HLD)**, **Database ERD**, **API Contract**, and **Security Design**. Together, this is the blueprint engineering (you) builds directly against — every table, endpoint, and rule below should trace back to a User Story or Business Rule already agreed in the Charter/User Stories docs.

---

## PART 1 — High-Level Design (HLD)

### 1.1 What "High-Level Design" means

Before writing code, we decide the *shape* of the system — its major pieces and how they talk to each other — without yet deciding exact database columns or endpoint URLs (that's Parts 2 and 3). Think of HLD as the floor plan of a house before you pick doorknobs.

### 1.2 The Request Lifecycle

Every action in Saanthe follows this path:

```
Client (curl / Postman / future frontend)
   │  sends HTTP request (e.g., POST /orders)
   ▼
FastAPI Router layer        ── receives the request, validates its shape (via Pydantic schemas)
   │
   ▼
Service layer                ── contains business logic ("can this user cancel this order?")
   │
   ▼
Repository layer             ── talks to the database (raw queries/ORM calls live here only)
   │
   ▼
PostgreSQL database           ── stores/retrieves the actual data
   │
   ▼  (response flows back up through the same layers, in reverse)
Client receives JSON response + HTTP status code
```

**Why layers, not one big file:** each layer has exactly one job. This is called **separation of concerns** — a core software design principle. Practically, it means: you can test business logic (Service layer) without needing a real database running (mock the Repository layer instead); you can swap PostgreSQL for another database later by only touching the Repository layer; and when something breaks, you know which layer to look in based on *what* broke (a validation error → Router; a business rule violation → Service; a query bug → Repository).

### 1.3 Folder Structure (confirmed from your original brief)

```
app/
    main.py                 # starts the FastAPI app, includes all routers

    routers/                # Part 3 (API Contract) lives here — one file per resource
        auth.py
        users.py
        products.py
        orders.py
        payments.py
        vendor.py

    services/               # business logic — the "rules" from the Charter live here
        auth_service.py
        user_service.py
        product_service.py
        order_service.py
        payment_service.py
        vendor_service.py

    models/                 # Part 2 (ERD) lives here — one file per database table
        user.py
        vendor_profile.py
        product.py
        order.py
        payment.py

    schemas/                # Pydantic models — define the exact shape of requests/responses
        user.py
        product.py
        order.py
        payment.py

    repositories/           # direct database access — no business logic here
        user_repository.py
        product_repository.py
        order_repository.py
        payment_repository.py

    database/
        connection.py       # sets up the connection to PostgreSQL

    core/
        security.py         # password hashing, token creation/verification

    tests/                  # pytest lives here, mirrors the app/ structure
```

**One new term:** **Pydantic** is a Python library FastAPI uses to define and automatically validate the exact "shape" of data — e.g., "an order request must have a list of items, each with a `product_id` (integer) and `quantity` (positive integer)." If a request doesn't match, FastAPI rejects it automatically with a clear error, before your code even runs. This is why `schemas/` is separate from `models/` — models define the *database* shape, schemas define the *API* shape, and they're often similar but not identical (e.g., a response schema might exclude the password hash entirely).

---

## PART 2 — Database ERD (Entity-Relationship Diagram)

### 2.1 Key terms, quickly

- **Entity/Table:** a category of thing we store (e.g., "Product"). Each row is one specific instance (one specific product).
- **Primary Key (PK):** a column that uniquely identifies each row — no two rows share one. Always an auto-incrementing `id` here, for simplicity.
- **Foreign Key (FK):** a column that points to another table's Primary Key — this is how relationships between tables are built (e.g., an order "points to" the user who placed it).
- **Cardinality:** describes *how many* of one thing relate to *how many* of another (one-to-one, one-to-many, many-to-many).

### 2.2 Entities and Relationships

```
users (1) ────────── (0 or 1) vendor_profiles
  │                          │
  │ (1 to many)              │ (1 to many)
  ▼                          ▼
orders                    products
  │ (1 to many)
  ▼
order_items ────────── (many to 1) products
  │
  │ (1 to many — see note below)
  ▼
payments
```

**Reading this:** one `user` may have zero or one `vendor_profiles` (Option B from our earlier discussion). One `user` can place many `orders`. One `vendor_profile` can have many `products`. One `order` contains many `order_items`, and each `order_item` points to exactly one `product`. One `order` can have multiple `payment` attempts (failed retries), but only one can ever be `SUCCESS` (enforced in the Service layer, per Business Rule #9).

### 2.3 Table Definitions

**`users`**
| Column | Type | Notes |
|---|---|---|
| id | integer, PK | auto-increment |
| name | string | |
| email | string, unique | enforced at DB level, not just app level |
| password_hash | string | never store raw passwords — see Part 4 |
| created_at | timestamp | |

**`vendor_profiles`**
| Column | Type | Notes |
|---|---|---|
| id | integer, PK | |
| user_id | integer, FK → users.id, **unique** | the `unique` constraint is what enforces "one vendor profile per user" (Option B) |
| business_name | string | optional display name for their "stall" |
| created_at | timestamp | |

**`products`**
| Column | Type | Notes |
|---|---|---|
| id | integer, PK | |
| vendor_profile_id | integer, FK → vendor_profiles.id | who owns/sells this |
| name | string | |
| description | text | |
| price | decimal | **never use floating-point for money** — decimal avoids rounding errors, an important detail for financial systems |
| stock_quantity | integer | |
| is_active | boolean | soft-delete flag (Business Rule #8) |
| created_at | timestamp | |

**`orders`**
| Column | Type | Notes |
|---|---|---|
| id | integer, PK | |
| buyer_user_id | integer, FK → users.id | who placed the order |
| status | enum/string | `PENDING`, `PAID`, `SHIPPED`, `CANCELLED` — matches the state machine in User Flows |
| total_amount | decimal | calculated server-side, never trusted from client (Business Rule #5) |
| created_at | timestamp | |

**`order_items`**
| Column | Type | Notes |
|---|---|---|
| id | integer, PK | |
| order_id | integer, FK → orders.id | |
| product_id | integer, FK → products.id | |
| quantity | integer | |
| unit_price_at_purchase | decimal | **important:** we store the price *at the time of purchase*, separate from the product's current price — otherwise, if a vendor changes a price later, historical orders would show the wrong amount. This is a real, common data-integrity bug in poorly-designed e-commerce systems. |

**`payments`**
| Column | Type | Notes |
|---|---|---|
| id | integer, PK | |
| order_id | integer, FK → orders.id | |
| status | enum/string | `SUCCESS`, `FAILED` |
| amount | decimal | |
| created_at | timestamp | |

*Note: `order_id` is NOT marked unique here — this deliberately allows multiple payment attempts (e.g., a failed attempt followed by a successful retry) to exist as separate rows, which is more accurate than overwriting a single row. The Service layer enforces "only one `SUCCESS` per order," not the database schema — this is a business rule, not a structural constraint.*

---

## PART 3 — API Contract

Each endpoint below traces back to a User Story (referenced in parentheses). Request/response bodies are simplified to key fields — exact Pydantic schemas get finalized when we implement.

| Method | Endpoint | Story | Request Body (key fields) | Success Response |
|---|---|---|---|---|
| POST | `/auth/register` | US-1 | name, email, password | 201, user (no password) |
| POST | `/auth/login` | US-2 | email, password | 200, access_token |
| POST | `/auth/logout` | US-4 | (token in header) | 200 |
| GET | `/users/me` | US-3 | (token in header) | 200, user profile |
| PUT | `/users/me` | US-3 | name, email (optional) | 200, updated profile |
| GET | `/products` | US-5 | (public, no auth required) | 200, list of active products |
| POST | `/orders` | US-6 | items: [{product_id, quantity}] | 201, order + total |
| PATCH | `/orders/{id}/cancel` | US-7 | — | 200, updated order |
| POST | `/orders/{id}/pay` | US-8 | — | 200/402, payment result |
| GET | `/orders` | US-9 | (token in header) | 200, own orders only |
| GET | `/payments` | US-9 | (token in header) | 200, own payments only |
| POST | `/vendor/profile` | US-10 | business_name (optional) | 201, vendor profile |
| POST | `/vendor/products` | US-11 | name, description, price, stock | 201, product |
| PUT | `/vendor/products/{id}` | US-11 | fields to update | 200, updated product |
| DELETE | `/vendor/products/{id}` | US-11 | — | 200 (soft delete → is_active=false) |
| GET | `/vendor/orders` | US-12 | (token in header) | 200, orders containing own products |
| GET | `/vendor/payments` | US-12 | (token in header) | 200, payments for own products |
| PATCH | `/vendor/orders/{id}/status` | US-13 | status | 200, updated order |
| GET | `/vendor/dashboard` | US-14 | (token in header) | 200, aggregate stats |

**A note on `402`:** this is a real (if rarely used) HTTP status code literally named "Payment Required" — a fitting, if slightly obscure, choice for a failed simulated payment.

---

## PART 4 — Security Design

### 4.1 Password Storage

Passwords are never stored as plain text or even encrypted (encryption implies something can be reversed/decrypted — we never want that for passwords). Instead, we use **hashing** — a one-way mathematical function that turns a password into a fixed-length string that can't practically be reversed. We'll use **bcrypt** (an industry-standard hashing algorithm designed specifically to be slow, which is a deliberate defense against attackers trying to guess passwords by brute force).

At login, we don't "decrypt" the stored hash — we hash the *submitted* password the same way and compare the two hashes. If they match, the password was correct.

### 4.2 Authentication: JWT

We'll use **JWT (JSON Web Token)** for authentication. A JWT is a signed piece of text the server gives the client after login, containing the user's ID (and possibly other claims) — the client sends it back on every subsequent request (typically in an `Authorization: Bearer <token>` header), and the server verifies its signature to confirm it's genuine and unmodified, without needing to look anything up in the database on every request.

**Trade-off worth knowing (referenced in US-4):** JWTs are **stateless** — the server doesn't store a list of "active" tokens, so there's no simple way to truly force-invalidate one before it naturally expires. For MVP, we'll set a reasonably short expiration (e.g., 1 hour) and treat "logout" as a client-side action (discard the token) rather than a true server-side invalidation. A production system needing real forced-logout would add a token blocklist (checked against on each request) — noted as a v1.x improvement, not needed for MVP.

### 4.3 Authorization: Ownership Checks

Since Saanthe uses ownership-based access control (not fixed roles — Business Rule #6/#7), every protected endpoint follows this pattern in the Service layer:
1. Identify the requesting user from their JWT
2. Fetch the resource they're trying to act on (an order, a product, etc.)
3. Compare: does this resource belong to this user (as buyer) or their vendor profile (as seller)?
4. If not, reject with `403 Forbidden` before any data is returned or modified

### 4.4 Input Validation

Handled largely "for free" by Pydantic schemas (Part 1.3) — malformed requests are rejected with `422` before reaching business logic. Business-*rule* validation (e.g., "is this order still `PENDING`?") happens in the Service layer, since it depends on stored data, not just the shape of the incoming request.

### 4.5 What's Explicitly Not Covered (MVP)

- Rate limiting (protecting against brute-force login attempts) — noted for v1.x
- HTTPS/TLS setup — relevant only once deployed (v1.0+), not for local development
- Real PII/compliance handling — out of scope per Charter Assumptions (no real user data)

---

## What's Next

This design doc is the reference point for the remaining SDLC steps: **Backlog + Test Plan** (breaking this into buildable tickets and defining what pytest will check), then **Implementation** — starting with Version 0.0 (architecture teaching) and Version 0.1 (the first running FastAPI endpoint).

Review each part above — the ERD (Part 2) is the one most worth double-checking carefully, since changing table structure after code exists is far more expensive than changing it now.
