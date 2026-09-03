# Saanthe-API
Marketplace/transaction backend built from scratch with FastAPI — full SDLC process documented.

A backend e-commerce/marketplace system built from scratch — documented and engineered following a real Software Development Life Cycle (SDLC), not a copy-paste tutorial.

The name comes from **"santha" (సంత)** — a traditional Telugu/Kannada village market, where the same person can show up to sell their goods and also walk around buying from others. Saanthe is built around that same idea: **any user can browse and buy, and any user can optionally create a Vendor Profile to sell** — no separate "customer" and "seller" account types.

This project exists as a hands-on learning build — going through the full engineering process (problem definition, requirements, design, implementation, testing) end-to-end, the way a real engineering team would, in order to build genuine, defensible backend engineering skill.

---

## Tech Stack

- **Language:** Python 3.13
- **Framework:** FastAPI
- **Server:** Uvicorn
- **Database:** PostgreSQL (planned — not yet implemented)
- **Testing:** pytest (planned)
- **Version Control:** Git / GitHub

---

## Project Documentation

Every major engineering decision in this project is documented before being implemented. Full docs live in [`/docs`](./docs):

| Document | What it covers |
|---|---|
| `00_problem_statement_opportunity_brief.md` | Why this project exists, and the decision to pursue it |
| `roles_and_responsibilities.md` | How project roles (Stakeholder, PM, Engineering) are structured |
| `01_project_charter.md` | Project vision, MVP scope, business rules, requirements |
| `02_user_flows_and_use_cases.md` | Step-by-step flows for every major user action, including error handling |
| `03_user_stories.md` | Formal user stories with acceptance criteria |
| `04_technical_design_doc.md` | High-Level Design, Database ERD, API Contract, and Security Design |

---

## Architecture

Saanthe follows a layered backend architecture:

```
Client → Router → Service → Repository → Database
```

- **Router** — receives HTTP requests, validates their shape, forwards to the Service layer
- **Service** — contains business logic and rules (e.g., "can this order be cancelled?")
- **Repository** — the only layer that talks directly to the database
- **Database** — PostgreSQL, stores all persistent data

Full reasoning behind this structure is in `docs/04_technical_design_doc.md`.

---

## Project Status

🚧 **Actively in development — pre-implementation / early setup stage.**

- [x] Problem Statement & Charter
- [x] User Flows & User Stories
- [x] Technical Design Doc (HLD, ERD, API Contract, Security)
- [x] Local Python environment set up (virtual environment, FastAPI, Uvicorn installed)
- [x] Base folder structure created
- [ ] Database models implemented
- [ ] First working API endpoint
- [ ] Authentication
- [ ] Core order/payment flow
- [ ] Automated tests

---

## Running This Project Locally

*(Setup below reflects current progress — this section will be updated as implementation continues.)*

**1. Clone the repository**
```bash
git clone https://github.com/PENDEM25/Saanthe-API.git
cd Saanthe-API
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```
*(Note: `requirements.txt` will be added once core dependencies are finalized.)*

**4. Run the development server**
```bash
uvicorn app.main:app --reload
```
*(Note: this will work once `app/main.py` exists — coming soon.)*

---

## License

MIT — see [LICENSE](./LICENSE).

## A Note on This Project

This is a solo learning project, built with Claude acting as a Product Management / Technical Advisory partner throughout the design process. Every architectural decision — and the reasoning behind it — is intentionally documented in `/docs`, both as a personal reference and as a resource for anyone else learning backend engineering from scratch.
