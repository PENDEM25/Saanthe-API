# User Flows & Use Cases
## Saanthe — v0.1 MVP

This document maps each major action a user takes to: the **happy path** (everything goes right) and the **key failure paths** (what should happen when it doesn't). This is what turns into your API contract next — every step here becomes an endpoint or a validation rule.

**Format used:** `Actor → Action → System Response`, with error branches called out.

---

## A. Customer Flows

### A1. Registration
1. Customer submits: name, email, password
2. System checks email isn't already registered
3. System hashes password (never stores raw password — covered in Security Design)
4. System creates user record with role = `CUSTOMER`
5. System returns confirmation (not auto-logged-in for MVP — simpler)

**Error paths:**
- Email already exists → `409 Conflict` ("email already registered") — *409 is an HTTP status code meaning "this conflicts with existing data"*
- Missing/invalid fields (e.g., malformed email) → `422 Unprocessable Entity`
- Password too weak (define a minimum rule, e.g., 8+ chars) → `422`

---

### A2. Login
1. Customer submits email + password
2. System looks up user by email
3. System verifies password against stored hash
4. System issues an access token (mechanism decided in Security Design — likely JWT, which we'll explain when we get there)
5. Customer uses this token on all future requests

**Error paths:**
- Email not found OR password wrong → `401 Unauthorized` (deliberately vague — don't reveal *which* one was wrong; that's a security best practice to prevent attackers from guessing valid emails)
- Account deactivated (future feature, not MVP) → n/a for now

---

### A3. View / Update Profile
1. Customer (authenticated) requests own profile → system returns it
2. Customer submits updated fields (e.g., name) → system validates and saves

**Error paths:**
- No/invalid token → `401 Unauthorized`
- Attempt to change email to one that's already taken → `409`
- Attempt to change role (customer → vendor) → rejected, `403 Forbidden` (role changes aren't a customer-facing feature)

---

### A4. Browse Products
1. Customer requests product list (optionally filtered/paginated later — not MVP-critical)
2. System returns only **active** products (deactivated ones are hidden from customers)

**Error paths:**
- None significant — this is a public/low-risk read endpoint

---

### A5. Create an Order
1. Customer (authenticated) submits a list of `{product_id, quantity}` pairs
2. System validates: each product exists and is active
3. System calculates total server-side using **current** product prices (never trust a price sent by the client — Business Rule #5 from the Charter)
4. System creates order with status `PENDING`, plus order_items
5. System returns the created order with total

**Error paths:**
- Product doesn't exist or is deactivated → `400 Bad Request`, order not created
- Empty item list → `400` (Business Rule #4: at least one item)
- Not authenticated → `401`

---

### A6. Cancel an Order
1. Customer requests cancellation of their own order
2. System checks: order belongs to this customer AND status is `PENDING` (Business Rule #2)
3. System updates status to `CANCELLED`

**Error paths:**
- Order belongs to a different customer → `403 Forbidden`
- Order already paid/shipped → `409 Conflict` ("cannot cancel — already processed")
- Order doesn't exist → `404 Not Found`

---

### A7. Initiate Payment
1. Customer submits payment request for a specific order
2. System checks: order belongs to this customer, status is `PENDING`, and no successful payment already exists for it (Business Rule #3 & #9 — duplicate prevention)
3. System calls the **simulated payment processor** (a function that randomly or deterministically returns success/failure — we'll build this in v0.7)
4. **On success:** payment record created (status `SUCCESS`), order status → `PAID`
5. **On failure:** payment record created (status `FAILED`), order status stays `PENDING` (customer can retry)

**Error paths:**
- Order not `PENDING` or already paid → `409 Conflict`
- Order belongs to another customer → `403`
- Simulated processor failure → payment recorded as `FAILED`, order untouched, customer notified to retry

*This flow is the most important one in the whole project — it's where data consistency really matters. We'll spend real time here in LLD on "what if the server crashes between steps 3 and 4" (this is where the concept of a database transaction becomes essential, not just theoretical).*

---

### A8. View Order & Payment History
1. Customer requests their own orders/payments
2. System returns only records belonging to that customer (never another customer's — Business Rule #7)

**Error paths:**
- Not authenticated → `401`

---

### A9. Logout
1. Customer sends logout request
2. System invalidates the token (exact mechanism depends on auth approach chosen in Security Design — some token types can't truly be "invalidated" server-side, which is itself a good interview topic we'll cover)

---

## B. Vendor Flows

### B1. Vendor Login
Same mechanism as A2, but role must be `VENDOR`. Role is checked on every protected vendor endpoint afterward.

### B2. Create / Update / Delete (Deactivate) Product
1. Vendor (authenticated, role=VENDOR) submits product data (name, price, stock, description)
2. System validates and creates/updates record
3. "Delete" is actually a **soft delete** — set `is_active = false`, never hard-delete (Business Rule #8: historical orders must still reference valid product data)

**Error paths:**
- Non-vendor attempts this → `403 Forbidden`
- Invalid data (negative price, etc.) → `422`
- Product not found (for update/delete) → `404`

### B3. View Customers (Read-Only)
Vendor requests customer list → system returns basic info (never password hashes — Security Design will define exactly what fields are exposed).

### B4. View All Orders / Update Order Status
1. Vendor views all orders (across all customers — this is the vendor's privilege)
2. Vendor updates status (e.g., `PAID` → `SHIPPED`)

**Error paths:**
- Invalid status transition (e.g., `CANCELLED` → `SHIPPED`) → `409` — this means we'll need a defined **state machine** for order status (a concept we'll formalize in the Technical Design Doc)

### B5. View All Payments
Read-only, all payments across all customers.

### B6. Dashboard Statistics
1. Vendor requests dashboard
2. System computes (likely via SQL aggregation — `COUNT`, `SUM`):
   - total customers
   - total orders
   - successful payments count
   - failed payments count
   - total revenue (sum of successful payments only)

**Error paths:**
- Non-vendor access → `403`

---

## C. Order Status State Machine (derived from the flows above)

This is worth pulling out explicitly since multiple flows reference it:

```
PENDING → CANCELLED   (customer cancels, A6)
PENDING → PAID        (payment succeeds, A7)
PENDING → PENDING     (payment fails, stays put — A7)
PAID → SHIPPED         (vendor updates, B4)
```

No other transitions are valid. Any attempt outside this diagram is rejected with `409`. We'll enforce this formally in code later (not just "trust the frontend to send valid transitions").

---

## D. Summary Table — Actions → Endpoints (preview only, finalized in API Contract next)

| Actor | Action | Rough Endpoint (draft) |
|---|---|---|
| Customer | Register | `POST /auth/register` |
| Customer | Login | `POST /auth/login` |
| Customer | View/update profile | `GET/PUT /users/me` |
| Customer | Browse products | `GET /products` |
| Customer | Create order | `POST /orders` |
| Customer | Cancel order | `PATCH /orders/{id}/cancel` |
| Customer | Initiate payment | `POST /orders/{id}/pay` |
| Customer | View history | `GET /orders`, `GET /payments` |
| Vendor | Manage products | `POST/GET/PUT/DELETE /products/{id}` (vendor-scoped) |
| Vendor | View customers | `GET /vendor/customers` |
| Vendor | View/update orders | `GET /vendor/orders`, `PATCH /vendor/orders/{id}/status` |
| Vendor | View payments | `GET /vendor/payments` |
| Vendor | Dashboard | `GET /vendor/dashboard` |

---

## What's Next

**→ Technical Design Doc** (combined HLD + ERD + API Contract + Security). This is where the endpoints above get exact request/response shapes, the database tables get their columns and relationships defined, and we decide the actual auth mechanism.

Flag anything above that looks wrong before we lock in the state machine and business-rule enforcement — this table is the backbone everything else builds from.
