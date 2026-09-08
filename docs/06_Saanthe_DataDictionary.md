# Data Dictionary
## Saanthe-API — Database Design Reference

Exact column types, sizes, and constraints for every table, derived from the ERD. This sits alongside `04_technical_design_doc.md` as the precise reference used to write the actual SQL schema and Python models.

---

## `users`

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `name` | VARCHAR(100) | NOT NULL |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE |
| `password_hash` | VARCHAR(255) | NOT NULL |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT = now() |

## `vendor_profiles`

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `user_id` | INTEGER | FOREIGN KEY → users.id, UNIQUE, NOT NULL |
| `business_name` | VARCHAR(100) | NULL allowed |
| `created_at` | TIMESTAMP | DEFAULT = now() |

*UNIQUE on `user_id` enforces one vendor profile per user (single-identity model, Option B).*

## `products`

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `vendor_profile_id` | INTEGER | FOREIGN KEY → vendor_profiles.id, NOT NULL |
| `name` | VARCHAR(150) | NOT NULL |
| `description` | TEXT | NULL allowed |
| `price` | DECIMAL(10,2) | NOT NULL, CHECK (price > 0) |
| `stock_quantity` | INTEGER | NOT NULL, DEFAULT = 0, CHECK (stock_quantity >= 0) |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT = true |
| `created_at` | TIMESTAMP | DEFAULT = now() |

## `orders`

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `buyer_user_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT = 'PENDING' |
| `total_amount` | DECIMAL(10,2) | NOT NULL, CHECK (total_amount >= 0) |
| `created_at` | TIMESTAMP | DEFAULT = now() |

## `order_items`

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `order_id` | INTEGER | FOREIGN KEY → orders.id, NOT NULL |
| `product_id` | INTEGER | FOREIGN KEY → products.id, NOT NULL |
| `quantity` | INTEGER | NOT NULL, CHECK (quantity > 0) |
| `unit_price_at_purchase` | DECIMAL(10,2) | NOT NULL, CHECK (unit_price_at_purchase >= 0) |

*Neither `order_id` nor `product_id` is UNIQUE — both are expected to repeat across rows (one order, many products; one product, many orders).*

## `payments`

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `order_id` | INTEGER | FOREIGN KEY → orders.id, NOT NULL |
| `status` | VARCHAR(20) | NOT NULL |
| `amount` | DECIMAL(10,2) | NOT NULL, CHECK (amount >= 0) |
| `created_at` | TIMESTAMP | DEFAULT = now() |

*`order_id` is deliberately not UNIQUE — allows multiple payment attempts (e.g., one FAILED, one SUCCESS retry) per order.*

---

## Key Design Principles Applied Throughout

- **Money is always `DECIMAL(10,2)`**, never INTEGER or floating-point — avoids rounding errors in financial data.
- **Status-like fields with more than 2 possible states (now or foreseeably) use `VARCHAR`, not `BOOLEAN`** — `orders.status` and `payments.status` can each grow to more states; `products.is_active` genuinely never needs a third state, so it stays `BOOLEAN`.
- **UNIQUE constraints only where repetition would be a real error** — enforced on `users.email` and `vendor_profiles.user_id`; deliberately absent from every Foreign Key that's expected to repeat (`order_items.order_id`, `order_items.product_id`, `payments.order_id`, `products.vendor_profile_id`, `orders.buyer_user_id`).
- **CHECK constraints enforce business-rule-level validity** at the database layer itself (e.g., `quantity > 0`, `price > 0`) — a last line of defense even if application code has a bug.
