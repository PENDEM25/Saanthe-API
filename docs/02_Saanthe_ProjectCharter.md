# Project Charter
## Marketplace / Financial Transaction Portal — Version 0.1 (MVP)

---

### 1. Project Name

**"Saanthe"** (repo: `saanthe-api`) — a small marketplace platform where users can browse products, place orders, and pay for them (using a simulated payment system for learning purposes), and can optionally sell by creating a vendor profile, managing what's for sale and tracking how their sales are doing. The name draws from "santha" (సంత), a local-market word — a nod to the project being a from-scratch build of a real marketplace concept, not a generic tutorial clone.

---

### 2. Project Vision

Build a small, real-world-shaped backend system — not a simplified exercise — that teaches the full lifecycle of a production API: from a user's request, through the server, through business rules, into a database, and back out again, with real engineering practices (design docs, testing, version control) applied at every step.

The end goal isn't "a working app." The end goal is: **you can explain, defend, and rebuild every decision in this system — in an interview, on the job, or when teaching someone else — because you understand it, not because you memorized it.**

---

### 3. Business Problem

*(Even a learning project should be framed as solving a real problem — this is how you'll practice thinking like an engineer, not just a coder.)*

Small vendors (imagine a solo artisan, a small electronics reseller, a local service provider) need a simple way to:
- List what they sell
- Accept orders from customers online
- Get paid
- See basic stats about how their business is doing

Building this from scratch — instead of using Shopify/Etsy — teaches you exactly what those platforms are doing under the hood.

---

### 4. Target Users

Saanthe uses a **single-identity model**, matching the real "saanthe" (village market) concept it's named after: anyone who shows up can browse and buy, and anyone can also set up a stall and sell — often the same person, same visit.

| Concept | Description |
|---|---|
| **User** | Every account. Every user can browse products, place orders, and pay — this is the base identity, not a separate "customer role." |
| **Vendor Profile** | An *optional* extension any user can create when they choose to sell. Creating one unlocks product management, order/payment visibility for their own products, and dashboard stats — scoped to that vendor profile, not the whole platform. |

A user with no vendor profile behaves exactly like a traditional "customer." A user who creates a vendor profile gains selling capabilities **in addition to**, not instead of, their buying capabilities. This means the same person can sell a product and buy someone else's product, in the same account.

For MVP, assume a small number of vendor profiles overall (not yet optimized for large-scale multi-vendor discovery/search) — but structurally, many users can each independently hold a vendor profile from day one, which is a meaningfully different (and more accurate) model than "one vendor per system."

---

### 5. Business Goals

1. Provide a functioning order-and-payment loop end-to-end
2. Demonstrate secure handling of user accounts and role-based permissions
3. Demonstrate consistent, correct financial record-keeping (no lost or duplicated payments)
4. Provide basic business visibility (dashboard) for the vendor

---

### 6. MVP Scope

The MVP is intentionally **small and vertical** — meaning it should cover the *entire* flow (signup → browse → order → pay → see history) for a *narrow* feature set, rather than covering many features shallowly.

#### In-Scope Features (V0.1 – V0.9 per your roadmap)

**Every user (base capabilities — no vendor profile required):**
- Register / log in / log out
- View & update own profile
- Browse active products (across all vendors)
- Create an order (single or multiple items, potentially from different vendors)
- Cancel an order (only if not yet paid/shipped — business rule, defined below)
- Initiate a **simulated** payment
- View own order & payment history

**Additional capabilities once a user creates a Vendor Profile:**
- Create / read / update / deactivate **their own** products
- View orders and payments **for their own products only**
- Update status of orders containing their own products (e.g., mark shipped)
- View a dashboard scoped to their own vendor activity: total orders received, successful/failed payments, total revenue

*Note: a platform-wide admin view (across all vendors) is not in MVP scope — see below.*

#### Explicitly Out of Scope (for now)

- Real payment processing (Stripe/PayPal integration) — simulated only
- Multi-vendor support (many shops on one platform)
- Product reviews/ratings
- Search relevance/recommendation engines
- Shipping/logistics integration
- Refunds/partial refunds workflow
- Email/SMS notifications
- Admin ability to edit other users' passwords
- Mobile app / frontend UI (this is a backend/API-only project initially)
- **Platform-wide admin/superuser role** (someone who can view all vendors' data, all customers, and global stats across the whole platform) — each vendor profile sees only its own data for MVP; a superuser role is a reasonable v1.x addition, not needed to prove out the core model
- Horizontal scaling, caching, queues, containers, cloud deployment (these come in v1.0+ per your roadmap)
- **Crowdsourced/peer-to-peer delivery matching** (a courier delivers a product from seller to buyer along their existing route, for a fee) — a validated real-world concept (see: Roadie, DoorDash's enterprise delivery arm), but deliberately deferred. This is a distinct engineering discipline (geospatial/real-time route-matching, constraint optimization) and a distinct business-viability question (two-sided marketplace liquidity in a given radius) — both would require their own separate Phase 1 discovery process before design, not a bolt-on to Saanthe's MVP.

Keeping these explicitly *out* is as important as defining what's *in* — this is a real skill: scope control.

---

### 7. User Capabilities (Summary) — every account, by default

- Account: create, log in, log out, view/update profile
- Catalog: browse active products (across all vendors)
- Orders: create, view, cancel (conditionally)
- Payments: initiate, view status
- History: view past orders/payments

### 8. Vendor Profile Capabilities (Summary) — unlocked when a user creates one

- Catalog: full CRUD + deactivate (soft delete) — **scoped to products they own**
- Orders: view orders containing their products, update status — **scoped to their own products, not platform-wide**
- Payments: view payments related to their own products
- Dashboard: aggregate stats — **scoped to their own vendor activity**, not platform-wide totals

*Removed from MVP scope: a vendor viewing the full customer list. Since customers and vendors are the same identity pool, "view all customers" would mean viewing platform-wide user data — that's a platform-admin capability, explicitly out of scope (see Section 6).*

---

### 9. Major Business Rules

*(These are the rules that will actually drive your database design and API logic later — write them down now so nothing is ambiguous when you get to LLD.)*

1. A customer **cannot** place an order for a deactivated product.
2. An order can only be **cancelled** while its status is `PENDING` (i.e., before payment succeeds or vendor marks it shipped).
3. A payment can only be initiated for an order that is `PENDING` and has not already been successfully paid.
4. Each order must have **at least one** order item.
5. Order totals are calculated server-side from current product prices — never trusted from the client.
6. A user acting as a vendor can only view or modify data tied to **their own** vendor profile (their own products, orders containing their products, related payments) — never another vendor profile's data.
7. A user can only view/cancel/modify **their own** orders (as a buyer) — never another user's orders — regardless of whether either party also holds a vendor profile.
8. Deactivating a product does not delete historical orders that reference it (data integrity — history must remain accurate).
9. A payment cannot be processed twice for the same order (duplicate-payment prevention).
10. A user is not required to have a vendor profile to buy; creating a vendor profile is optional and additive — it never removes or replaces base buying capabilities.
11. A user is not blocked from placing an order on their own listed product — this is intentionally unrestricted for MVP (self-purchase edge case is a real-world possibility in an open peer marketplace, e.g., testing your own listing's checkout flow); flagged here as a known, accepted behavior rather than silently allowed.

---

### 10. Functional Requirements (High-Level)

| ID | Requirement |
|---|---|
| FR-1 | System shall allow customer registration with unique email + hashed password |
| FR-2 | System shall authenticate users and issue a session/token on login |
| FR-3 | System shall enforce access control based on data ownership and vendor-profile status (does this user have a vendor profile, and do they own the specific product/order in question) on all protected endpoints |
| FR-4 | System shall allow vendors to perform CRUD operations on products |
| FR-5 | System shall allow customers to create orders composed of one or more products |
| FR-6 | System shall calculate order totals server-side |
| FR-7 | System shall simulate a payment process and record the resulting transaction |
| FR-8 | System shall update order status based on payment outcome |
| FR-9 | System shall expose read endpoints for order/payment history, scoped to what the requesting user owns (their own orders as a buyer; their own products' orders/payments if they hold a vendor profile) |
| FR-10 | System shall provide vendor-facing aggregate statistics |

*(Detailed, testable functional requirements — with exact request/response shapes — will be finalized in the API Specification stage, not here. This is intentionally high-level.)*

---

### 11. Non-Functional Requirements (High-Level)

| Category | Requirement |
|---|---|
| **Security** | Passwords must never be stored in plain text; use industry-standard hashing (we'll cover *why* and *how* in the Security Design stage) |
| **Data Integrity** | Financial operations (payment + order status update) must be atomic — either both succeed or both fail, never a partial state |
| **Reliability** | No duplicate payments should ever be recorded for a single order |
| **Maintainability** | Code should be organized into clear layers (routing / business logic / data access) so it's testable and extensible |
| **Testability** | Core business logic (order totals, payment rules, status transitions) must be unit-testable independent of the web framework |
| **Performance** | Not a priority for MVP — correctness first. (We are explicitly *not* optimizing for scale yet.) |
| **Documentation** | Every API endpoint should be self-documenting via FastAPI's automatic docs |

---

### 12. Assumptions

- Single vendor, single currency, no internationalization needed for MVP
- You (the learner) are running this locally, not deploying it publicly, during early versions
- "Authentication" for MVP can be a reasonably simple token scheme — we don't need enterprise-grade SSO
- No real money, real users, or real PII (Personally Identifiable Information) will ever be processed in this system

---

### 13. Constraints

- Tech stack fixed to: Python, FastAPI, PostgreSQL, SQL, REST, pytest, Git (per your instructions)
- No advanced infra (Docker, cloud, queues, caching) until fundamentals (through v0.9) are solid
- Development must follow the SDLC order you specified — no skipping ahead to code
- You are a **beginner**, so every new technical term must be explained in plain language + analogy before being used

---

### 14. MVP Success Criteria

The MVP (through v0.9) is considered successful when:

1. ✅ A customer can register, log in, browse products, place an order, pay (simulated), and see it reflected in their history — entirely through API calls you make yourself (e.g., via a tool like `curl` or a browser-based API tester).
2. ✅ A vendor can log in, manage products, see all orders/payments, and view accurate dashboard statistics.
3. ✅ All business rules in Section 9 are enforced and covered by automated tests (pytest).
4. ✅ You can explain — out loud, without notes — how a single request travels from client → API → business logic → database → response, and why each layer exists.
5. ✅ No duplicate or inconsistent financial records exist under normal or adversarial testing (e.g., double-clicking "pay").

---

## What's Next

Per the SDLC order, the next artifact is:

**→ User Flows & Use Cases** — where we'll walk through each major action (register, place an order, pay, cancel, etc.) as step-by-step flows, including what happens when things go *wrong* (e.g., insufficient stock, invalid card, expired session). This is what will directly feed into your Functional Requirements getting more specific, and eventually your API contract.

I have **not** started any code yet, as instructed. Let me know if you want to adjust anything in this charter (e.g., scope, business rules) before we move to User Flows — it's much cheaper to change scope now than after we've built something.
