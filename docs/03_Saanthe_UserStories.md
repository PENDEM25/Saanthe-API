# User Stories
## Saanthe-API — Phase 2 (PRD component)

Each story follows the standard industry format: **As a [user], I want to [action], so that [benefit].** Each includes brief **acceptance criteria** — the specific, checkable conditions that define "done." This is the level of detail that feeds directly into the Technical Design Doc next.

*Note: since Saanthe uses a single-identity model (Section 4 of the Charter), stories are grouped by capability, not by "customer" vs. "vendor" as separate user types. Any user can perform "base" stories; "vendor profile" stories require that user to have created one.*

---

## A. Account & Identity

**US-1:** As a user, I want to register with my name, email, and password, so that I can access the platform.
- *Acceptance:* Duplicate emails rejected (409); weak passwords rejected (422); password never stored or returned in plain text.

**US-2:** As a user, I want to log in with my email and password, so that I can access my account and perform actions.
- *Acceptance:* Valid credentials return an access token; invalid credentials return a generic 401 (doesn't reveal whether the email or password was wrong).

**US-3:** As a user, I want to view and update my profile, so that my account information stays accurate.
- *Acceptance:* Can't change email to one already in use (409); can't self-assign vendor/admin privileges through this endpoint.

**US-4:** As a user, I want to log out, so that my session/token is no longer usable on a shared or public device.
- *Acceptance:* Token is invalidated (or, if using a stateless token approach, this is documented clearly to the user as a known trade-off — to be resolved in Security Design).

---

## B. Browsing & Buying (base capability — no vendor profile required)

**US-5:** As a user, I want to browse all active products from any seller, so that I can find something I want to buy.
- *Acceptance:* Deactivated products never appear; results include the seller's product info (not the seller's private account info).

**US-6:** As a user, I want to place an order containing one or more products, so that I can purchase items I've found.
- *Acceptance:* Order rejected if any product is inactive or doesn't exist (400); total is calculated server-side from current prices, never trusted from the client; order requires at least one item.

**US-7:** As a user, I want to cancel an order I placed, so that I'm not charged for something I no longer want.
- *Acceptance:* Only allowed while order status is `PENDING`; rejected (409) if already paid/shipped; rejected (403) if it's not the requesting user's own order.

**US-8:** As a user, I want to pay for an order, so that I can complete my purchase.
- *Acceptance:* Only allowed on `PENDING` orders with no prior successful payment (duplicate-payment prevention); on success, order status becomes `PAID`; on failure, order remains `PENDING` and the user can retry.

**US-9:** As a user, I want to view my own order and payment history, so that I can track what I've bought and its status.
- *Acceptance:* Only the requesting user's own records are returned — never another user's.

---

## C. Selling (unlocked via Vendor Profile)

**US-10:** As a user, I want to create a vendor profile, so that I can start selling products without needing a separate account.
- *Acceptance:* Any existing user can create exactly one vendor profile linked to their account; creating one does not remove or alter their existing buying capabilities.

**US-11:** As a vendor-profile holder, I want to create, update, and deactivate my own products, so that I can manage what I'm selling.
- *Acceptance:* A user can only modify products tied to their own vendor profile (403 otherwise); deactivating is a soft delete — historical orders referencing the product remain intact and accurate.

**US-12:** As a vendor-profile holder, I want to view orders and payments that involve my own products, so that I can track my sales.
- *Acceptance:* Only orders/payments tied to the vendor's own products are returned — never another vendor's sales data, and never another user's unrelated purchases.

**US-13:** As a vendor-profile holder, I want to update the status of orders containing my products (e.g., mark as shipped), so that buyers know the state of their purchase.
- *Acceptance:* Only valid status transitions allowed (per the state machine in the User Flows doc — e.g., `PAID → SHIPPED`); invalid transitions rejected (409); only allowed on orders containing the vendor's own products.

**US-14:** As a vendor-profile holder, I want to view a dashboard of my own sales activity (orders received, successful/failed payments, total revenue), so that I can understand how my selling is going.
- *Acceptance:* All figures are scoped to this vendor profile only — never platform-wide totals (platform-wide admin view is explicitly out of scope, per the Charter).

---

## D. Cross-Cutting / Edge Cases (worth naming explicitly, not just implying)

**US-15:** As a user who is also a vendor-profile holder, I want to be able to buy products (including, if I choose, my own listed product), so that my buying capability is never restricted by also being a seller.
- *Acceptance:* Self-purchase is allowed, not blocked (per Business Rule #11 in the Charter) — this is a deliberate, documented decision, not an oversight.

**US-16:** As a user, I want confidence that no one else can view or modify my private data (profile, orders, payments) regardless of whether they hold a vendor profile, so that my information stays secure.
- *Acceptance:* Every protected endpoint enforces ownership checks; attempts to access another user's private data return 403/404, never leak data through error messages.

---

## What's Next

With Goals, Scope, and Success Metrics (already in the Charter) and User Stories (above) complete, **Phase 2 is done.**

Next: **Technical Design Doc** (HLD + ERD + API Contract + Security combined, per the condensed plan). This is where each story above gets translated into exact database tables, API endpoints, and request/response shapes.
